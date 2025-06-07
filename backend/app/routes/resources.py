import os
from flask import Blueprint, jsonify, send_file, current_app, request
from ..models import UploadedFile
from flask_jwt_extended import jwt_required
from .. import db

bp_resources = Blueprint('resources', __name__)

@bp_resources.route('/resources', methods=['GET'])
@jwt_required()
def get_resources():
    files = UploadedFile.query.all()
    return jsonify([f.to_dict() for f in files]), 200

@bp_resources.route('/resources/<int:id>', methods=['GET'])
@jwt_required()
def get_resource(id):
    resource = UploadedFile.query.get_or_404(id)
    return jsonify(resource.to_dict()), 200

@bp_resources.route('/resources/<int:id>', methods=['PUT'])
@jwt_required()
def update_resource(id):
    resource = UploadedFile.query.get_or_404(id)
    data = request.get_json()
    
    if 'text_content' in data:
        resource.text_content = data['text_content']
        
    try:
        db.session.commit()
        return jsonify(resource.to_dict()), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


@bp_resources.route('/mp3/<filename>', methods=['GET']) 
@jwt_required()
def get_mp3(filename):
    saved_path = os.path.join(current_app.config["UPLOAD_FOLDER"], filename)
    return send_file(
        saved_path,
        mimetype='audio/mpeg',
        conditional=False  # True时触发下载而非播放
    )