import sqlite3
import time
from datetime import datetime
from threading import Thread
from queue import Queue, Empty
from grip8a.db.config import DB_FORCE

DB = DB_FORCE
write_queue = Queue()
_writer_thread = None
_writer_running = False


def init_force_db():
    """Create the DB table (safe to call every run)."""
    conn = sqlite3.connect(DB)
    c = conn.cursor()
    c.execute("""
        CREATE TABLE IF NOT EXISTS readings (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            date TEXT,
            user TEXT,
            current_weight REAL,
            weight_percent REAL,
            timestamp_ms INTEGER,
            timestamp_iso TEXT,
            force REAL
        )
    """)
    conn.commit()
    conn.close()


def _writer_loop():
    """Runs in background. Pulls force readings off the queue and writes them."""
    global _writer_running
    _writer_running = True

    conn = sqlite3.connect(DB)
    c = conn.cursor()

    while _writer_running:
        try:
            force_value = write_queue.get(timeout=0.2)
        except Empty:
            continue  # loop again; allows thread to exit cleanly

        ts = time.time()
        ts_ms = int(ts * 1000)
        ts_iso = datetime.utcfromtimestamp(ts).isoformat()

        c.execute("""
            INSERT INTO readings (date, user, current_weight, timestamp_ms, timestamp_iso, force)
            VALUES (?, ?, ?)
        """, (ts_ms, ts_iso, force_value))
        conn.commit()

    conn.close()


def start_force_writer():
    """Start background write thread (idempotent)."""
    global _writer_thread, _writer_running
    if _writer_thread is not None and _writer_thread.is_alive():
        return

    _writer_running = True
    _writer_thread = Thread(target=_writer_loop, daemon=True)
    _writer_thread.start()


def stop_force_writer():
    """Stop background writer thread gracefully."""
    global _writer_running
    _writer_running = False


def queue_force_reading(force_value):
    """
    Called by BLE loop. Extremely fast — just pushes a number into the queue.
    """
    write_queue.put(force_value)
