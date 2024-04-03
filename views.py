from app import app
from flask import render_template, request, jsonify, json, abort, redirect, flash, url_for
from markupsafe import escape
import flashcard
import transcript
import utility
import models
import datetime
from flask_login import current_user, login_required
from supermemo2 import SMTwo

TOKENS_PER_CHUNK = 3900
CARDS_PER_CHUNK = 4

@app.route('/')
@app.route("/index")
def index():
    return render_template('index.html', header_color = "purple")

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
            video_match = models.Video.query.filter_by(video_id=video_id).first()
            session = models.Sessions.query.filter_by(video_id=video_id).first() 
            if video_match and session and session.difficulty == diff and session.amount == amount:
                id = models.add_session(video_id, session.json_data, session.amount, session.difficulty)
                return render_template('flashcards.html', body_tag = "show_flashcards", flashcards_dumps = session.json_data, url = video_url, title = video_match.title, channel = video_match.channel, session_id = id, header_color = "purple")
            else: #only generate new entry if video doesnt exist in db
                #transcribe video
                try:
                    video_transcript = transcript.get_transcript(video_id)
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
                models.add_video(video_id, video_info["title"], video_info["channel_title"], video_transcript)
                id = models.add_session(video_id, dict_list_json, amount, diff)
                return render_template('flashcards.html', body_tag = "show_flashcards", flashcards_dumps = dict_list_json, url = video_url, title = video_info["title"], channel = video_info["channel_title"], video_id = video_id, session_id=id, header_color = "purple")
        
    return render_template('flashcards.html', body_tag = "show_flashcards")

@app.route("/dashboard")
@login_required
def dashboard():
    # check for decks corresponding to user id 
    decks = models.UserDeck.query.filter_by(user_id=current_user.id).all()
    if decks:
        return render_template("dashboard.html", decks = decks, header_color = "purple")
    else:
        flash("No cards saved.")
        return render_template("dashboard.html", header_color = "purple")

@app.route("/save_deck/<session_id>", methods=['GET', 'POST'])
@login_required
def save_deck(session_id):

    session = models.Sessions.query.filter_by(id = session_id).first()
    if session:
        userdeck = models.UserDeck.query.filter_by(user_id = current_user.id, video_id=session.video_id).first()      
        json_data = request.get_json()
        if json_data:
            if userdeck: #overwrite non-matching entries if entry already exists
                for i in range(len(userdeck.cards)):
                    if json_data[i]["answer"] != userdeck.cards[i].answer or json_data[i]["question"] != userdeck.cards[i].question:
                        userdeck.cards[i].answer = json_data[i]["answer"]
                        userdeck.cards[i].question = json_data[i]["question"]
                models.db.session.commit()
                return redirect(url_for("dashboard"))
            else:
                deck_id = models.add_userdeck(current_user.id,session.video_id)
                for card in json_data:
                    models.add_usercard(deck_id, card["answer"], card["question"], 0, 0, 0)
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
    return render_template("study.html", deck_id = id, header_color = "purple")

@app.route("/study")
@login_required
def study_all():
    starting_card = models.UserCard.query.join(models.UserCard.deck).filter(models.UserDeck.user_id == current_user.id, models.UserCard.due_date <= datetime.datetime.now()).first()
    if starting_card:
        return render_template("study.html", starting_card_id=starting_card.id, header_color = "purple")
    else:
        return render_template("study.html", starting_card_id=-1, header_color = "purple")

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
            models.db.session.commit()
        else:
            review = SMTwo(card.easiness, card.interval, card.repetitions).review(rating, datetime.datetime.now())
            card.repetitions = review.repetitions
            card.easiness = review.easiness
            card.interval = review.interval 
            card.due_date = review.review_date
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

@app.errorhandler(500)
def internal_server_error(e):
    return render_template('errors/500.html'), 500

@app.errorhandler(404)
def page_not_found(e):
    return render_template('errors/404.html'), 404

@app.errorhandler(400)
def page_not_found(e):
    return render_template('errors/400.html'), 400