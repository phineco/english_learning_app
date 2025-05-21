from flask import Blueprint, request, jsonify
from ..models import Word
from .. import db

bp_words = Blueprint('words', __name__)

@bp_words.route('/', methods=['GET'])
def get_words():
    # Add pagination and filtering later
    words = Word.query.all()
    return jsonify([word.to_dict() for word in words]), 200

@bp_words.route('/<int:word_id>', methods=['GET'])
def get_word(word_id):
    word = Word.query.get_or_404(word_id)
    return jsonify(word.to_dict()), 200

@bp_words.route('/', methods=['POST'])
def create_word():
    data = request.get_json()
    if not data or not data.get('text'):
        return jsonify({'message': 'Missing word text'}), 400

    # Add more validation as needed
    word = Word(
        text=data['text'],
        phonetic_symbol=data.get('phonetic_symbol'),
        definition=data.get('definition'),
        example_sentence=data.get('example_sentence'),
        audio_url=data.get('audio_url'),
        difficulty_level=data.get('difficulty_level', 1)
    )
    db.session.add(word)
    db.session.commit()
    return jsonify({'message': 'Word created successfully', 'word': word.to_dict()}), 201

# Add PUT and DELETE endpoints as needed