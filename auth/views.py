from flask import Blueprint, render_template, redirect, request, url_for, flash
from werkzeug.security import generate_password_hash, check_password_hash
from markupsafe import escape 
import models
from auth.forms import SignupForm
from flask_login import login_user, login_required, current_user, logout_user
from app import limiter 
from auth.decorators import logout_required
from auth.token import generate_token, confirm_token
from datetime import datetime
from emails import send_email

auth_bp = Blueprint("auth", __name__)

@auth_bp.route("/login")
@logout_required
def login():
    return render_template("auth/login.html")

@auth_bp.route('/login', methods=['POST'])
@limiter.limit("10/minute")
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
@limiter.limit("30/minute")
@logout_required
def signup_post():
    form = SignupForm(request.form)
    validation = form.validate()
    if validation:
        username = form.username.data.lower()
        email = form.email.data
        newsletter = form.newsletter.data

        if models.User.query.filter_by(email=email).first(): # if this returns a user, then the email already exists in database
            return 'Email address already exists'

        if models.User.query.filter_by(username=username).first(): # if this returns a user, then the username already exists in database
            return 'Username already exists'

        token = generate_token(email)
        veri_url = url_for('auth.verify_email', token = token, _external=True)
        html = render_template("auth/verification_email.html", verification_url = veri_url, username = username)
        try:
            send_email(email, "Podmem Email Verification", html)
        except:
            return "Couldn't send email."
        
        # add the new user to the database
        user = models.add_user(email=form.email.data, username=form.username.data, password=generate_password_hash(form.password.data, method='scrypt'), newsletter = newsletter)
        login_user(user)

        return f'<span id = "response" hx-swap-oob="outerHTML"> <script>window.location.href = "{url_for("auth.inactive")}", true;</script></span>'
    else:
        #return "Invalid input."
        errors = [y[0] for x, y in form.errors.items()]
        response = ""
        for error in form.errors.items():
            response = f"{response} <span id = {error[0]} class = 'red alert' hx-swap-oob='outerHTML'>{error[1][0]}</span>"
            print(response)
        return response

@auth_bp.route('/verify/<token>')
@login_required
def verify_email(token):
    if current_user.is_verified:
        return render_template("message.html", message = "This account is already verified", submessage = "No sweat, you're already verified in our system!")
    email = confirm_token(token)
    user = models.User.query.filter_by(email=current_user.email).first_or_404()
    if user.email == email:
        user.is_verified = True
        user.verification_date = datetime.now()
        models.db.session.commit()
        return render_template("message.html", message = "Success!", submessage = "Your account has been verified.")
    else:
        return render_template("message.html", message = "Verification failed.", submessage = "The link is invalid or has expired.")

@auth_bp.route('/inactive')
@login_required
def inactive():
    if current_user.is_verified:
        return redirect(url_for('index'))
    return render_template('auth/inactive.html')

@auth_bp.route('/resend_verification')
@limiter.limit("5/minute")
@login_required
def resend_verification():
    if current_user.is_verified:
        return f'<script>window.location.href = {url_for("index")}</script>' 
    token = generate_token(current_user.email)  
    veri_url = url_for('auth.verify_email', token = token, _external=True)
    html = render_template("auth/verification_email.html", verification_url = veri_url)
    try:
        send_email(current_user.email, "Podmem Email Verification", html)
    except:
        return render_template("fragments/success.html", success = False)
    return render_template("fragments/success.html", success = True)

@auth_bp.route("/privacy_policy")
def privacy_policy():
    return render_template("fragments/privacy_policy.html")

@auth_bp.route("/terms")
def terms():
    return render_template("fragments/terms.html")

@auth_bp.route("/faq")
def faq_page():
    return render_template("fragments/faq_page.html")

@auth_bp.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))