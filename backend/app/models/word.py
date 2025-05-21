from .. import db
import datetime

class Word(db.Model):
    __tablename__ = 'words'
    id = db.Column(db.Integer, primary_key=True)
    text = db.Column(db.String(255), nullable=False, index=True)
    phonetic_symbol = db.Column(db.String(255))
    definition = db.Column(db.Text)
    example_sentence = db.Column(db.Text)
    audio_url = db.Column(db.String(512)) # URL to a standard pronunciation audio
    difficulty_level = db.Column(db.Integer, default=1) # e.g., 1-5
    created_at = db.Column(db.DateTime, default=datetime.datetime.utcnow)

    # recordings = db.relationship('Recording', backref='word', lazy='dynamic')

    def __repr__(self):
        return f'<Word {self.text}>'

    def to_dict(self):
        return {
            'id': self.id,
            'text': self.text,
            'phonetic_symbol': self.phonetic_symbol,
            'definition': self.definition,
            'example_sentence': self.example_sentence,
            'audio_url': self.audio_url,
            'difficulty_level': self.difficulty_level,
            'created_at': self.created_at.isoformat() + 'Z'
        }