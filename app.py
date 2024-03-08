from flask import Flask, render_template, request, jsonify, json
from markupsafe import escape
import flashcard
import transcript
import utility

TOKENS_PER_CHUNK = 3900
CARDS_PER_CHUNK = 4
app = Flask(__name__)

@app.route('/')
@app.route("/index")
def index():
    return render_template('index.html', body_tag = "index")

@app.route("/flashcards", methods =["GET", "POST"])
def flashcards():
    if request.method == "POST":
        video_url = request.form.get("video-url")
        amount = str(request.form.get("amount"))
        diff = str(request.form.get("difficulty"))
        print(f"Hello my dear friend {diff}, {utility.evaluate_select(diff, ['low', 'medium', 'high'])}")

        if video_url != None:
            video_id = video_url.split("v=", 1)[1]
            video_transcript = transcript.get_transcript(escape(video_id))
            flashcards = flashcard.generate_flashcards(flashcard.split_text(video_transcript, TOKENS_PER_CHUNK), CARDS_PER_CHUNK * utility.evaluate_select(amount, ["low", "medium", "high"]), difficulty=utility.evaluate_select(diff, ["low", "medium", "high"], 2))
            dict_list = [flashcard.return_dict() for flashcard in flashcards]
            return render_template('flashcards.html', body_tag = "show_flashcards", flashcards_dumps = json.dumps(dict_list), n_cards = len(dict_list), url = video_url)
        
    return render_template('flashcards.html', body_tag = "show_flashcards")

#generate and serve flashcards for given video
@app.route("/watch", methods=["GET"])
def serve_flashcards(tokens_per_chunk = TOKENS_PER_CHUNK):
    video_id = request.args.get('v', None)
    if video_id != None:
        video_transcript = transcript.get_transcript(escape(video_id))
        flashcards = flashcard.generate_flashcards(flashcard.split_text(video_transcript, tokens_per_chunk), 4)
        dict_list = [flashcard.return_dict() for flashcard in flashcards]
        return jsonify(dict_list)
    else: 
        return "Wrong URL"
