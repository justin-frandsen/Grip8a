from flask import Flask, render_template
import flask
print(flask.__version__)

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html', template_folder='templates')

@app.route('/stats')
def cakes():
    return 'Lets gooooooo!'

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=8000)