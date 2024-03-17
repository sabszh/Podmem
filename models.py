from app import app, db
import pymysql
import config

# Sessions table
class Sessions(db.Model):
    __tablename__ = "sessions"
 
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    video_id = db.Column(db.String(200), nullable=False, unique=False)
    time = db.Column(db.DateTime, nullable=False, unique=False)
    transcript = db.Column(db.Text, nullable=False, unique=False)
    json_data = db.Column(db.JSON, nullable=False, unique=False)
    amount = db.Column(db.Integer, nullable=False, unique=False)
    difficulty = db.Column(db.Integer, nullable=False, unique=False)
    edited = db.Column(db.Boolean, nullable=True, unique=False)
    export_option = db.Column(db.String(30), nullable=True, unique=False)
    export_json = db.Column(db.String(30), nullable=True, unique=False)

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

#add session entry 
def add_session(video_id, time, transcript, json_data, amount, difficulty):

        session = Sessions(
            video_id=video_id,
            time=time,
            transcript=transcript,
            json_data=json_data,
            amount=amount,
            difficulty=difficulty,
        )
        db.session.add(session)
        db.session.commit()

#create analytics database and add tables defined in Sessions class
if __name__ == "__main__":
    create_db(config.DB_NAME)