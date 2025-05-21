import os
import sys
# DON'T CHANGE THIS !!!
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_jwt_extended import JWTManager
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
    from.routes.resources import bp_resources

    app.register_blueprint(bp_auth, url_prefix='/auth')
    app.register_blueprint(bp_words, url_prefix='/words')
    app.register_blueprint(bp_records, url_prefix='/records')
    app.register_blueprint(bp_convert, url_prefix='/convert')
    app.register_blueprint(bp_resources)

    with app.app_context():  # 必须使用应用上下文[5][8][9]
        db.create_all()  # 创建所有继承自db.Model的类对应的表[1][2][5]
        print("数据库表已成功创建")

    @app.route('/hello')
    def hello():
        return "Hello, English Learning App Backend!"

    @app.after_request
    def add_cors_headers(response):
        response.headers['Access-Control-Allow-Origin'] = 'http://127.0.0.1:5173'
        response.headers['Access-Control-Allow-Methods'] = 'GET,POST,PUT,DELETE'
        response.headers['Access-Control-Allow-Headers'] = 'Content-Type,Authorization'
        return response

    return app

    