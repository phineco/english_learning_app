import tempfile
import os
from .. import db
import uuid
from ..models import UploadedFile
from ..models import User
from flask import Blueprint, request, jsonify, send_file,  current_app, send_from_directory

from werkzeug.utils import secure_filename

from funasr import AutoModel
from funasr.utils.postprocess_utils import rich_transcription_postprocess
##/Users/louisw/.cache/modelscope/hub/models/iic/SenseVoiceSmall
model_dir = "iic/SenseVoiceSmall"
model = AutoModel(
    model=model_dir,
    disable_update=True,
    vad_model="fsmn-vad",
    vad_kwargs={"max_single_segment_time": 30000},
    device="cuda:0",
)

bp_convert = Blueprint('convert', __name__)

@bp_convert.route('/text-to-speech', methods=['POST'])
def text_to_speech():
    if 'file' not in request.files:
        return jsonify({'message': '缺少txt文件'}), 400
    txt_file = request.files['file']
    if not txt_file.filename.endswith('.txt'):
        return jsonify({'message': '文件类型错误，仅支持txt'}), 400
    text = txt_file.read().decode('utf-8')
    mp3_path = tempfile.mktemp(suffix='.mp3')
    with open(mp3_path, 'wb') as f:
        f.write(b'MOCK_MP3_DATA')
    return send_file(mp3_path, as_attachment=True, download_name='output.mp3', mimetype='audio/mpeg')

@bp_convert.route('/speech-to-text', methods=['POST'])
def speech_to_text():
    user_id = request.form.get("user_id", type=int) 
    if not user_id:
        default_user = User.query.first()
        if default_user:
            user_id = default_user.id
        else:
            return jsonify({"success": False, "message": "User not found or not authenticated. Please create a user first."}), 401

    if 'file' not in request.files:
        return jsonify({'message': '缺少mp3文件'}), 400
    audio_file = request.files['file']
    if not audio_file.filename.endswith('.mp3'):
        return jsonify({'message': '文件类型错误，仅支持mp3'}), 400
    recognized_text = '模拟识别文本'

    unique_file_stem = str(uuid.uuid4())
    # Path for the original uploaded file (txt or mp3)
    stored_original_filename = f"{unique_file_stem}.mp3"
    original_save_path = os.path.join(current_app.config["UPLOAD_FOLDER"], stored_original_filename)
    
    try:
        audio_file.save(original_save_path)
    except Exception as e:
        current_app.logger.error(f"Error saving original file: {e}")
        return jsonify({"success": False, "message": f"Error saving original file: {str(e)}"}), 500


    res = model.generate(
        input=original_save_path,
        cache={},
        language="auto",  # "zn", "en", "yue", "ja", "ko", "nospeech"
        use_itn=True,
        batch_size_s=60,
        merge_vad=True,  #
        merge_length_s=15,
    )
    recognized_text = rich_transcription_postprocess(res[0]["text"])
    print(recognized_text)
    #mp3_path = tempfile.mktemp(suffix='.mp3')
    #with open(mp3_path, 'wb') as f:
    #    f.write(audio_file.read())

    uploaded_file = UploadedFile(user_id=user_id, filename=audio_file.filename, text_content=recognized_text, file_type='mp3', file_path=original_save_path)
    db.session.add(uploaded_file)
    db.session.commit()
    return jsonify({'text': recognized_text})

