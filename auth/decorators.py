from functools import wraps
from flask import flash, redirect, url_for, render_template
from flask_login import current_user

#is logged out decorator
def logout_required(func):
    @wraps(func)
    def decorated_function(*args, **kwargs):
        if current_user.is_authenticated:
            return render_template('fragments/alert.html', message = 'You are already logged in') 
        return func(*args, **kwargs)

    return decorated_function

#is account verified?
def is_verified(func):
    @wraps(func)
    def decorated_function(*args, **kwargs):
        if current_user.is_verified is False:
            return redirect(url_for("auth.inactive"))
        return func(*args, **kwargs)

    return decorated_function