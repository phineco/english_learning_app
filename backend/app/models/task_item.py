from .. import db
import datetime

class TaskItem(db.Model):
    __tablename__ = 'task_items'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.String(64), db.ForeignKey('users.id'), nullable=False)
    task_id = db.Column(db.Integer, db.ForeignKey('tasks.id'), nullable=False)
    resource_id = db.Column(db.Integer, db.ForeignKey('uploaded_files.id'), nullable=True)
    plan_time = db.Column(db.DateTime, nullable=True)  # 计划时间
    begin_time = db.Column(db.DateTime, nullable=True)  # 开始时间
    end_time = db.Column(db.DateTime, nullable=True)    # 结束时间
    score = db.Column(db.Float, nullable=True)          # 得分
    create_date = db.Column(db.DateTime, default=datetime.datetime.now, nullable=False)
    update_date = db.Column(db.DateTime, default=datetime.datetime.now, onupdate=datetime.datetime.now, nullable=False)
    
    # 关系定义
    user = db.relationship('User', backref=db.backref('task_items', lazy='dynamic'))
    task = db.relationship('Task', backref=db.backref('task_items', lazy='dynamic'))
    resource = db.relationship('UploadedFile', backref=db.backref('task_items', lazy='dynamic'))
    
    def __repr__(self):
        return f'<TaskItem {self.id} for Task {self.task_id} by User {self.user_id}>'
    
    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'task_id': self.task_id,
            'resource_id': self.resource_id,
            'plan_time': self.plan_time if self.plan_time else None,
            'begin_time': self.begin_time if self.begin_time else None,
            'end_time': self.end_time if self.end_time else None,
            'score': self.score,
            'create_date': self.create_date,
            'update_date': self.update_date,
            'user_username': self.user.username if self.user else None,
            #'task_task_id': self.task.id if self.task else None,
            'resource_filename': self.resource.filename if self.resource else None
        }