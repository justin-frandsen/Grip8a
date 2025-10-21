from flask import Flask, render_template, jsonify
import random
import time

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

#example dynamic route
@app.route('/hello/<name>')
def hello(name):
    return render_template('page.html', name=name)

@app.route('/graph')
def graph():
    return render_template('graph.html')

@app.route('/stats')
def stats():
    return "Statistics Page"

@app.route('/data')
def data():
    # Fake time-series data
    return jsonify({
        'time': time.time(),
        'force': random.uniform(20, 80)
    })

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=8000)