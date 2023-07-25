from flask import Flask, render_template, redirect, url_for, request, session, flash
from flask_bootstrap import Bootstrap5
from flask_session import Session
from flask_wtf import FlaskForm
from mysql.connector import IntegrityError, DataError
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import DataRequired, Length, Regexp, ValidationError

from . import tables, sanitize

app = Flask(__name__)
app.secret_key = 'B5F61F92-EADD-4952-A165-A39568B83603'

app.config['SESSION_TYPE'] = 'filesystem'
Session(app)

Bootstrap5(app)


def form_endpoint(form, template_path: str, on_submit: callable, next_location: str = None, template_args: dict = {}):
    if not isinstance(form, FlaskForm):
        # Instantiate form class
        form = form()

    if form.validate_on_submit():
        try:
            on_submit(form)
            if next_location:
                return redirect(next_location)

        except ValidationError as e:
            flash(str(e), 'danger')
        except (IntegrityError, DataError) as e:
            flash(e.msg, 'danger')

    return render_template(template_path, form=form, **template_args)


@app.route('/')
def home():
    return render_template('index.html')

@app.route('/sign-up', methods=['GET', 'POST'])
def sign_up():
    class Form(FlaskForm):
        sin = StringField('SIN', validators=[DataRequired(), Regexp(sanitize.sin_pattern, 0, 'Must have the form xxx-xxx-xxx.')])

        name = StringField('Name', validators=[DataRequired(), Length(1, 63)])
        dob = StringField('Date of Birth', validators=[DataRequired(), Length(1, 15)])
        address = StringField('Address', validators=[Length(0, 127)])
        occupation = StringField('Occupation', validators=[Length(0, 31)])

        username = StringField('Choose a Username', validators=[DataRequired(), Length(1, 63)])
        password = PasswordField('Choose a Password', validators=[Length(0, 63)])

        submit = SubmitField('Sign Up')

    def on_submit(form):
        tables.users.sign_up(
            sin=sanitize.sin(form.sin.data),

            name=form.name.data,
            dob=form.dob.data,
            address=form.address.data,
            occupation=form.occupation.data,

            username=form.username.data
        )

    return form_endpoint(Form, 'sign-up.html',
                         next_location='/dashboard',
                         on_submit=on_submit)

@app.route('/log-in', methods=['GET', 'POST'])
def log_in():
    class Form(FlaskForm):
        username = StringField('Username', validators=[DataRequired(), Length(1, 63)])
        password = PasswordField('Password', validators=[Length(0, 63)])
        submit = SubmitField('Log In')

    def on_submit(form):
        tables.users.log_in(username=form.username.data)

    return form_endpoint(Form, 'log-in.html',
                         next_location='/dashboard',
                         on_submit=on_submit)

@app.route('/dashboard')
def dashboard():
    return render_template(
        'dashboard.html',
        user=tables.users.current()
    )

@app.route('/my-profile', methods=['GET', 'POST'])
def my_profile():
    class Form(FlaskForm):
        id = StringField('User ID', render_kw={'readonly': True})

        sin = StringField('SIN', validators=[DataRequired(), Regexp(sanitize.sin_pattern, 0, 'Must have the form xxx-xxx-xxx.')])

        name = StringField('Name', validators=[DataRequired(), Length(1, 63)])
        dob = StringField('Date of Birth', validators=[DataRequired(), Length(1, 15)])
        address = StringField('Address', validators=[Length(0, 127)])
        occupation = StringField('Occupation', validators=[Length(0, 31)])

        username = StringField('Username', validators=[DataRequired(), Length(1, 63)])
        password = PasswordField('Password', validators=[Length(0, 63)])

        submit = SubmitField('Save Changes')

    def on_submit(form):
        tables.users.update_profile(
            sin=sanitize.sin(form.sin.data),

            name=form.name.data,
            dob=form.dob.data,
            address=form.address.data,
            occupation=form.occupation.data,

            username=form.username.data
        )
        flash('Your changes have been saved.', 'success')

    form = Form()
    if not form.is_submitted():
        user = tables.users.current()

        form.id.data = user.id

        form.sin.data = str(user.sin)

        form.name.data = user.name
        form.dob.data = str(user.dob)
        form.address.data = user.address
        form.occupation.data = user.occupation

        form.username.data = user.username

    return form_endpoint(form, 'my-profile.html',
                         on_submit=on_submit)

@app.route('/my-listings')
def my_listings():
    return render_template(
        'my-listings.html',
        user=tables.users.current(),
        listings=tables.listings.owned_by_current_user()
    )

if __name__ == '__main__':
    app.run()
