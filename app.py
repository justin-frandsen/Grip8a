from flask import Flask, render_template

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html', template_folder='templates')

@app.route('/hello/<name>')
def hello(name):
    return render_template('page.html', name=name)

@app.route('/stats')
def cakes():
    return 'Lets gooooooo!'

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=8000)