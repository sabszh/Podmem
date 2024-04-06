from flask_mail import Message
from app import mail, app

def send_email(to, subject, html):
	msg = Message(subject,html=html, recipients=[to])
	with app.app_context():
		mail.send(msg)