from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField, DateField
from wtforms.validators import DataRequired, Email, EqualTo, Length, ValidationError
from .models import User # To check if username/email already exists

class RegistrationForm(FlaskForm):
    username = StringField('Username',
                           validators=[DataRequired(), Length(min=2, max=20)])
    email = StringField('Email',
                        validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired(), Length(min=6)])
    confirm_password = PasswordField('Confirm Password',
                                     validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Sign Up')

    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user:
            raise ValidationError('That username is taken. Please choose a different one.')

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user:
            raise ValidationError('That email is already registered. Please choose a different one or login.')

class LoginForm(FlaskForm):
    email = StringField('Email',
                        validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember_me = BooleanField('Remember Me')
    submit = SubmitField('Login')

class CreateHouseholdForm(FlaskForm):
    name = StringField('Household Name', validators=[DataRequired(), Length(min=2, max=100)])
    submit = SubmitField('Create Household')

class CreateShoppingListForm(FlaskForm):
    name = StringField('List Name', validators=[DataRequired(), Length(min=2, max=100)])
    date = DateField('Date', format='%Y-%m-%d', validators=[DataRequired()])
    submit = SubmitField('Create List')

class AddShoppingItemForm(FlaskForm):
    name = StringField('Item Name', validators=[DataRequired(), Length(min=1, max=100)])
    category = StringField('Category', validators=[Length(max=50)])
    amount = StringField('Amount', validators=[Length(max=50)])
    free_text = StringField('Notes', validators=[Length(max=200)]) # Using StringField for TextArea-like behavior if not using specific TextArea field
    submit = SubmitField('Add Item')

class EditShoppingItemForm(FlaskForm):
    name = StringField('Item Name', validators=[DataRequired(), Length(min=1, max=100)])
    category = StringField('Category', validators=[Length(max=50)])
    amount = StringField('Amount', validators=[Length(max=50)])
    free_text = StringField('Notes', validators=[Length(max=200)])
    bought = BooleanField('Bought')
    submit = SubmitField('Update Item')
