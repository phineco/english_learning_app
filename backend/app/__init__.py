import os
import sys
from datetime import timedelta
# DON'T CHANGE THIS !!!
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from flask import Flask, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_jwt_extended import JWTManager, jwt_required
from .config import Config

db = SQLAlchemy()
migrate = Migrate()

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    db.init_app(app)

    # Configure upload folder
    UPLOAD_FOLDER = os.path.join(os.getcwd(), 'uploads') 
    app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
    TTS_AUDIO_FOLDER = os.path.join(UPLOAD_FOLDER, 'tts_audio') # Folder for TTS generated audio
    app.config['TTS_AUDIO_FOLDER'] = TTS_AUDIO_FOLDER

    app.config['JWT_SECRET_KEY'] = 'sdfsa8e@@ERRWSDXC12SZa'
    app.config["JWT_ACCESS_TOKEN_EXPIRES"] = timedelta(minutes=20)  # 访问令牌过期时间
    app.config["JWT_REFRESH_TOKEN_EXPIRES"] = timedelta(days=30)    # 刷新令牌过期时间
    app.config["JWT_TOKEN_LOCATION"] = ["headers", "cookies"]  # 支持 header 和 cookie

    if not os.path.exists(UPLOAD_FOLDER):
        os.makedirs(UPLOAD_FOLDER)
    if not os.path.exists(TTS_AUDIO_FOLDER):
        os.makedirs(TTS_AUDIO_FOLDER)
    if not os.path.exists(os.path.join(UPLOAD_FOLDER, 'user_recordings')):
        os.makedirs(os.path.join(UPLOAD_FOLDER, 'user_recordings'))

    migrate.init_app(app, db)
    jwt = JWTManager(app) # Initialize JWTManager

    # 注册蓝本
    from .routes.auth import bp_auth
    from .routes.words import bp_words
    from .routes.records import bp_records
    from .routes.convert import bp_convert
    from .routes.resources import bp_resources
    from .routes.tasks  import bp_tasks

    app.register_blueprint(bp_auth, url_prefix='/auth')
    app.register_blueprint(bp_words, url_prefix='/words')
    app.register_blueprint(bp_records, url_prefix='/records')
    app.register_blueprint(bp_convert, url_prefix='/convert')
    app.register_blueprint(bp_tasks)
    app.register_blueprint(bp_resources)

    with app.app_context():  # 必须使用应用上下文[5][8][9]
        db.create_all()  # 创建所有继承自db.Model的类对应的表[1][2][5]
        print("数据库表已成功创建")

    @app.route('/test')
    @jwt_required()
    def hello():
        return "Hello, English Learning App Backend!"
    # 添加 JWT 错误处理器
    @jwt.unauthorized_loader
    def missing_token_callback(error):
        print(error)
        return jsonify({"error": error}), 401  # 返回 401 代替 422
    
    # 令牌过期错误处理
    @jwt.expired_token_loader
    def expired_token_callback(jwt_header, jwt_payload):
        return jsonify({
            "msg": "Token has expired",
            "error": "token_expired"
        }), 401

    @jwt.invalid_token_loader
    def invalid_token_callback(error):
        print(error)
        return jsonify({"error": error}), 401
    
    @app.after_request
    def add_cors_headers(response):
        response.headers['Access-Control-Allow-Origin'] = 'http://localhost:5173'
        response.headers['Access-Control-Allow-Methods'] = 'OPTIONS,GET,POST,PUT,DELETE'
        response.headers['Access-Control-Allow-Headers'] = 'Content-Type,Authorization'
        return response

    return app

    