from flask import Flask, render_template, jsonify, request
from markupsafe import escape
from flask_sqlalchemy import SQLAlchemy
import random
import time
from datetime import datetime, timezone
import os

# Initialize Flask app
app = Flask(__name__)

# Database configuration - use SQLite file in project by default
base_dir = os.path.abspath(os.path.dirname(__file__))
app.config['SQLALCHEMY_DATABASE_URI'] = f"sqlite:///{os.path.join(base_dir, 'grip8a.db')}"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)


# Models
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), unique=True, nullable=False)

    def to_dict(self):
        return {'id': self.id, 'name': self.name}


class Reading(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)
    timestamp_ms = db.Column(db.BigInteger, nullable=False)
    timestamp_iso = db.Column(db.String(50), nullable=False)
    force = db.Column(db.Float, nullable=False)

    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'timestamp_ms': self.timestamp_ms,
            'timestamp_iso': self.timestamp_iso,
            'force': self.force
        }


with app.app_context():
    # Create tables if they don't exist
    db.create_all()

# Home route
@app.route('/')
def index():
    return render_template('index.html')

#example dynamic route
@app.route('/hello/<name>')
def hello(name):
    # ensure the incoming name is escaped to avoid template injection
    safe_name = escape(name)
    return render_template('page.html', name=safe_name)

# renders dynamic graph page
@app.route('/graph')
def graph():
    # default graph with no pre-selected user
    return render_template('graph.html', selected_user=None)

# dynamic graph page for specific user
@app.route('/graph/<username>')
def graph_for_user(username):
    # pass the selected username to the template so it can pre-select
    return render_template('graph.html', selected_user=username)

# Will later be used to show statistics (probably not updated quite as often as /data)
@app.route('/stats')
def stats():
    return "Statistics Page"

#real time readings of force sensor (currently faked with random data)
@app.route('/data')
def data():
    # Fake time-series data
    ts = time.time()
    ts_ms = int(ts * 1000)
    ts_iso = datetime.fromtimestamp(ts, tz=timezone.utc).isoformat()
    return jsonify({
        'time': ts,              # seconds since epoch (float)
        'time_ms': ts_ms,        # milliseconds since epoch (int)
        'time_iso': ts_iso,      # ISO 8601 string in UTC
        'force': random.uniform(20, 80) # random force value use the real sensor data here
    })

# API: create a user
@app.route('/api/users', methods=['GET', 'POST'])
def users():
    if request.method == 'POST':
        payload = request.get_json() or {}
        name = payload.get('name')
        if not name:
            return jsonify({'error': 'name required'}), 400
        name = escape(name)
        existing = User.query.filter_by(name=name).first()
        if existing:
            return jsonify(existing.to_dict()), 200
        user = User(name=name)
        db.session.add(user)
        db.session.commit()
        return jsonify(user.to_dict()), 201

    # GET - list users
    all_users = User.query.all()
    return jsonify([u.to_dict() for u in all_users])

# API: post a reading
@app.route('/api/readings', methods=['POST', 'GET'])
def api_readings():
    if request.method == 'POST':
        payload = request.get_json() or {}
        user_id = payload.get('user_id')
        force = payload.get('force')
        timestamp_ms = payload.get('timestamp_ms')
        timestamp_iso = payload.get('timestamp_iso')

        if force is None:
            return jsonify({'error': 'force required'}), 400

        # fill timestamps if not provided (might get rid of this still considering how to handle missing timestamps and data)
        if timestamp_ms is None:
            ts = time.time()
            timestamp_ms = int(ts * 1000)
            timestamp_iso = datetime.fromtimestamp(ts, tz=timezone.utc).isoformat()

        reading = Reading(user_id=user_id, timestamp_ms=timestamp_ms, timestamp_iso=timestamp_iso, force=float(force))
        db.session.add(reading)
        db.session.commit()
        return jsonify(reading.to_dict()), 201

    # GET - return recent readings (limit 100)
    recent = Reading.query.order_by(Reading.timestamp_ms.desc()).limit(100).all()
    return jsonify([r.to_dict() for r in recent])

# Run the app
if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=8000)