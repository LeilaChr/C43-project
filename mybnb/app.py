from flask import Flask, render_template
import os


app = Flask(__name__)

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/sign-up')
def sign_up():
    return render_template('sign-up.html')

@app.route('/log-in')
def log_in():
    return render_template('log-in.html')


if __name__ == '__main__':
    app.run()
