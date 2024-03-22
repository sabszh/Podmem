from dotenv import load_dotenv
import os

load_dotenv() #requires .env file

OPENAI_KEY = os.getenv('OPEN_AI_API_KEY')
YOUTUBE_KEY = os.getenv('YT_API_KEY')
SECRET_KEY = os.getenv('SECRET_KEY')

DB_NAME = "analytics"
USER = os.getenv("DB_USER")
PIN = os.getenv("DB_PASSWORD")
HOST = os.getenv("DB_HOSTNAME")

class FlaskConfig: 
    ENVIRONMENT = "development"
    FLASK_APP = "Podmem"
    FLASK_DEBUG = True    
    SQLALCHEMY_DATABASE_URI = f"mysql+pymysql://{USER}:{PIN}@{HOST}/{DB_NAME}"
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    TRAP_HTTP_EXCEPTIONS = True
    SECRET_KEY = SECRET_KEY