from flask import Flask, render_template, redirect, url_for, request, session, flash
from flask_bootstrap import Bootstrap5
from flask_session import Session
from flask_wtf import FlaskForm
from mysql.connector import IntegrityError, DataError
from wtforms import StringField, PasswordField, IntegerField, FloatField, SelectField, SelectMultipleField, SubmitField
from wtforms.validators import DataRequired, Length, Regexp, ValidationError
from datetime import datetime, timedelta

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

def validate_dob(field):
    if not field.data:
        return
    try:
        dob_date = datetime.strptime(field.data, "%Y-%m-%d").date()
    except ValueError:
        raise ValidationError("Invalid date format. Please use YYYY-MM-DD.")

    current_date = datetime.now().date()
    max_dob_date = current_date - timedelta(days=365 * 18)
    min_dob_date = current_date - timedelta(days=365 * 100)

    if dob_date >= current_date:
        raise ValidationError("Date of Birth cannot be in the future.")

    if dob_date >= max_dob_date:
        raise ValidationError("Date of Birth should be at least 18 years ago.")

    if dob_date <= min_dob_date:
        raise ValidationError("Date of Birth should be less than 100 years ago.")
        
@app.route('/')
def home():
    return render_template('index.html')

@app.route('/sign-up', methods=['GET', 'POST'])
def sign_up():
    class Form(FlaskForm):
        sin = StringField('SIN', validators=[DataRequired(), Regexp(sanitize.sin_pattern, 0, 'Must have the form xxx-xxx-xxx.')], render_kw={"placeholder": "xxx-xxx-xxx"})

        name = StringField('Name', validators=[DataRequired(), Length(1, 63)])
        dob = StringField('Date of Birth', validators=[DataRequired(), Length(1, 15)], render_kw={"placeholder": "YYYY-MM-DD"})
        address = StringField('Address', validators=[Length(0, 127)])
        occupation = StringField('Occupation', validators=[Length(0, 31)])

        username = StringField('Choose a Username', validators=[DataRequired(), Length(1, 63)])
        password = PasswordField('Choose a Password', validators=[Length(0, 63)])

        submit = SubmitField('Sign Up')
    
    def on_submit(form):
        validate_dob(form.dob)
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
@app.route('/my-profile/delete', methods=['POST'])
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
        delete = SubmitField('Delete Account', render_kw={'class': 'btn-light btn-outline-danger', 'formaction': '/my-profile/delete'})

    is_delete_request = (request.path.lower() == '/my-profile/delete')

    def on_submit(form):
        if is_delete_request:
            tables.users.delete_current()
            flash('Your account was deleted.', 'success')
        else:
            validate_dob(form.dob)
            tables.users.update_profile(
                sin=sanitize.sin(form.sin.data),

                name=form.name.data,
                dob=form.dob.data,
                address=form.address.data,
                occupation=form.occupation.data,

                username=form.username.data
            )
            flash('Your changes have been saved.', 'success')

    user = tables.users.current()

    form = Form()
    if not form.is_submitted():
        form.id.data = user.id

        form.sin.data = str(user.sin)

        form.name.data = user.name
        form.dob.data = str(user.dob)
        form.address.data = user.address
        form.occupation.data = user.occupation

        form.username.data = user.username

    return form_endpoint(
        form, 'my-profile.html',
        on_submit=on_submit,
        next_location=('/' if is_delete_request else None),
        template_args={
            'user': user
        }
    )

@app.route('/my-listings')
def my_listings():
    return render_template(
        'my-listings.html',
        user=tables.users.current(),
        listings=tables.listings.owned_by_current_user()
    )

@app.route('/listings/<id>/edit', methods=['GET', 'POST'])
def listing(id):
    class Form(FlaskForm):
        id = StringField('Listing ID', render_kw={'readonly': True})

        country = StringField('Country', validators=[Length(1, 31)])
        city = StringField('City', validators=[Length(1, 31)])
        postal = StringField('Postal', validators=[Length(6, 6)])
        address = StringField('Address', validators=[Length(0, 127)])

        lat = FloatField('Latitude', validators=[DataRequired()])
        lon = FloatField('Longitude', validators=[DataRequired()])

        type = SelectField(
            'Type',
            choices=[
                'Apartment',
                'House',
                'Bed and breakfast',
                'Boutique hotel',
                'Bungalow',
                'Cabin',
                'Chalet',
                'Condominium',
                'Cottage',
                'Guest suite',
                'Guesthouse',
                'Hostel',
                'Hotel',
                'Kezhan',
                'Loft',
                'Resort',
                'Serviced apartment',
                'Townhouse',
                'Villa',
            ])
        amenities = SelectMultipleField(
            'Amenities (select multiple)',
            choices=[
                'Wifi',
                'Kitchen',
                'Washer',
                'Air conditioning',
                'Iron',
                'Free parking',
                'Dryer',
                'Heating',
                'Dedicated workspace',
                'TV',
                'Hair dryer',
                'Pool',
                'Hot tub',
                'EV charger',
                'Crib',
                'Gym',
                'BBQ grill',
                'Breakfast',
                'Indoor fireplace',
                'Smoking allowed',
                'Beachfront',
                'Waterfront',
                'Ski-in/ski-out',
                'Smoke alarm',
                'Carbon monoxide alarm',
            ],
            render_kw={
                'size': '10'
            }
        )

        submit = SubmitField('Save Changes')

    def on_submit(form):
        tables.listings.update(
            id=id,

            country=form.country.data,
            city=form.city.data,
            postal=form.postal.data,
            address=form.address.data,

            lat=form.lat.data,
            lon=form.lon.data,

            type=form.type.data,
            amenities=', '.join(form.amenities.data),
        )
        flash('Your changes have been saved.', 'success')

    listing = tables.listings.for_id(id).fetchone()

    form = Form()
    if not form.is_submitted():
        form.id.data = listing.id

        form.country.data = listing.country
        form.city.data = listing.city
        form.postal.data = listing.postal
        form.address.data = listing.address

        form.lat.data = listing.lat
        form.lon.data = listing.lon

        form.type.data = listing.type
        form.amenities.data = listing.amenities.split(', ')

    return form_endpoint(
        form, 'listing-edit.html',
        on_submit=on_submit,
        template_args={
            'user': tables.users.current(),
            'listing': listing
        }
    )

if __name__ == '__main__':
    app.run()
