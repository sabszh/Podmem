import requests
from flask_mail import Message
from app import mail, app

def send_simple_message():
	return requests.post(
		"https://api.mailgun.net/v3/podmem.com/messages",
		auth=("api", "f68a26c9-8a9e5ad5"),
		data={"from": "Excited User <postmaster@podmem.com>",
			"to": ["gustavidunsloth@hotmail.com"],
			"subject": "Hello",
			"text": "Testing some Mailgun awesomeness!"})

def send_smtp():
    msg = Message("Hello",body="Dette er den første mail fra Podmem. Det virker super godt. Vh Podmem", recipients=["gustavidunsloth@hotmail.com"])
    mail.send(msg)

with app.app_context():
    send_smtp()