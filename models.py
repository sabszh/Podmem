from app import db
from flask_login import UserMixin
from datetime import datetime

# Users table
class User(UserMixin, db.Model):
    __tablename__ = "user"
    id = db.Column(db.Integer, primary_key=True) # primary keys are required by SQLAlchemy
    username = db.Column(db.String(100), unique=True)
    email = db.Column(db.String(100), unique=True)
    password = db.Column(db.String(1000))
    is_verified = db.Column(db.Boolean, nullable=True, unique=False)
    creation_date = db.Column(db.DateTime, nullable=False, unique=False)

#add new user
def add_user(username, password, email, is_verified = False, creation_date = datetime.now()):
    user = User(
        username=username,
        password=password,
        email=email,
        is_verified = is_verified,
        creation_date = creation_date
    )
    db.session.add(user)
    db.session.commit()

class UserCard(db.Model):
    __tablename__ = "user_card"

    id = db.Column(db.Integer, primary_key=True)
    answer = db.Column(db.Text, nullable=False, unique=False)
    question = db.Column(db.Text, nullable=False, unique=False)
    deck_id = db.Column(db.Integer, db.ForeignKey('user_deck.id'))
    deck = db.relationship("UserDeck", back_populates="cards")
    easiness = db.Column(db.Float, nullable=True, unique=False)
    interval = db.Column(db.Integer, nullable=False, unique=False)
    repetitions = db.Column(db.Integer, nullable=False, unique=False)
    due_date = db.Column(db.DateTime, nullable=False, unique=False)
    dont_show = db.Column(db.Boolean, nullable=True, unique=False)
    last_practiced = db.Column(db.DateTime, nullable=False, unique=False)
    total_repetitions = db.Column(db.Integer, nullable=False, unique=False)

#add session entry 
def add_usercard(deck_id, answer, question, easiness = 0, interval = 0, repetitions = 0, due_date=datetime.now(), dont_show=False, last_practiced=datetime.now(), total_repetitions = 0):
    user_card = UserCard(
        deck_id=deck_id,
        answer=answer,
        question=question,
        easiness=easiness,
        interval=interval,
        repetitions=repetitions,
        due_date=due_date,
        dont_show = dont_show,
        last_practiced = last_practiced,
        total_repetitions = total_repetitions
    )
    db.session.add(user_card)
    db.session.commit()
    return user_card.id

class UserDeck(db.Model):
    __tablename__ = "user_deck"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    user = db.relationship("User", backref=db.backref("user", uselist=False))
    creation_date = db.Column(db.DateTime, nullable=False, unique=False)
    video_id = db.Column(db.String(200), db.ForeignKey('video.video_id'))
    video = db.relationship("Video", backref=db.backref("video", uselist=False))
    cards = db.relationship("UserCard", back_populates="deck")

def add_userdeck(user_id, video_id, creation_date=datetime.now()):
    deck = UserDeck(user_id=user_id, video_id=video_id, creation_date=creation_date)
    db.session.add(deck)
    db.session.commit()
    return deck.id

# Sessions table
class Video(db.Model):
    __tablename__ = "video"
 
    video_id = db.Column(db.String(200), primary_key=True)
    title = db.Column(db.String(200), nullable=True, unique=False)
    channel = db.Column(db.String(200), nullable=True, unique=False)

#add session entry 
def add_video(video_id, title, channel):
    video = Video(
        video_id = video_id,
        title = title,
        channel = channel
    )

    db.session.add(video)
    db.session.commit()

# Sessions table
class Sessions(db.Model):
    __tablename__ = "sessions"
 
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    video_id = db.Column(db.String(200), db.ForeignKey('video.video_id'))
    time = db.Column(db.DateTime, nullable=False, unique=False)
    json_data = db.Column(db.JSON, nullable=False, unique=False)
    amount = db.Column(db.Integer, nullable=False, unique=False)
    difficulty = db.Column(db.Integer, nullable=False, unique=False)
    edited = db.Column(db.Boolean, nullable=True, unique=False)
    export_option = db.Column(db.String(30), nullable=True, unique=False)
    export_json = db.Column(db.JSON, nullable=True, unique=False)

#add session entry 
def add_session(video_id, json_data, amount, difficulty, time=datetime.now()):
    session = Sessions(
        video_id=video_id,
        time=time,
        json_data=json_data,
        amount=amount,
        difficulty=difficulty,
    )

    db.session.add(session)
    db.session.commit()
    return session.id
