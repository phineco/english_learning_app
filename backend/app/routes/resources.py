from flask import Blueprint, jsonify, send_file
from ..models import UploadedFile

bp_resources = Blueprint('resources', __name__)

@bp_resources.route('/resources', methods=['GET'])
def get_resources():
    files = UploadedFile.query.all()
    return jsonify([f.to_dict() for f in files]), 200

@bp_resources.route('/resources/<int:id>', methods=['GET'])
def get_resource(id):
    resource = UploadedFile.query.get_or_404(id)
    return jsonify(resource.to_dict()), 200


@bp_resources.route('/mp3/<filename>', methods=['GET']) 
def get_mp3(filename):
    return send_file(
        f'/Users/louisw/synology/english_learning_app/backend/uploads/{filename}',
        mimetype='audio/mpeg',
        conditional=False  # True时触发下载而非播放
    )