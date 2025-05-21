from .. import db
import datetime

class Recording(db.Model):
    __tablename__ = 'recordings'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    word_id = db.Column(db.Integer, db.ForeignKey('words.id'), nullable=False)
    audio_file_path = db.Column(db.String(512), nullable=False) # Path to the user's recording
    score = db.Column(db.Float) # Pronunciation score
    feedback = db.Column(db.Text) # Detailed feedback (e.g., mispronounced phonemes)
    recognized_text = db.Column(db.Text) # Text recognized from user's speech
    created_at = db.Column(db.DateTime, default=datetime.datetime.utcnow)

    user = db.relationship('User', backref=db.backref('recordings', lazy='dynamic'))
    word = db.relationship('Word', backref=db.backref('recordings', lazy='dynamic'))

    def __repr__(self):
        return f'<Recording {self.id} by User {self.user_id} for Word {self.word_id}>'

    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'word_id': self.word_id,
            'audio_file_path': self.audio_file_path,
            'score': self.score,
            'feedback': self.feedback,
            'recognized_text': self.recognized_text,
            'created_at': self.created_at.isoformat() + 'Z',
            'user_username': self.user.username if self.user else None,
            'word_text': self.word.text if self.word else None
        }