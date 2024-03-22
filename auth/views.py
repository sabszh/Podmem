from flask import Blueprint, render_template, redirect, request, url_for, flash
from werkzeug.security import generate_password_hash, check_password_hash
from markupsafe import escape 
import models
from auth.forms import SignupForm
from flask_login import login_user, login_required, current_user, logout_user

auth_bp = Blueprint("auth", __name__)

@auth_bp.route("/login")
def login():
    return render_template("auth/login.html")

@auth_bp.route('/login', methods=['POST'])
def login_post():
    username = request.form.get('username')
    password = request.form.get('password')
    remember = request.form.get('remember')

    # check if the user exists
    user = models.User.query.filter_by(username=username).first()

    # take the user-supplied password, hash it, and compare it to the hashed password in the database
    if not user or not check_password_hash(user.password, password):
        flash('Please check your login details and try again')
        return redirect(url_for('auth.login')) # if the user doesn't exist or password is wrong, reload the page

    # if the above check passes, then we know the user has the right credentials
    login_user(user, remember=remember)
    return redirect(url_for('dashboard'))

@auth_bp.route("/signup")
def signup():
    return render_template("auth/signup.html")

@auth_bp.route('/signup', methods=['POST'])
def signup_post():
    form = SignupForm(request.form)
    validation = form.validate()
    if validation:
        if models.User.query.filter_by(email=form.email.data).first(): # if this returns a user, then the email already exists in database
            flash('Email address already exists')
            return redirect(url_for('auth.signup'))

        if models.User.query.filter_by(username=form.username.data).first(): # if this returns a user, then the email already exists in database
            flash('Username already exists')
            return redirect(url_for('auth.signup'))

        # add the new user to the database
        models.add_user(email=form.email.data, username=form.username.data, password=generate_password_hash(form.password.data, method='scrypt'))
        return redirect(url_for('auth.login'))
    else:
        flash([y for x, y in form.errors.items()])
        return redirect(url_for('auth.signup'))

@auth_bp.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))