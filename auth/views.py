from flask import Blueprint, render_template, redirect, request, url_for, flash
from werkzeug.security import generate_password_hash, check_password_hash
from markupsafe import escape 
import models
from auth.forms import SignupForm
from flask_login import login_user, login_required, current_user, logout_user
from app import limiter 
from auth.decorators import logout_required

auth_bp = Blueprint("auth", __name__)

@auth_bp.route("/login")
@logout_required
def login():
    return render_template("auth/login.html")

@auth_bp.route('/login', methods=['POST'])
@limiter.limit("100/minute")
@logout_required
def login_post():
    username = request.form.get('username').lower()
    password = request.form.get('password')
    remember = request.form.get('remember')

    # check if the user exists
    user = models.User.query.filter_by(username=username).first()

    # take the user-supplied password, hash it, and compare it to the hashed password in the database
    if not user or not check_password_hash(user.password, password):
        return 'Please check your login details and try again'

    # if the above check passes, then we know the user has the right credentials
    login_user(user, remember=remember)
    return '<script>location.reload();</script>'

@auth_bp.route("/signup")
def signup():
    return render_template("auth/signup.html")

@auth_bp.route('/signup', methods=['POST'])
@limiter.limit("100/minute")
@logout_required
def signup_post():
    form = SignupForm(request.form)
    validation = form.validate()
    if validation:
        username = form.username.data.lower()
        if models.User.query.filter_by(email=form.email.data).first(): # if this returns a user, then the email already exists in database
            return 'Email address already exists'

        if models.User.query.filter_by(username=username).first(): # if this returns a user, then the username already exists in database
            return 'Username already exists'

        # add the new user to the database
        models.add_user(email=form.email.data, username=form.username.data, password=generate_password_hash(form.password.data, method='scrypt'))
        return '<script>location.reload();</script>'
    else:
        #return "Invalid input."
        return [y[0] for x, y in form.errors.items()]

@auth_bp.route("/privacy_policy")
def privacy_policy():
    return render_template("fragments/privacy_policy.html")

@auth_bp.route("/terms")
def terms():
    return render_template("fragments/terms.html")

@auth_bp.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))