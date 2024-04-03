from app import app, db, limiter, login_manager
from auth.views import auth_bp
from views import *
from models import *
import config
import pymysql

#auth init
app.register_blueprint(auth_bp)

login_manager.login_view = 'auth.login'
login_manager.init_app(app)

#limiter 
limiter.init_app(app)

@login_manager.user_loader
def load_user(user_id):
    # since the user_id is just the primary key of our user table, use it in the query for the user
    return User.query.get(int(user_id))

#create db
def create_db(name : str):

    # Initializing connection
    con = pymysql.connections.Connection(
        host=config.HOST,
        user=config.USER,
        password=config.PIN
    )

    # Creating cursor object
    cursor = con.cursor()

    cursor.execute(f"CREATE DATABASE IF NOT EXISTS {name}")
    cursor.execute("SHOW DATABASES")

    # Displaying databases
    for databases in cursor:
        print(databases)

    # Closing the cursor and connection to the database
    cursor.close()
    con.close()

#create tables in db.model
def create_tables():
    with app.app_context():
        create_db(config.DB_NAME)
        db.create_all()

if __name__ == '__main__':
    create_tables()
    app.run()