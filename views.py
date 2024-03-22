from app import app
from flask import render_template, request, jsonify, json, abort, redirect, flash, url_for
from markupsafe import escape
import flashcard
import transcript
import utility
import models
import datetime
from flask_login import current_user, login_required

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
        amount = utility.evaluate_select(str(escape(request.form.get("amount"))), ["low", "medium", "high"])
        diff = utility.evaluate_select(str(escape(request.form.get("difficulty"))), ["low", "medium", "high"])

        #honeypot spam protection
        honey_check = request.form.get("terms")
        honey_input = request.form.get("surname")
        if honey_check or honey_input != "": return render_template("base.html")

        if video_url != None:
            video_id = video_url.split("v=", 1)[1]
            #look in db to see if video already has been prompted
            video_match = models.Sessions.query.filter_by(video_id=video_id).first()
            if video_match:
                #save analytics data 
                id = models.add_session(video_id, datetime.datetime.now(), video_match.transcript, video_match.json_data, video_match.amount, video_match.difficulty, video_match.title, video_match.channel)
                return render_template('flashcards.html', body_tag = "show_flashcards", flashcards_dumps = video_match.json_data, url = video_url, title = video_match.title, channel = video_match.channel, video_id=video_id, session_id = id)
            else: #only generate new entry if video doesnt exist in db
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
                id = models.add_session(video_id, datetime.datetime.now(), video_transcript, dict_list_json, amount, diff, video_info["title"], video_info["channel_title"])
                return render_template('flashcards.html', body_tag = "show_flashcards", flashcards_dumps = dict_list_json, url = video_url, title = video_info["title"], channel = video_info["channel_title"], video_id = video_id, session_id=id)
        
    return render_template('flashcards.html', body_tag = "show_flashcards")

@app.route("/dashboard")
@login_required
def dashboard():
    # check for decks corresponding to user id 
    decks = models.UserDeck.query.filter_by(user_id=current_user.id).all()
    if decks:
        return render_template("dashboard.html", decks = decks)
    else:
        flash("No cards saved.")
        return render_template("dashboard.html")

@app.route("/save_deck/<video_id>/<session_id>", methods=['GET', 'POST'])
@login_required
def save_deck(video_id, session_id):
    #models.Sessions.query.filter_by(video_id=video_id).first()
    session = models.Sessions.query.filter_by(id = session_id).first()
    if session:
        userdeck = models.UserDeck.query.filter_by(user_id = current_user.id).filter_by(video_id= video_id).first() 
        json_data = request.get_json()
        if json_data:
            if userdeck: #overwrite if entry already exists
                models.db.session.delete(userdeck)
                models.db.session.commit()
            models.add_userdeck(current_user.id,session_id,json_data,datetime.datetime.now(),datetime.datetime.now(), session.title, session.channel, session.video_id)
            return redirect(url_for("dashboard"))
        else:
            abort(400)
    else:
        abort(400)

@app.route("/view_userdeck/<id>", methods=['GET'])
@login_required
def view_userdeck(id):
    userdeck = models.UserDeck.query.filter_by(id=id).first()
    if userdeck:
        if userdeck.user_id == current_user.id:
            return render_template('flashcards.html', body_tag = "show_flashcards", flashcards_dumps = json.dumps(userdeck.json_data), title = userdeck.title, channel = userdeck.channel, video_id = userdeck.video_id, session_id=userdeck.session_id)
        else: 
            flash("You do not have access to this page.")
            return redirect(url_for("dashboard"))
    else:
        flash("The deck doesn't exist")
        return redirect(url_for("dashboard"))

@app.route("/delete_userdeck/<id>", methods=['GET'])
@login_required
def delete_userdeck(id):
    userdeck = models.UserDeck.query.filter_by(id=id).first()
    if userdeck:
        models.db.session.delete(userdeck)
        models.db.session.commit()
        return redirect(url_for("dashboard"))
    else:
        flash("The deck doesn't exist")
        return redirect(url_for("dashboard"))

@app.errorhandler(500)
def internal_server_error(e):
    return render_template('errors/500.html'), 500

@app.errorhandler(404)
def page_not_found(e):
    return render_template('errors/404.html'), 404

@app.errorhandler(400)
def page_not_found(e):
    return render_template('errors/400.html'), 400