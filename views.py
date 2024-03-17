from app import app
from flask import render_template, request, jsonify, json, abort
from markupsafe import escape
import flashcard
import transcript
import utility
import models
import datetime

TOKENS_PER_CHUNK = 3900
CARDS_PER_CHUNK = 4

@app.route('/')
@app.route("/index")
def index():
    return render_template('index.html', body_tag = "index")

@app.route("/flashcards", methods =["GET", "POST"])
def flashcards():
    if request.method == "POST":
        video_url = request.form.get("video-url")
        amount = utility.evaluate_select(str(request.form.get("amount")), ["low", "medium", "high"])
        diff = utility.evaluate_select(str(request.form.get("difficulty")), ["low", "medium", "high"])

        #honeypot spam protection
        honey_check = request.form.get("terms")
        honey_input = request.form.get("surname")
        if honey_check or honey_input != "": return render_template("base.html")

        if video_url != None:
            video_id = video_url.split("v=", 1)[1]

            #transcribe video
            try:
                video_transcript = transcript.get_transcript(escape(video_id))
            except: 
                abort(400)

            #get video info from data api
            try:
                video_info = transcript.get_video_info(video_id)
            except: 
                abort(400)

            flashcards = flashcard.generate_flashcards(flashcard.split_text(video_transcript, TOKENS_PER_CHUNK), CARDS_PER_CHUNK * amount, difficulty=diff)

            #create dictionary with all flash cards and convert to json
            dict_list = [flashcard.return_dict() for flashcard in flashcards]
            dict_list_json = json.dumps(dict_list)

            #save analytics data 
            models.add_session(video_id, datetime.datetime.now(), video_transcript, dict_list_json, amount, diff)
            return render_template('flashcards.html', body_tag = "show_flashcards", flashcards_dumps = dict_list_json, n_cards = len(dict_list), url = video_url, title = video_info["title"], channel = video_info["channel_title"])
        
    return render_template('flashcards.html', body_tag = "show_flashcards")

@app.errorhandler(500)
def internal_server_error(e):
    return render_template('500.html'), 500

@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404

@app.errorhandler(400)
def page_not_found(e):
    return render_template('400.html'), 400