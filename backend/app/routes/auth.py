from flask import Blueprint, request, jsonify
from ..models import User
from .. import db
from flask_jwt_extended import create_access_token, create_refresh_token, jwt_required, get_jwt_identity
import uuid

bp_auth = Blueprint('auth', __name__)
@bp_auth.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    if not data or not data.get('username') or not data.get('email') or not data.get('password'):
        return jsonify({'message': 'Missing username, email, or password'}), 400

    if User.query.filter_by(username=data['username']).first():
        return jsonify({'message': 'Username already exists'}), 400
    if User.query.filter_by(email=data['email']).first():
        return jsonify({'message': 'Email already registered'}), 400

    user = User(id=str(uuid.uuid4()), username=data['username'], email=data['email'])
    user.set_password(data['password'])
    db.session.add(user)
    db.session.commit()
    return jsonify({'message': 'User registered successfully', 'user': user.to_dict()}), 201

@bp_auth.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    if not data or not data.get('username') or not data.get('password'):
        return jsonify({'message': 'Missing username or password'}), 400

    user = User.query.filter_by(username=data['username']).first()
    if user is None or not user.check_password(data['password']):
        return jsonify({'message': 'Invalid username or password'}), 401

    access_token = create_access_token(identity=user.id)
    refresh_token = create_refresh_token(identity=user.id)
    return jsonify(access_token=access_token, refresh_token=refresh_token, user=user.to_dict()), 200

@bp_auth.route('/profile', methods=['GET'])
@jwt_required()
def profile():
    current_user_id = get_jwt_identity()
    user = User.query.get(current_user_id)
    if not user:
        return jsonify({'message': 'User not found'}), 404
    return jsonify(user.to_dict())

# 刷新令牌路由 - 使用刷新令牌获取新的访问令牌
@bp_auth.route("/refresh", methods=["POST"])
@jwt_required(refresh=True)  # 需要有效的刷新令牌
def refresh():
    identity = get_jwt_identity()
    # 创建新的访问令牌（使用原用户名）
    access_token = create_access_token(identity=identity)
    return jsonify({"access_token": access_token}), 200