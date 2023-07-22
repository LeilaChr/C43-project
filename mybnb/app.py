from flask import Flask, render_template, redirect, url_for, request
from flask_bootstrap import Bootstrap5
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import DataRequired, Length

from .user import user

app = Flask(__name__)
app.config['SECRET_KEY'] = 'hello'
bootstrap = Bootstrap5(app)


def form_endpoint(form, template_path: str, on_submit: callable, next_location: str = None, template_args: dict = {}):
    if not isinstance(form, FlaskForm):
        # Instantiate form class
        form = form()

    if form.validate_on_submit():
        on_submit(form)
        if next_location:
            return redirect(next_location)

    return render_template(template_path, form=form, **template_args)


@app.route('/')
def home():
    return render_template('index.html')

@app.route('/sign-up', methods=['GET', 'POST'])
def sign_up():
    class Form(FlaskForm):
        name = StringField('Name',  validators=[DataRequired(), Length(1, 63)])
        username = StringField('Choose a Username', validators=[DataRequired(), Length(1, 63)])
        password = PasswordField('Choose a Password', validators=[DataRequired(), Length(1, 63)])
        submit = SubmitField('Sign Up')

    def on_submit(form):
        # TODO: Write to database here
        pass

    return form_endpoint(Form, 'sign-up.html',
                         next_location='/dashboard',
                         on_submit=on_submit)

@app.route('/log-in', methods=['GET', 'POST'])
def log_in():
    class Form(FlaskForm):
        username = StringField('Username', validators=[DataRequired(), Length(1, 63)])
        password = PasswordField('Password', validators=[DataRequired(), Length(1, 63)])
        submit = SubmitField('Log In')

    def on_submit(form):
        # TODO: Query database here
        global user
        user = {
            'id': 1,
            'username': form.username.data,
            'name': 'Demo User'
        }

    return form_endpoint(Form, 'log-in.html', on_submit,
                         next_location='/dashboard',
                         on_submit=on_submit)

@app.route('/dashboard')
def dashboard():
    global user
    return render_template('dashboard.html', user=user)

@app.route('/my-profile', methods=['GET', 'POST'])
def my_profile():
    class Form(FlaskForm):
        id = StringField('User ID', render_kw={'readonly': True})
        name = StringField('Name',  validators=[DataRequired(), Length(1, 63)])
        username = StringField('Username', validators=[DataRequired(), Length(1, 63)])
        password = PasswordField('Password', validators=[Length(0, 63)])
        submit = SubmitField('Save Changes')

    def on_submit(form):
        # TODO: Write to database here
        global user
        user = {
            'id': 1,
            'username': form.username.data,
            'name': form.name.data
        }


    form = Form()
    global user
    form.id.data = user['id']
    form.name.data = user['name']
    form.username.data = user['username']

    return form_endpoint(form, 'my-profile.html',
                         on_submit=on_submit)


if __name__ == '__main__':
    app.run()
