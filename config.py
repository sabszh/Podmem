from dotenv import load_dotenv
import os

load_dotenv() #requires .env file

OPENAI_KEY = os.getenv('OPEN_AI_API_KEY')
YOUTUBE_KEY = os.getenv('YT_API_KEY')
SECRET_KEY = os.getenv('SECRET_KEY')
SECRET_SECURITY_SALT = os.getenv('SECRET_SECURITY_SALT')

DB_NAME = os.getenv("DB_NAME")
USER = os.getenv("DB_USER")
PIN = os.getenv("DB_PASSWORD")
HOST = os.getenv("DB_HOSTNAME")
ENVIRONMENT = os.getenv("ENVIRONMENT")
MAIL_PASS = os.getenv("MAIL_PASS")
MAIL_USER = os.getenv("MAIL_USER")
MAIL_SERVER = os.getenv("MAIL_SERVER")

class FlaskConfig: 
    ENVIRONMENT = ENVIRONMENT
    FLASK_APP = "Podmem"
    FLASK_DEBUG = False   
    SQLALCHEMY_DATABASE_URI = f"mysql+pymysql://{USER}:{PIN}@{HOST}/{DB_NAME}"
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    TRAP_HTTP_EXCEPTIONS = True
    SECRET_KEY = SECRET_KEY
    SECURITY_PASSWORD_SALT = SECRET_SECURITY_SALT
    MAIL_DEFAULT_SENDER = MAIL_USER
    MAIL_SERVER = MAIL_SERVER
    MAIL_PORT = 587
    MAIL_USERNAME = MAIL_USER
    MAIL_PASSWORD = MAIL_PASS