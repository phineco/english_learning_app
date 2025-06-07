from datetime import datetime, date, time
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.models.task_item import TaskItem
from app.models.task import Task
from app.models.uploaded_file import UploadedFile
from app import db
from sqlalchemy import and_, or_

bp_task_items = Blueprint('task_items', __name__)

@bp_task_items.route('/task-items', methods=['GET'])
@jwt_required()
def get_task_items():
    """获取当前用户的所有任务项"""
    current_user_id = get_jwt_identity()
    
    # 获取查询参数
    task_id = request.args.get('task_id', type=str)  # 按主任务ID筛选
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)
    
    # 构建查询
    query = TaskItem.query.filter_by(user_id=current_user_id)
    
    if task_id:
        query = query.filter_by(task_id=task_id)
    
    # 按创建时间倒序排列
    query = query.order_by(TaskItem.create_date.desc())
    
    # 分页
    task_items = query.paginate(
        page=page, per_page=per_page, error_out=False
    )
    
    return jsonify({
        'task_items': [item.to_dict() for item in task_items.items],
        'total': task_items.total,
        'pages': task_items.pages,
        'current_page': page
    }), 200

@bp_task_items.route('/task-items/uncompleted', methods=['GET'])
@jwt_required()
def get_uncompleted_task_items():
    """获取截至今日未完成的跟读任务列表"""
    current_user_id = get_jwt_identity()
    
    # 获取今日23:59:59的时间戳
    today = date.today()
    today_end = datetime.combine(today, time(23, 59, 59))
    
    # 查询条件：结束时间和分数都为空（未完成），并且plan_time在今日23:59:59以前
    query = TaskItem.query.filter(
        TaskItem.user_id == current_user_id,
        TaskItem.end_time.is_(None),
        TaskItem.score.is_(None),
        TaskItem.plan_time < today_end
    ).order_by(TaskItem.plan_time.desc())
    
    task_items = query.all()
    
    # 获取关联的资源信息
    result = []
    for item in task_items:
        item_dict = item.to_dict()
        # 获取关联的资源信息
        if item.resource_id:
            resource = UploadedFile.query.get(item.resource_id)
            if resource:
                item_dict['resource_name'] = resource.filename
        result.append(item_dict)
    
    return jsonify({
        'task_items': result,
        'total': len(result)
    }), 200

@bp_task_items.route('/task-items/<int:item_id>', methods=['GET'])
@jwt_required()
def get_task_item(item_id):
    """获取指定任务项详情"""
    current_user_id = get_jwt_identity()
    
    task_item = TaskItem.query.filter_by(
        id=item_id, 
        user_id=current_user_id
    ).first()
    
    if not task_item:
        return jsonify({'error': '任务项不存在'}), 404
    
    return jsonify(task_item.to_dict()), 200

@bp_task_items.route('/task-items', methods=['POST'])
@jwt_required()
def create_task_item():
    """创建新的任务项"""
    current_user_id = get_jwt_identity()
    data = request.get_json()
    
    # 验证必需字段
    if not data.get('task_id'):
        return jsonify({'error': '任务ID不能为空'}), 400
    
    # 验证任务是否存在且属于当前用户
    task = Task.query.filter_by(
        id=data['task_id'],
        user_id=current_user_id
    ).first()
    
    if not task:
        return jsonify({'error': '任务不存在或无权限'}), 404
    
    # 创建任务项
    task_item = TaskItem(
        user_id=current_user_id,
        task_id=data['task_id'],
        resource_id=data.get('resource_id'),
        begin_time=datetime.datetime.fromisoformat(data['begin_time'].replace('Z', '+00:00')) if data.get('begin_time') else None,
        end_time=datetime.datetime.fromisoformat(data['end_time'].replace('Z', '+00:00')) if data.get('end_time') else None,
        score=data.get('score')
    )
    
    try:
        db.session.add(task_item)
        db.session.commit()
        return jsonify(task_item.to_dict()), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': '创建任务项失败'}), 500

@bp_task_items.route('/task-items/<int:item_id>', methods=['PUT'])
@jwt_required()
def update_task_item(item_id):
    """更新任务项"""
    current_user_id = get_jwt_identity()
    data = request.get_json()
    
    task_item = TaskItem.query.filter_by(
        id=item_id,
        user_id=current_user_id
    ).first()
    
    if not task_item:
        return jsonify({'error': '任务项不存在'}), 404
    
    # 记录原始score值，用于判断是否需要更新finished_task_num
    original_score = task_item.score
    
    # 更新字段
    if 'resource_id' in data:
        task_item.resource_id = data['resource_id']
    if 'begin_time' in data:
        task_item.begin_time = datetime.datetime.fromisoformat(data['begin_time'].replace('Z', '+00:00')) if data['begin_time'] else None
    if 'end_time' in data:
        task_item.end_time = datetime.datetime.fromisoformat(data['end_time'].replace('Z', '+00:00')) if data['end_time'] else None
    if 'score' in data:
        task_item.score = data['score']
        
        # 如果score从None变为有值，说明任务完成了，需要增加finished_task_num
        if original_score is None and data['score'] is not None:
            task = task_item.task
            if task:
                task.finished_task_num += 1
    
    try:
        db.session.commit()
        return jsonify(task_item.to_dict()), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': '更新任务项失败'}), 500

@bp_task_items.route('/task-items/<int:item_id>', methods=['DELETE'])
@jwt_required()
def delete_task_item(item_id):
    """删除任务项"""
    current_user_id = get_jwt_identity()
    
    task_item = TaskItem.query.filter_by(
        id=item_id,
        user_id=current_user_id
    ).first()
    
    if not task_item:
        return jsonify({'error': '任务项不存在'}), 404
    
    try:
        db.session.delete(task_item)
        db.session.commit()
        return jsonify({'message': '任务项删除成功'}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': '删除任务项失败'}), 500

@bp_task_items.route('/tasks/<string:task_id>/items', methods=['GET'])
@jwt_required()
def get_task_items_by_task(task_id):
    """获取指定任务下的所有任务项"""
    current_user_id = get_jwt_identity()
    
    # 验证任务是否存在且属于当前用户
    task = Task.query.filter_by(
        id=task_id,
        user_id=current_user_id
    ).first()
    
    if not task:
        return jsonify({'error': '任务不存在或无权限'}), 404
    
    # 获取查询参数
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)
    
    # 查询任务项
    task_items = TaskItem.query.filter_by(
        task_id=task_id,
        user_id=current_user_id
    ).order_by(TaskItem.plan_time.asc()).paginate(
        page=page, per_page=per_page, error_out=False
    )
    
    return jsonify({
        'task_items': [item.to_dict() for item in task_items.items],
        'total': task_items.total,
        'pages': task_items.pages,
        'current_page': page,
        'task': task.to_dict()
    }), 200