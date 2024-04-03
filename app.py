from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_mail import Mail
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from flask_login import LoginManager

app = Flask(__name__)
app.config.from_object("config.FlaskConfig")
mail = Mail(app)
login_manager = LoginManager()

#limiter init
limiter = Limiter(
    get_remote_address,
    default_limits=["200 per minute"],
    storage_uri="memory://",
)

# Creating SQLAlchemy instance
db = SQLAlchemy()

# Initializing Flask app with SQLAlchemy
db.init_app(app)