from wtforms import Form, BooleanField, StringField, PasswordField, validators

class SignupForm(Form):
    email = StringField('email', [validators.Length(min=3, max=254), validators.Email()])
    username = StringField('username', [validators.Length(min=2, max=25)])
    password = PasswordField('password', [validators.Length(min=8, max=25)])
    terms  = BooleanField('terms', [validators.DataRequired()])