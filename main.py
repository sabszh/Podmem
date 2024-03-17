from app import app, db
from views import *
from models import *

#create tables in db.model
def create_tables():
    with app.app_context():
        db.create_all()

if __name__ == '__main__':
    create_tables()
    app.run()