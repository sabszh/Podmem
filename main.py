from app import app, db
from views import *
from models import *
import config
import pymysql

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
    create_db(config.DB_NAME)    
    create_tables()
    app.run()