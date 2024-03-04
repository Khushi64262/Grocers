from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, BooleanField, DateField, DecimalField, SelectField, IntegerField
from wtforms.validators import DataRequired, Length, Email, EqualTo, ValidationError
from MAD1.models import User, Category
from datetime import datetime

class RegistrationForm(FlaskForm):
    username = StringField("Username", validators=[DataRequired(), Length(min=2, max=20)])
    email = StringField("Email", validators=[DataRequired(), Email()])
    password = PasswordField("Password", validators=[DataRequired()])
    confirm_password = PasswordField("Confirm Password", validators=[DataRequired(), EqualTo("password")])
    submit = SubmitField("Sign up")

    def validate_username(self, username):
        user = User.query.filter_by(username = username.data).first()
        if user:
            raise ValidationError('Username already taken, chose a different one!')
        
    def validate_email(self, email):
        user = User.query.filter_by(email = email.data).first()
        if user:
            raise ValidationError('Account with this email-id already exists')

class LoginForm(FlaskForm):
    email = StringField("Email", validators=[DataRequired(), Email()])
    password = PasswordField("Password", validators=[DataRequired()])
    is_admin = BooleanField("Are you an admin?")
    remember = BooleanField('Remember me')
    submit = SubmitField("Log in")


class CategoryForm(FlaskForm):
    name = StringField("Category Name", validators=[DataRequired(), Length(min=2, max=50)])
    submit = SubmitField("Add Category")

    def validate_name(self, field):
        if Category.query.filter_by(name=field.data).first():
            raise ValidationError('Category with this name already exists.')

class ProductForm(FlaskForm):
    name = StringField("Product Name", validators=[DataRequired(), Length(min=2, max=100)])
    manufacturer = StringField("Manufacturer", validators=[DataRequired(), Length(min=2, max=100)])
    expiry_date = DateField("Expiry Date", validators=[DataRequired()])
    rate_per_unit = DecimalField("Rate per Unit", validators=[DataRequired()])
    unit = StringField("Unit", validators=[DataRequired(), Length(min=1, max=20)])
    units_available = IntegerField("Units Available")
    category = SelectField("Category", coerce=int, validators=[DataRequired()])
    submit = SubmitField("Add Product")

    def validate_rate_per_unit(self, field):
        if field.data <= 0:
            raise ValidationError('Rate per unit must be greater than 0.')

    def validate_expiry_date(self, field):
        if field.data < datetime.today().date():
            raise ValidationError('Expiry date must be in the future.')
