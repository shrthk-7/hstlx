from flask import render_template, url_for, redirect, flash, request, abort
from flask_login import login_user, logout_user, current_user, login_required
from flask_mail import Message
from werkzeug.utils import secure_filename

from main.models import User, Post
from main.forms import (RegistrationForm, LoginForm, updateAccountForm, newItemForm)
from main import app, bcrypt, db, mail


#to create random profile picture names
from secrets import token_hex
#to create path to save profile picture
import os
#to resize uploaded image
from PIL import Image

@app.route("/")
@app.route("/home")
def home():
	page = request.args.get('page', 1, type=int)
	# images = post.images.split(',')
	posts = Post.query.order_by(Post.date_posted.desc()).paginate(page=page, per_page=3) 
	return render_template('home.html', posts=posts, title="Home Page")

@app.route("/about")
def about():
	return render_template('about.html', title="About Page")

@app.route("/login", methods=['GET', 'POST'])
def login():
	if current_user.is_authenticated:
		flash('You are already logged in', category='success')
		return redirect(url_for('home'))
	form = LoginForm()
	if form.validate_on_submit():
		user = User.query.filter_by(email=form.email.data).first()
		if user and bcrypt.check_password_hash(user.password,  form.password.data):
			login_user(user, remember = form.remember.data)
			next_page = request.args.get('next') #returns none
			flash('You have logged in successfully', category='success')
			return redirect(next_page) if next_page else redirect(url_for('home'))
		else:
			flash('Failed to log in', category='danger')
			return redirect(url_for('login'))
	return render_template('login.html', title="Log In", form=form)

@app.route("/register", methods=['GET', 'POST'])
def register():
	form = RegistrationForm()
	if form.validate_on_submit():
		hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
		user = User(username = form.username.data, email = form.email.data, password = hashed_password)
		db.session.add(user)
		db.session.commit()
		flash(f"Account created for {form.username.data}", category='success')
		return redirect(url_for('login')) 
	'''
		'home' is the name of the function to redirect, not route
	'''
	return render_template('register.html', title="Register", form=form)

@app.route("/logout")
@login_required
def logout():
	logout_user()
	flash('Successfully logged out', category='success')
	return redirect(url_for('home'))

def save_picture(img_data, path):
	_, file_ext = os.path.splitext(img_data.filename)
	filename = secure_filename(str(hash(img_data.filename))) + file_ext
	img_path = os.path.join(app.root_path, path, filename)
	img_data.save(img_path)
	return filename

@app.route("/account", methods=['GET', 'POST'])
@login_required
def account():
	form = updateAccountForm()
	if form.validate_on_submit():
		if form.profile_picture.data:
			picture_file = save_picture(form.profile_picture.data, 'static/profile_pictures')
			current_user.image_file = picture_file
		current_user.username = form.username.data
		current_user.email = form.email.data
		db.session.commit()
		flash('Account Details updated', category='success')
		return redirect(url_for('account'))
	elif request.method == 'GET':
		form.username.data = current_user.username
		form.email.data = current_user.email
	image_url = url_for('static', filename=f'profile_pictures/{current_user.image_file}')
	if os.path.exists(f'./main/{image_url}') == False:
		image_url = url_for('static', filename='profile_pictures/default.jpg')
	return render_template('account.html', title='Account', image_file=image_url, form=form)

@app.route("/post/new", methods=['GET', 'POST'])
@login_required
def new_post():
	form = newItemForm()
	if form.validate_on_submit():
		files = []
		if form.files.data:
			for file in form.files.data:
				img = save_picture(file, 'static/product_pictures')
				files.append(img)
		file_str = ','.join(files)
		print(file_str)
		post = Post(title=form.title.data, content=form.content.data, author=current_user, list_type=form.list_type.data, images=file_str, price= form.price.data)
		db.session.add(post)
		db.session.commit()
		flash('Post Added', category='success')
		return redirect(url_for('home'))
	return render_template('create_post.html', title='List New Item', form = form, legend = 'List New Item')

@app.route("/post/<int:post_id>")
def post(post_id):
	post = Post.query.get_or_404(post_id)
	images = post.images.split(',')
	print(images)
	return render_template('post.html', title=post.title, post=post, images=images)

@app.route("/post/<int:post_id>/update", methods = ['GET', 'POST'])
@login_required
def update_post(post_id):
	post = Post.query.get_or_404(post_id)
	if post.author != current_user:
		abort(403)
	form = newItemForm()
	if form.validate_on_submit():
		post.title = form.title.data
		post.content = form.content.data
		db.session.commit()
		flash('Post successfully updated', category='success')
		return redirect(url_for('post', post_id = post.id))
	elif request.method == 'GET':
		form.title.data = post.title
		form.content.data = post.content
	return render_template('create_post.html', title='Update Post', form=form, legend='Update Post')

@app.route("/post/<int:post_id>/delete", methods=['POST'])
@login_required
def delete_post(post_id):
	post = Post.query.get_or_404(post_id)
	if post.author != current_user:
		abort(403)
	db.session.delete(post)
	db.session.commit()
	flash('Post Successfully Deleted', category='success')
	return redirect(url_for('home'))

@app.route("/user/<string:username>")
def user_posts(username):
	page = request.args.get('page', 1, type=int)
	user = User.query.filter_by(username=username).first_or_404()
	posts = Post.query.filter_by(author=user).order_by(Post.date_posted.desc()).paginate(page=page, per_page=5)
	return render_template('user_posts.html',user=user, posts=posts, title=f"{username}'s Posts")