from app import app, limiter
from flask import render_template, request, jsonify, json, abort, redirect, flash, url_for
from markupsafe import escape
import flashcard
import transcript
import utility
import models
import datetime
import re
from flask_login import current_user, login_required
from supermemo2 import SMTwo
from auth.decorators import is_verified

TOKENS_PER_CHUNK = 3900
CARDS_PER_CHUNK = 4

@app.route('/')
@app.route("/index")
def index():
    return render_template('index.html')

@app.route("/flashcards", methods =["GET", "POST"])
def flashcards():
    if request.method == "POST":
        video_url = request.form.get("video-url")
        amount = utility.evaluate_select(str(escape(request.form.get("amount"))), ["low", "medium", "high"])
        diff = utility.evaluate_select(str(escape(request.form.get("difficulty"))), ["low", "medium", "high"])

        #honeypot spam protection
        honey_check = request.form.get("terms")
        honey_input = request.form.get("surname")
        if honey_check or honey_input != "":
            return render_template("base.html")

        if video_url != None:
            # Check if the URL is a mobile link
            if "youtu.be" in video_url:
                # Extract video ID from mobile link
                video_id = video_url.split("/")[-1].split("?")[0]
            else:
                # Extract video ID from standard YouTube URL
                video_id = video_url.split("v=", 1)[1]
                # Check if there are additional parameters after video ID and remove them
                video_id = video_id.split("&", 1)[0]

            #look in db to see if video already has been prompted
            session = models.Sessions.query.filter(models.Sessions.video_id==video_id, models.Sessions.difficulty == diff, models.Sessions.amount == amount, models.Sessions.json_data != "").first() 
            video_match = models.Video.query.filter_by(video_id=video_id).first()
            
            #get video info from data api
            try:
                video_info = transcript.get_video_info(video_id)
            except Exception as error:
                raise FlashcardError(error) 

            #transcribe video
            try:
                video_transcript = transcript.get_transcript(video_id)
            except Exception as error: 
                raise FlashcardError(error)

            if session:
                id = models.add_session(video_id, "", session.amount, session.difficulty)
                return render_template('flashcards.html', flashcards_dumps = session.json_data, url = video_url, title = video_match.title, channel = video_match.channel, session_id = id, transcript = video_transcript)
            else: #only generate new entry if exact prompt doesnt already exist in db
                flashcards = flashcard.generate_flashcards(flashcard.split_text(video_transcript, TOKENS_PER_CHUNK), CARDS_PER_CHUNK * amount, difficulty=diff)
                #create dictionary with all flash cards and convert to json
                dict_list = [flashcard.return_dict() for flashcard in flashcards]
                dict_list_json = json.dumps(dict_list)
                #save analytics data 
                if not video_match: #only add new video if it doesn't already exist
                    models.add_video(video_id, video_info["title"], video_info["channel_title"])
                id = models.add_session(video_id, dict_list_json, amount, diff)
                return render_template('flashcards.html', flashcards_dumps = dict_list_json, url = video_url, title = video_info["title"], channel = video_info["channel_title"], video_id = video_id, session_id=id, transcript = video_transcript)
            
    #if there is no post request, redirect to index    
    return redirect('index')

@app.route("/dashboard")
@login_required
@is_verified
def dashboard():
    # check for decks corresponding to user id 
    decks = models.UserDeck.query.filter_by(user_id=current_user.id).all()
    if decks:
        return render_template("dashboard.html", decks = decks)
    else:
        flash("No cards saved.")
        return render_template("dashboard.html")

@app.route("/save_deck/<session_id>", methods=['GET', 'POST'])
@login_required
@is_verified
def save_deck(session_id):
    session = models.Sessions.query.filter_by(id = session_id).first()
    if session:
        #check if this session contains json – otherwise fetch "parent" session
        if session.json_data == "":
            parent_session = models.Sessions.query.filter(models.Sessions.video_id==session.video_id, models.Sessions.difficulty == session.difficulty, models.Sessions.amount == session.amount, models.Sessions.json_data != "").first()
            og_json = json.loads(parent_session.json_data)
        else:
            og_json = json.loads(session.json_data)

        userdeck = models.UserDeck.query.filter_by(user_id = current_user.id, video_id=session.video_id).first()      
        json_data = request.get_json()
        if json_data:
            edited = False
            if userdeck: #overwrite non-matching entries if entry already exists
                #check if cards have been edited
                print(len(og_json))
                print(len(json_data))
                if len(og_json) == len(json_data):
                    for i in range(len(og_json)):
                        if og_json[i]["answer"] != json_data[i]["answer"] or og_json[i]["question"] != json_data[i]["question"]:
                            edited = True
                            break
                else:
                    edited = True
                for card in userdeck.cards:
                    models.db.session.delete(card)
                for card in json_data:
                    models.add_usercard(userdeck.id, card["answer"], card["question"])
                models.db.session.commit()
            else:
                deck_id = models.add_userdeck(current_user.id,session.video_id)
                for card in json_data:
                    models.add_usercard(deck_id, card["answer"], card["question"])
            #save analytics data
            session.export_option = "save"
            session.edited = edited
            if edited: session.export_json = json_data 
            models.db.session.commit()      
            return json.dumps({'success':True}), 200, {'ContentType':'application/json'} 
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
            return render_template(
                'flashcards_user.html',
                cards = userdeck.cards,
                title = userdeck.video.title,
                channel = userdeck.video.channel,
            )
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

@app.route("/study/<id>", methods=['GET'])
@login_required
def study_deck(id):
    return render_template("study.html", deck_id = id,)

@app.route("/study")
@is_verified
@login_required
def study_all():
    starting_card = models.UserCard.query.join(models.UserCard.deck).filter(models.UserDeck.user_id == current_user.id, models.UserCard.due_date <= datetime.datetime.now()).first()
    if starting_card:
        return render_template("study.html", starting_card_id=starting_card.id)
    else:
        return render_template("study.html", starting_card_id=-1)

@app.route("/review/<rating>/<card_id>")
@login_required
def review_and_serve_next_card(rating, card_id):
    if int(card_id) == -1:
        return render_template(
            "fragments/alert.html",
            message = "No cards to study currently.",
            sub_message = "Give your brain a break and come back later."
        )
    
    card = models.UserCard.query.filter_by(id=card_id).first()
    rating = int(rating)

    if rating != -1:
        if card.repetitions == 0: 
            review = SMTwo.first_review(rating, datetime.datetime.now())
            card.repetitions = review.repetitions
            card.easiness = review.easiness
            card.interval = review.interval
            card.due_date = review.review_date
            card.total_repetitions += 1
            models.db.session.commit()
        else:
            review = SMTwo(card.easiness, card.interval, card.repetitions).review(rating, datetime.datetime.now())
            card.repetitions = review.repetitions
            card.easiness = review.easiness
            card.interval = review.interval 
            card.due_date = review.review_date
            card.total_repetitions += 1
            models.db.session.commit()

    new_card = models.UserCard.query.join(models.UserCard.deck).filter(models.UserDeck.user_id == current_user.id, models.UserCard.due_date <= datetime.datetime.now()).first()
    if not new_card:
        return render_template(
            "fragments/alert.html",
            message = "No cards to study currently.",
            sub_message = "Give your brain a break and come back later."
        )
    
    return render_template("fragments/study_card.html", card = new_card)

@app.route("/review_deck/<deck_id>/<index>")
@login_required
def review_card_in_deck(deck_id, index):
    deck_id = int(deck_id)
    index = int(index)
    deck = models.UserDeck.query.filter_by(user_id = current_user.id, id = deck_id).first()
    if not deck:
        return render_template("fragments/alert.html", message = "You don't have access to this deck.")
    cards = deck.cards
    if index + 1 < len(deck.cards):
        new_index = index + 1
    else:
        new_index = 0
    return render_template("fragments/study_card.html", card = cards[index], new_index = new_index, deck_id = deck_id)

@app.route("/view_card/<id>")
@login_required
def view_card(id):
    card = models.UserCard.query.filter_by(id=id).first()
    if card:
        return render_template('fragments/user_card.html', card = card)

@app.route("/delete_card/<id>", methods=['DELETE'])
@login_required
def delete_card(id):
    card = models.UserCard.query.filter_by(id=id).first()
    if card:
        models.db.session.delete(card)
        models.db.session.commit()
        return ""

@app.route("/update_card/<id>", methods=['POST'])
@login_required
def update_card(id):
    card = models.UserCard.query.filter_by(id=id).first()
    question = request.form.get("question")
    answer = request.form.get("answer")
    card.answer = answer
    card.question = question
    models.db.session.commit()
    return render_template("fragments/user_card.html", card = card)

@app.route("/create_card/<deck_id>", methods=['POST'])
@login_required
def create_card(deck_id):
    id = models.add_usercard(deck_id, "", "", 0, 0, 0)
    card = models.UserCard.query.filter_by(id=id).first()
    return render_template("fragments/user_card.html", card = card, new = True)

@app.route("/get_notification/<type>")
@login_required
def get_notification(type):
    cards = models.UserCard.query.join(models.UserCard.deck).filter(models.UserDeck.user_id == current_user.id, models.UserCard.due_date <= datetime.datetime.now()).all()
    if cards: 
        n = len(cards)
    else:
        n = 0

    if type == "count":
        return str(n) 
    if type == "message":
        return f"{n} cards pending for practice"

@app.route("/sitemap.xml")
def sitemap():
    return render_template('sitemap.xml')

@app.route("/robots.txt")
def robots():
    return render_template('robots.txt')

class CustomError(Exception):
    pass

class FlashcardError(CustomError):
    code = "403"
    description = "Flashcard Generation Error"


@app.errorhandler(CustomError)
def handle_exception(e):
    print("Custom error:", e.args[0])
    return render_template('errors/error.html', error_code = e.code, error_title = e.description, error_message = e.args[0]), e.code

@app.errorhandler(500)
def internal_server_error(e):
    return render_template('errors/error.html', error_code = "500", error_title = "server error", error_message = "Sorry, something went wrong."), 500

@app.errorhandler(404)
def page_not_found(e):
    return render_template('errors/error.html', error_code = "404", error_title = "page not found", error_message = "Sorry, the page you were trying to access doesn't exist."), 404

@app.errorhandler(400)
def page_not_found(e):
    return render_template('errors/error.html', error_code = "400", error_title = "bad request", error_message = "Sorry, we couldn't handle your request."), 400

@app.errorhandler(429)
def ratelimit_handler(e):
    return render_template('errors/error.html', error_code = "429", error_title = "too many requests", error_message = "Sorry, you have submitted too many requests. Wait a few minutes, and try again."), 429
