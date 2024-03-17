from flask import Flask
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config.from_object("config.FlaskConfig")

# Creating SQLAlchemy instance
db = SQLAlchemy()

# Initializing Flask app with SQLAlchemy
db.init_app(app)


