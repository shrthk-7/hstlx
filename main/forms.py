from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed 
from flask_login import current_user
from main.models import User

from wtforms import StringField, SubmitField, PasswordField, BooleanField, TextAreaField, RadioField, MultipleFileField, IntegerField
from wtforms.validators import DataRequired, Length, Email, EqualTo, ValidationError, NumberRange

# forms are expressed as python classes
class RegistrationForm(FlaskForm):
	username 	= StringField('Username',
				validators=[Length(min=2, max=20), DataRequired()])
	email 		= StringField('Email',
				validators=[Email(), DataRequired()])
	password 	= PasswordField('Password',
				validators=[DataRequired()])
	confirm_password = PasswordField('Confirm Password',
				validators=[EqualTo('password'), DataRequired()])
	submit 		= SubmitField('Sign Up')

	def validate_username(self, username):
		user = User.query.filter_by(username=username.data).first()
		if user:
			raise ValidationError(f'{username.data} is already taken!')

	def validate_email(self, email):
		e = User.query.filter_by(email=email.data).first()
		if e:
			raise ValidationError(f'{email.data} is already taken!')

class LoginForm(FlaskForm):
	email 		= StringField('Email',
				validators=[DataRequired(), Email()])
	password 	= PasswordField('Password',
				validators=[DataRequired()])
	remember 	= BooleanField('Remember Me')
	submit 		= SubmitField('Sign In')

class updateAccountForm(FlaskForm):
	username 	= StringField('Username', 
				validators=[Length(min=2, max=20), DataRequired()])
	email 		= StringField('Email',
				validators=[Email(), DataRequired()])
	profile_picture = FileField('Upload a profile picture', validators=[FileAllowed(['jpg', 'png', 'jpeg'])])
	submit 		= SubmitField('Update')

	def validate_username(self, username):
		if username.data == current_user.username:
			return True
		user = User.query.filter_by(username=username.data).first()
		if user:
			raise ValidationError(f'{username.data} is already taken!')
	def validate_email(self, email):
		if email.data == current_user.email:
			return True
		e = User.query.filter_by(email=email.data).first()
		if e:
			raise ValidationError(f'{email.data} is already taken!')

class newItemForm(FlaskForm):
	title 	= StringField('Title', validators=[DataRequired()])
	content = TextAreaField('Content', validators=[DataRequired()])
	list_type = RadioField('List Type', choices=[('Sale', 'For Sale'), ('Rent', 'To Rent')],default='Sale')
	files = MultipleFileField('Images', description='Add images of the listed item',validators=[FileAllowed(['jpg', 'png', 'jpeg'])])
	price = IntegerField('Price', description='Enter the selling price or rent price of the listed item', validators=[DataRequired(), NumberRange(0)])
	submit 	= SubmitField('Post')