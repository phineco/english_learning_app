from flask import Blueprint, request, jsonify, current_app
from ..models import Recording, User, UploadedFile
from flask import Blueprint, request, jsonify, current_app
from flask_jwt_extended import jwt_required, get_jwt_identity
from .. import db
from ..services.speech_evaluation_service import SpeechEvaluationService
import os
from werkzeug.utils import secure_filename # For handling file uploads securely

bp_records = Blueprint('records', __name__)

# Configure upload folder (example, adjust as needed)
# UPLOAD_FOLDER = os.path.join(current_app.root_path, '..', 'uploads', 'recordings')
# ALLOWED_EXTENSIONS = {'wav', 'mp3', 'm4a'}

# def allowed_file(filename):
#     return '.' in filename and \
#            filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


#@jwt_required()
@bp_records.route('/submitRecords', methods=['POST'])
def create_recording():
    #current_user_id = get_jwt_identity()
    #user_id = current_user_id # Use user_id from JWT

    data = request.form
    if 'file' not in request.files or not data.get('word_id', type=int):
        return jsonify({'message': 'Missing audio file or word_id'}), 400

    user_id = data.get("user_id", type=int) 
    if not user_id:
        default_user = User.query.first()
        if default_user:
            user_id = default_user.id
        else:
            return jsonify({"success": False, "message": "User not found or not authenticated. Please create a user first."}), 401
    
    audio_file = request.files['file']
    word_id = data.get('word_id', type=int)

    user = User.query.get(user_id)
    word = UploadedFile.query.get_or_404(word_id)

    if not user:
        print("User not found")  # Add this print statement for debug purposes
        return jsonify({'message': 'User not found'}), 404
    if not word:
        print("Word not found")
        return jsonify({'message': 'Word not found'}), 404


    filename = f"user_{user_id}_word_{word_id}_" + secure_filename(audio_file.filename) 
    upload_folder = current_app.config.get('UPLOAD_FOLDER', os.path.join(current_app.root_path, '..', 'uploads', 'recordings'))
    os.makedirs(upload_folder, exist_ok=True) # Ensure upload folder exists
    file_path = os.path.join(upload_folder, filename)

    try:
        audio_file.save(file_path)
    except Exception as e:
        current_app.logger.error(f"Error saving original file: {e}")
        return jsonify({"success": False, "message": f"Error saving original file: {str(e)}"}), 500
   
    # Initialize SpeechEvaluationService
    # In a real app, API keys or model paths might come from config
    speech_service = SpeechEvaluationService()

    # Evaluate pronunciation
    score, feedback, recognized_text = speech_service.evaluate_pronunciation(
        audio_file_path=file_path, # Pass the actual path in a real app
        reference_text=word.text_content
    )

    recording = Recording(
        user_id=user.id,
        word_id=word.id,
        audio_file_path=file_path, # Store the path to the audio file
        score=score,
        feedback=feedback,
        recognized_text=recognized_text
    )
    db.session.add(recording)
    db.session.commit()

    return jsonify({'message': 'Recording created and evaluated successfully', 'recording': recording.to_dict()}), 201
    # else:
    #     return jsonify({'message': 'File type not allowed'}), 400

@bp_records.route('/user/<int:user_id>', methods=['GET'])
def get_user_recordings(user_id):
    user = User.query.get_or_404(user_id)
    recordings = Recording.query.filter_by(user_id=user.id).order_by(Recording.created_at.desc()).all()
    return jsonify([rec.to_dict() for rec in recordings]), 200

@bp_records.route('/<int:recording_id>', methods=['GET'])
def get_recording(recording_id):
    recording = Recording.query.get_or_404(recording_id)
    return jsonify(recording.to_dict()), 200

# Add DELETE endpoint if needed