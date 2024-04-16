from wtforms import Form, BooleanField, StringField, PasswordField, validators

class SignupForm(Form):
    email = StringField('email', [validators.Length(min=3, max=254), validators.Email()])
    username = StringField('username', [validators.Length(min=2, max=25, message="Username must be between 2 and 25 characters")])
    password = PasswordField('password', [validators.Length(min=8, max=25, message="Password must be between 8 and 25 characters")])
    terms  = BooleanField('terms', [validators.DataRequired(message="Terms must be accepted")])
    newsletter  = BooleanField('newsletter', [])