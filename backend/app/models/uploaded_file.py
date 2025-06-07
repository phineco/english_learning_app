from .. import db
import datetime

class UploadedFile(db.Model):
    __tablename__ = 'uploaded_files'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.String(64), db.ForeignKey('users.id'), nullable=False)
    filename = db.Column(db.String(256), nullable=False)
    file_path = db.Column(db.String(512), nullable=False)
    text_content = db.Column(db.String(3000), nullable=False)
    file_type = db.Column(db.String(32), nullable=False)  # 例如 'mp3', 'txt'
    upload_time = db.Column(db.DateTime, default=datetime.datetime.now)

    user = db.relationship('User', backref=db.backref('uploaded_files', lazy='dynamic'))

    def __repr__(self):
        return f'<UploadedFile {self.id} {self.filename} by User {self.user_id}>'

    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'filename': self.filename,
            'file_path': self.file_path,
            'file_type': self.file_type,
            'text_content': self.text_content,
            'upload_time': self.upload_time,
            'user_username': self.user.username if self.user else None
        }