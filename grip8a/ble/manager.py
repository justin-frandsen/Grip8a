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
        self.stop_event = None
        self.client = None

    # identical to your original code…
