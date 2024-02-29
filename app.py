from flask import Flask, render_template, request, jsonify
from markupsafe import escape
import flashcard
import transcript

TOKENS_PER_CHUNK = 3900
app = Flask(__name__)

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

#generate and serve flashcards for given video
@app.route("/<video_id>")
def serve_flashcards_id(video_id, tokens_per_chunk = TOKENS_PER_CHUNK):
    video_transcript = transcript.get_transcript(escape(video_id))
    flashcards = flashcard.generate_flashcards(flashcard.split_text(video_transcript, tokens_per_chunk), 4)
    dict_list = [flashcard.return_dict() for flashcard in flashcards]
    return jsonify(dict_list)
