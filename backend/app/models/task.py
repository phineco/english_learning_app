from .. import db
import datetime

class Task(db.Model):
    __tablename__ = 'tasks'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.String(64), db.ForeignKey('users.id'), nullable=False)
    task_id = db.Column(db.String(64), unique=True, nullable=False, index=True)  # 任务唯一标识
    resource_id = db.Column(db.Integer, db.ForeignKey('uploaded_files.id'), nullable=True)  # 关联资源，可为空
    task_type = db.Column(db.String(32), nullable=False)  # 任务类型，如 'practice', 'review', 'test'
    task_plan_date = db.Column(db.DateTime, nullable=False)  # 任务计划日期
    task_finish_date = db.Column(db.DateTime, nullable=True)  # 任务完成日期，可为空
    task_status = db.Column(db.String(16), nullable=False, default='pending')  # 任务状态：pending, in_progress, completed, cancelled
    create_date = db.Column(db.DateTime, default=datetime.datetime.utcnow, nullable=False)
    update_date = db.Column(db.DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow, nullable=False)
    
    # 关系定义
    user = db.relationship('User', backref=db.backref('tasks', lazy='dynamic'))
    resource = db.relationship('UploadedFile', backref=db.backref('tasks', lazy='dynamic'))
    
    def __repr__(self):
        return f'<Task {self.task_id} by User {self.user_id}>'
    
    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'task_id': self.task_id,
            'resource_id': self.resource_id,
            'task_type': self.task_type,
            'task_plan_date': self.task_plan_date.isoformat() + 'Z' if self.task_plan_date else None,
            'task_finish_date': self.task_finish_date.isoformat() + 'Z' if self.task_finish_date else None,
            'task_status': self.task_status,
            'create_date': self.create_date.isoformat() + 'Z',
            'update_date': self.update_date.isoformat() + 'Z',
            'user_username': self.user.username if self.user else None,
            'resource_filename': self.resource.filename if self.resource else None
        }