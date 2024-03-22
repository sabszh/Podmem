from app import db
from flask_login import UserMixin

# Users table
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True) # primary keys are required by SQLAlchemy
    username = db.Column(db.String(100), unique=True)
    email = db.Column(db.String(100), unique=True)
    password = db.Column(db.String(1000))

#add new user
def add_user(username, password, email):
    user = User(
        username=username,
        password=password,
        email=email
    )
    db.session.add(user)
    db.session.commit()

class UserDeck(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer)
    session_id = db.Column(db.Integer, nullable=False, unique=False)
    video_id = db.Column(db.String(20), nullable=True, unique=False)
    json_data = db.Column(db.JSON, nullable=False, unique=False)
    title = db.Column(db.String(200), nullable=True, unique=False)
    channel = db.Column(db.String(200), nullable=True, unique=False)
    creation_date = db.Column(db.DateTime, nullable=False, unique=False)
    last_practiced = db.Column(db.DateTime, nullable=False, unique=False)

def add_userdeck(user_id, session_id, json_data, creation_date, last_practiced, title, channel, video_id):
    deck = UserDeck(user_id=user_id, session_id=session_id, json_data=json_data, creation_date=creation_date, last_practiced=last_practiced, title=title, channel=channel, video_id = video_id)
    db.session.add(deck)
    db.session.commit()

# Sessions table
class Sessions(db.Model):
    __tablename__ = "sessions"
 
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    video_id = db.Column(db.String(200), nullable=False, unique=False)
    title = db.Column(db.String(200), nullable=True, unique=False)
    channel = db.Column(db.String(200), nullable=True, unique=False)
    time = db.Column(db.DateTime, nullable=False, unique=False)
    transcript = db.Column(db.Text, nullable=False, unique=False)
    json_data = db.Column(db.JSON, nullable=False, unique=False)
    amount = db.Column(db.Integer, nullable=False, unique=False)
    difficulty = db.Column(db.Integer, nullable=False, unique=False)
    edited = db.Column(db.Boolean, nullable=True, unique=False)
    export_option = db.Column(db.String(30), nullable=True, unique=False)
    export_json = db.Column(db.String(30), nullable=True, unique=False)

#add session entry 
def add_session(video_id, time, transcript, json_data, amount, difficulty, title, channel):
    session = Sessions(
        video_id=video_id,
        time=time,
        transcript=transcript,
        json_data=json_data,
        amount=amount,
        difficulty=difficulty,
        title = title,
        channel = channel
    )
    db.session.add(session)
    db.session.commit()
    return session.id
