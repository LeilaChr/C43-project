from flask import Flask, render_template
from flask_bootstrap import Bootstrap5
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import DataRequired, Length

app = Flask(__name__)
app.config['SECRET_KEY'] = 'hello'

bootstrap = Bootstrap5(app)

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/sign-up')
def sign_up():
    class SignUpForm(FlaskForm):
        name = StringField('Name', validators=[DataRequired(), Length(0, 63)])
        submit = SubmitField('Sign Up')

    return render_template('sign-up.html', form=SignUpForm())

@app.route('/log-in')
def log_in():
    class LogInForm(FlaskForm):
        name = StringField('Username', validators=[DataRequired(), Length(0, 63)])
        password = PasswordField('Password', validators=[DataRequired(), Length(0, 63)])
        submit = SubmitField('Log In')

    return render_template('log-in.html', form=LogInForm())


if __name__ == '__main__':
    app.run()
