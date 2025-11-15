from flask import Flask, render_template, jsonify, request
from markupsafe import escape
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import func

import threading
import asyncio
from bleak import BleakClient, BleakScanner

import time
from datetime import datetime, timezone
import os

# Initialize Flask app
app = Flask(__name__)

# Database configuration - use SQLite file in project by default
base_dir = os.path.abspath(os.path.dirname(__file__))
app.config["SQLALCHEMY_DATABASE_URI"] = (
    f"sqlite:///{os.path.join(base_dir, 'grip8a.db')}"
)
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db = SQLAlchemy(app)

# BLE Device Configuration
DEVICE_NAME = "Arduino"
CHARACTERISTIC_UUID = "5387e989-6064-48e4-9387-688c754efcfa"

# Shared state for the latest force reading
force = 0.0


# ---------------------------
# Notification handler
# ---------------------------
def notification_handler(sender, data):
    """Callback for handling incoming BLE notifications.

    This is called from the Bleak client's event loop thread. It updates the
    module-level `force` variable so the Flask `/data` endpoint can return it.
    """
    global force
    try:
        # Prefer interpreting raw bytes as an unsigned little-endian integer
        force = int.from_bytes(data, byteorder="little", signed=False)
    except Exception:
        try:
            # Fallback: try decoding as a UTF-8 numeric string
            s = data.decode().strip()
            force = float(s)
        except Exception:
            # Could not parse incoming data; keep previous value
            print("Warning: could not parse BLE notification:", data)


# ---------------------------
# BLE manager that runs an asyncio loop in a background thread
# ---------------------------
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


# Single manager instance
ble_manager = BLEManager()


# ---------------------------
# Models
# ---------------------------
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), unique=True, nullable=False)
    # optional demographics
    age = db.Column(db.Integer, nullable=True)
    gender = db.Column(db.String(20), nullable=True)
    weight = db.Column(db.Float, nullable=True)
    notes = db.Column(db.Text, nullable=True)

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "age": self.age,
            "gender": self.gender,
            "weight": self.weight,
            "notes": self.notes,
        }


class Reading(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=True)
    timestamp_ms = db.Column(db.BigInteger, nullable=False)
    timestamp_iso = db.Column(db.String(50), nullable=False)
    force = db.Column(db.Float, nullable=False)

    def to_dict(self):
        return {
            "id": self.id,
            "user_id": self.user_id,
            "timestamp_ms": self.timestamp_ms,
            "timestamp_iso": self.timestamp_iso,
            "force": self.force,
        }


with app.app_context():
    # Create tables if they don't exist
    db.create_all()


# ---------------------------
# Routes
# ---------------------------
@app.route("/")
def index():
    return render_template("index.html")


@app.route("/graph")
def graph():
    return render_template("graph.html")

@app.route("/stats")
def stats():
    return render_template("stats.html")


@app.route("/stats/user/<username>")
def stats_for_user(username):
    # Render the same template but provide the selected username so the page can pre-select
    # Try to resolve the user by name (case-insensitive) and compute total force
    try:
        user = User.query.filter(func.lower(User.name) == username.lower()).first()
    except Exception:
        user = None

    if user is None:
        total_force = None
    else:
        row = db.session.query(
        func.count(Reading.id).label('count'),
        func.avg(Reading.force).label('avg_force'),
        func.sum(Reading.force).label('total_force'),
        func.min(Reading.force).label('min_force'),
        func.max(Reading.force).label('max_force'),
    ).filter(Reading.user_id == user.id).first()

    stats = {
        "count": int(row.count or 0),
        "total_force": float(row.total_force) if row.total_force is not None else 0.0,
        "avg_force": float(row.avg_force) if row.avg_force is not None else 0.0,
        "min_force": float(row.min_force) if row.min_force is not None else 0.0,
        "max_force": float(row.max_force) if row.max_force is not None else 0.0,
    }

    return render_template("stats.html", selected_user=username, stats=stats)

@app.route("/create_user")
def create_user():
    return render_template("create_user.html")

@app.route("/connect")
def connect():
    """Synchronous HTTP endpoint that starts the BLE background task."""
    try:
        ble_manager.start()
        return jsonify({"status": "connecting"}), 202
    except Exception as e:
        print("Error starting BLE manager:", e)
        return jsonify({"error": str(e)}), 500


@app.route("/disconnect")
def disconnect():
    """Synchronous HTTP endpoint to stop the BLE background task and disconnect."""
    try:
        ble_manager.stop()
        return jsonify({"status": "disconnected"}), 200
    except Exception as e:
        print("Error stopping BLE manager:", e)
        return jsonify({"error": str(e)}), 500


@app.route("/connect_status")
def connect_status():
    return jsonify(
        {
            "running": ble_manager.is_running(),
            "connected": ble_manager.is_connected(),
        }
    )


@app.route("/data")
def data():
    """Return the latest force reading and timestamps."""
    ts = time.time()
    ts_ms = int(ts * 1000)
    ts_iso = datetime.fromtimestamp(ts, tz=timezone.utc).isoformat()
    return jsonify(
        {
            "time": ts,
            "time_ms": ts_ms,
            "time_iso": ts_iso,
            "force": force,
        }
    )


# API: create a user
@app.route("/api/users", methods=["GET", "POST"])
def users():
    if request.method == "POST":
        payload = request.get_json() or {}
        name = payload.get("name")
        if not name:
            return jsonify({"error": "name required"}), 400
        name = escape(name).strip()

        # optional demographics
        try:
            age = int(payload.get("age", None)) if payload.get("age") is not None else None
        except Exception:
            return jsonify({"error": "invalid age"}), 400
        gender = payload.get("gender")
        try:
            weight = float(payload.get("weight")) if payload.get("weight") not in (None, "") else None
        except Exception:
            return jsonify({"error": "invalid weight"}), 400
        notes = payload.get("notes")

        existing = User.query.filter_by(name=name).first()
        if existing:
            return jsonify(existing.to_dict()), 200
        user = User(name=name, age=age, gender=gender, weight=weight, notes=notes)
        db.session.add(user)
        db.session.commit()
        return jsonify(user.to_dict()), 201

    all_users = User.query.all()
    return jsonify([u.to_dict() for u in all_users])


# API: post a reading
@app.route("/api/readings", methods=["POST", "GET"])
def api_readings():
    if request.method == "POST":
        payload = request.get_json() or {}
        user_id = payload.get("user_id")
        rforce = payload.get("force")
        timestamp_ms = payload.get("timestamp_ms")
        timestamp_iso = payload.get("timestamp_iso")

        if rforce is None:
            return jsonify({"error": "force required"}), 400

        if timestamp_ms is None:
            ts = time.time()
            timestamp_ms = int(ts * 1000)
            timestamp_iso = datetime.fromtimestamp(ts, tz=timezone.utc).isoformat()

        reading = Reading(
            user_id=user_id,
            timestamp_ms=timestamp_ms,
            timestamp_iso=timestamp_iso,
            force=float(rforce),
        )
        db.session.add(reading)
        db.session.commit()
        return jsonify(reading.to_dict()), 201

    recent = Reading.query.order_by(Reading.timestamp_ms.desc()).limit(100).all()
    return jsonify([r.to_dict() for r in recent])


# Run the app
if __name__ == "__main__":
    # Important note for development: avoid Flask auto-reloader while developing BLE code,
    # because the reloader spawns two processes which can result in duplicate BLE tasks/threads.
    # Use something like `python Grip8a/app.py` (default) and don't rely on flask's reloader.
    app.run(debug=True, host="0.0.0.0", port=8000)
