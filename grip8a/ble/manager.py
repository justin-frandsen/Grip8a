import asyncio, threading
from bleak import BleakClient, BleakScanner
from .config import DEVICE_NAME, CHARACTERISTIC_UUID

force = 0.0   # shared global reading

def notification_handler(sender, data):
    global force
    try:
        force = int.from_bytes(data, byteorder="little", signed=False)
    except:
        try:
            force = float(data.decode().strip())
        except:
            pass

class BLEManager:
    def __init__(self):
        self.loop = None
        self.thread = None
        self.stop_event = None  # asyncio.Event created inside the loop
        self.task_future = (
            None  # concurrent.futures.Future for the coroutine running the BLE task
        )
        self.client = None
        self._lock = threading.Lock()

    def _start_loop_thread(self):
        """Create and start the asyncio event loop in a background thread."""
        self.loop = asyncio.new_event_loop()

        def _run_loop():
            asyncio.set_event_loop(self.loop)
            self.loop.run_forever()

        self.thread = threading.Thread(target=_run_loop, daemon=True)
        self.thread.start()

        # Create the asyncio.Event inside the loop and store it
        fut = asyncio.run_coroutine_threadsafe(self._create_event(), self.loop)
        self.stop_event = fut.result()

    async def _create_event(self):
        return asyncio.Event()

    def start(self):
        """Start the background BLE task (non-blocking)."""
        with self._lock:
            if self.task_future and not self.task_future.done():
                # already running
                return
            if self.loop is None:
                self._start_loop_thread()
            # Schedule the BLE coroutine on the background loop
            self.task_future = asyncio.run_coroutine_threadsafe(
                self._ble_task(self.stop_event), self.loop
            )

    def is_running(self):
        with self._lock:
            return bool(self.task_future and not self.task_future.done())

    def is_connected(self):
        # very lightweight check: see if client reference exists and is connected
        with self._lock:
            client = self.client
        if client is None:
            return False
        try:
            # BleakClient.has a `.is_connected` coroutine/property depending on version.
            # Use a synchronous check by scheduling it on the loop if available.
            coro = getattr(client, "is_connected", None)
            if coro is None:
                return False
            if asyncio.iscoroutinefunction(coro):
                # schedule and get result
                fut = asyncio.run_coroutine_threadsafe(coro(), self.loop)
                return fut.result(timeout=2)
            elif isinstance(coro, bool):
                return bool(coro)
            else:
                # property-like
                return bool(coro)
        except Exception:
            return False

    def stop(self, timeout=10):
        """Request the BLE task to stop and tear down the background loop."""
        with self._lock:
            if not self.loop or not self.stop_event:
                return
            # signal the task to stop
            try:
                asyncio.run_coroutine_threadsafe(
                    self.stop_event.set(), self.loop
                ).result(timeout=2)
            except Exception as e:
                print("Error signaling BLE stop_event:", e)

            # wait for the task to exit
            if self.task_future:
                try:
                    self.task_future.result(timeout=timeout)
                except Exception as e:
                    print("BLE task did not finish cleanly:", e)

            # stop the loop
            try:
                self.loop.call_soon_threadsafe(self.loop.stop)
            except Exception as e:
                print("Error stopping BLE loop:", e)

            # join the thread briefly
            if self.thread:
                self.thread.join(timeout=1)

            # clear state
            self.loop = None
            self.thread = None
            self.stop_event = None
            self.task_future = None
            self.client = None

    async def _ble_task(self, stop_event: asyncio.Event):
        """Coroutine that scans, connects, subscribes to notifications and keeps running.

        Runs inside the background asyncio loop.
        """
        self.client = None
        try:
            while not stop_event.is_set():
                try:
                    print("BLE: scanning for devices...")
                    devices = await BleakScanner.discover()
                    target = None
                    for d in devices:
                        if d.name == DEVICE_NAME:
                            target = d
                            break

                    if not target:
                        print("BLE: device not found, retrying in 5s...")
                        await asyncio.sleep(5)
                        continue

                    client = BleakClient(target.address)
                    self.client = client
                    # Use context manager to ensure clean disconnects on exit
                    async with client:
                        print(f"BLE: Connected to {DEVICE_NAME} ({target.address})")
                        try:
                            await client.start_notify(
                                CHARACTERISTIC_UUID, notification_handler
                            )
                        except Exception as e:
                            print("BLE: Failed to start notify:", e)
                            # let context manager exit and retry
                            await asyncio.sleep(5)
                            continue

                        # Wait until stop_event is set (i.e. until a stop is requested)
                        await stop_event.wait()

                        # When stopping, try to stop notifications cleanly
                        try:
                            await client.stop_notify(CHARACTERISTIC_UUID)
                        except Exception:
                            pass

                    # If we get here and stop_event was set, break out
                    if stop_event.is_set():
                        break

                    # Otherwise, connection dropped unexpectedly - retry after a pause
                    print("BLE: Disconnected unexpectedly, retrying in 5s...")
                    await asyncio.sleep(5)

                except Exception as e:
                    print("BLE task iteration error:", e)
                    await asyncio.sleep(5)
        finally:
            # ensure we clear client reference
            self.client = None
            print("BLE: task exiting")
