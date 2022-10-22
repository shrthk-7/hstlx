from datetime import datetime
from sqlalchemy import  Column, String, Integer, DateTime, Text
from main import db, login_manager, app
from flask_login import UserMixin

@login_manager.user_loader
def load_user(user_id):
	return User.query.get(int(user_id))

class User(db.Model, UserMixin):
	id 			= Column(Integer, primary_key=True)
	username 	= Column(String(20), unique=True, nullable=False)
	email 		= Column(String(120), unique=True, nullable=False)
	image_file	= Column(String(20), nullable=False, default='default.jpg')
	password 	= Column(String(60), nullable=False)
	posts 		= db.relationship('Post', backref='author', lazy=True)
	
	def __repr__(self):
		return f"User('{self.username}', '{self.email}', '{self.image_file}')"

class Post(db.Model):
	id 			= Column(Integer, primary_key=True)
	title 		= Column(String(100), nullable=False)
	date_posted = Column(DateTime, nullable=False, default=datetime.utcnow)
	content 	= Column(Text, nullable=False)
	list_type 	= Column(Text, nullable=False)
	images 		= Column(String, nullable=True)
	price 		= Column(String, nullable=False)
	user_id 	= Column(Integer, db.ForeignKey('user.id'), nullable=False) 

	def __repr__(self):
		return f"Post('{self.title}', '{self.date_posted}')"