from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from .. import db
from ..models.task import Task
from ..models.user import User
from ..models.uploaded_file import UploadedFile
from ..models.task_item import TaskItem
import datetime
import uuid

bp_tasks = Blueprint('tasks', __name__)

@bp_tasks.route('/tasks', methods=['GET'])
@jwt_required()
def get_tasks():
    """获取当前用户的所有任务"""
    current_user_id = get_jwt_identity()
    
    # 获取查询参数
    task_status = request.args.get('status')  # 按状态筛选
    task_type = request.args.get('type')      # 按类型筛选
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)
    
    # 构建查询
    query = Task.query.filter_by(user_id=current_user_id)
    
    if task_status:
        query = query.filter_by(task_status=task_status)
    if task_type:
        query = query.filter_by(task_type=task_type)
    
    # 按创建时间倒序排列
    query = query.order_by(Task.create_date.desc())
    
    # 分页
    tasks = query.paginate(
        page=page, per_page=per_page, error_out=False
    )
    
    return jsonify({
        'tasks': [task.to_dict() for task in tasks.items],
        'total': tasks.total,
        'pages': tasks.pages,
        'current_page': page
    }), 200

@bp_tasks.route('/tasks/<int:task_id>', methods=['GET'])
@jwt_required()
def get_task(task_id):
    """获取指定任务详情"""
    current_user_id = get_jwt_identity()
    
    task = Task.query.filter_by(id=task_id, user_id=current_user_id).first()
    if not task:
        return jsonify({'error': '任务不存在'}), 404
    
    return jsonify(task.to_dict()), 200

@bp_tasks.route('/tasks', methods=['POST'])
@jwt_required()
def create_task():
    """创建新任务"""
    current_user_id = get_jwt_identity()
    data = request.get_json()
    
    # 验证必需字段
    required_fields = ['task_type', 'task_plan_date']
    for field in required_fields:
        if field not in data:
            return jsonify({'error': f'缺少必需字段: {field}'}), 400
    
    # 验证任务类型
    valid_task_types = ['practice', 'review', 'test', 'homework', 'exam']
    if data['task_type'] not in valid_task_types:
        return jsonify({'error': f'无效的任务类型，支持的类型: {", ".join(valid_task_types)}'}), 400
    
    # 验证任务状态
    task_status = data.get('task_status', 'pending')
    valid_statuses = ['pending', 'in_progress', 'completed', 'cancelled']
    if task_status not in valid_statuses:
        return jsonify({'error': f'无效的任务状态，支持的状态: {", ".join(valid_statuses)}'}), 400
    
    # 验证资源ID（如果提供）
    resource_id = data.get('resource_id')
    if resource_id:
        resource = UploadedFile.query.get(resource_id)
        if not resource:
            return jsonify({'error': '指定的资源不存在'}), 400
    
    try:
        # 解析计划日期
        task_plan_date = datetime.datetime.fromisoformat(data['task_plan_date'].replace('Z', '+00:00'))
        
        # 解析完成日期（如果提供）
        task_finish_date = None
        if data.get('task_finish_date'):
            task_finish_date = datetime.datetime.fromisoformat(data['task_finish_date'].replace('Z', '+00:00'))
        
        # 生成唯一任务ID
        task_id = str(uuid.uuid4())
        
        # 创建任务
        task = Task(
            user_id=current_user_id,
            id=task_id,
            resource_id=resource_id,
            cycle_type=data['cycle_type'],
            week_days=data['week_days'],
            task_type=data['task_type'],
            task_plan_date=task_plan_date,
            task_finish_date=task_finish_date,
            task_status=task_status
        )
        
        
        # 根据cycle_type创建task_item
        task_num = create_task_items_by_cycle(task, data['cycle_type'], data.get('week_days', ''), task_plan_date, task_finish_date)
        task.task_num = task_num
        db.session.add(task)
        db.session.commit()
        
        return jsonify(task.to_dict()), 201
        
    except ValueError as e:
        return jsonify({'error': f'日期格式错误: {str(e)}'}), 400
    except Exception as e:
        db.session.rollback()
        print(e)
        return jsonify({'error': f'批量删除任务失败: {str(e)}'}), 500


def create_task_items_by_cycle(task, cycle_type, week_days, start_date, end_date=None) -> int:
    """根据周期类型创建任务项"""
    from datetime import datetime, timedelta
    
    task_items_count = 0  # 统计创建的任务项数量
    
    if cycle_type == 'daily':
        # 每日任务：在开始日期和结束日期范围内创建任务项
        current_date = start_date
        while end_date is None or current_date <= end_date:
            task_item = TaskItem(
                user_id=task.user_id,
                task_id=task.id,
                resource_id=task.resource_id,
                plan_time=current_date,
                end_time=None,
                score=None
            )
            db.session.add(task_item)
            task_items_count += 1
            current_date += timedelta(days=1)
            
            # 如果没有结束日期，默认创建30天
            if end_date is None and current_date > start_date + timedelta(days=29):
                break
    
    elif cycle_type == 'weekly' and week_days:
        # 每周任务：根据指定的星期几在日期范围内创建任务项
        try:
            week_day_list = [int(day.strip()) for day in week_days.split(',') if day.strip().isdigit()]
        except:
            week_day_list = []
        
        if week_day_list:
            current_date = start_date
            week = 0
            
            while True:
                week_has_items = False
                for week_day in week_day_list:
                    # 计算该周的指定星期几
                    days_ahead = week_day - current_date.weekday()
                    if days_ahead < 0:  # 如果已经过了这个星期几
                        days_ahead += 7
                    
                    item_date = current_date + timedelta(days=days_ahead + week * 7)
                    
                    # 检查是否在结束日期范围内
                    if end_date is None or item_date <= end_date:
                        task_item = TaskItem(
                            user_id=task.user_id,
                            task_id=task.id,
                            resource_id=task.resource_id,
                            plan_time=item_date,
                            end_time=None,
                            score=None
                        )
                        db.session.add(task_item)
                        task_items_count += 1
                        week_has_items = True
                
                week += 1
                
                # 如果没有结束日期，默认创建12周
                if end_date is None and week >= 12:
                    break
                # 如果有结束日期且这周没有创建任何项目，说明已经超出范围
                elif end_date is not None and not week_has_items:
                    break
    
    elif cycle_type == 'once':
        # 一次性任务：只创建一个任务项
        task_item = TaskItem(
            user_id=task.user_id,
            task_id=task.id,
            resource_id=task.resource_id,
            plan_time=datetime.datetime.now(),
            begin_time=None,
            end_time=None,
            score=None
        )
        db.session.add(task_item)
        task_items_count += 1
    return task_items_count

@bp_tasks.route('/tasks/<int:task_id>', methods=['PUT'])
@jwt_required()
def update_task(task_id):
    """更新任务"""
    current_user_id = get_jwt_identity()
    data = request.get_json()
    
    task = Task.query.filter_by(id=task_id, user_id=current_user_id).first()
    if not task:
        return jsonify({'error': '任务不存在'}), 404
    
    try:
        # 更新字段
        if 'task_type' in data:
            valid_task_types = ['practice', 'review', 'test', 'homework', 'exam']
            if data['task_type'] not in valid_task_types:
                return jsonify({'error': f'无效的任务类型，支持的类型: {", ".join(valid_task_types)}'}), 400
            task.task_type = data['task_type']
        
        if 'task_status' in data:
            valid_statuses = ['pending', 'in_progress', 'completed', 'cancelled']
            if data['task_status'] not in valid_statuses:
                return jsonify({'error': f'无效的任务状态，支持的状态: {", ".join(valid_statuses)}'}), 400
            task.task_status = data['task_status']
            
            # 如果状态改为completed，自动设置完成时间
            if data['task_status'] == 'completed' and not task.task_finish_date:
                task.task_finish_date = datetime.datetime.now()
        
        if 'resource_id' in data:
            if data['resource_id']:
                resource = UploadedFile.query.get(data['resource_id'])
                if not resource:
                    return jsonify({'error': '指定的资源不存在'}), 400
            task.resource_id = data['resource_id']
        
        if 'task_plan_date' in data:
            task.task_plan_date = datetime.datetime.fromisoformat(data['task_plan_date'].replace('Z', '+00:00'))
        
        if 'task_finish_date' in data:
            if data['task_finish_date']:
                task.task_finish_date = datetime.datetime.fromisoformat(data['task_finish_date'].replace('Z', '+00:00'))
            else:
                task.task_finish_date = None
        
        # 更新时间自动更新
        task.update_date = datetime.datetime.now()
        
        db.session.commit()
        
        return jsonify(task.to_dict()), 200
        
    except ValueError as e:
        return jsonify({'error': f'日期格式错误: {str(e)}'}), 400
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'更新任务失败: {str(e)}'}), 500

@bp_tasks.route('/tasks/<int:task_id>', methods=['DELETE'])
@jwt_required()
def delete_task(task_id):
    """删除任务"""
    current_user_id = get_jwt_identity()
    
    task = Task.query.filter_by(id=task_id, user_id=current_user_id).first()
    if not task:
        return jsonify({'error': '任务不存在'}), 404
    
    try:
        db.session.delete(task)
        db.session.commit()
        
        return jsonify({'message': '任务删除成功'}), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'删除任务失败: {str(e)}'}), 500

@bp_tasks.route('/tasks/batch', methods=['DELETE'])
@jwt_required()
def batch_delete_tasks():
    """批量删除任务"""
    current_user_id = get_jwt_identity()
    data = request.get_json()
    
    if 'task_ids' not in data or not isinstance(data['task_ids'], list):
        return jsonify({'error': '请提供要删除的任务ID列表'}), 400
    
    try:
        # 查找属于当前用户的任务
        tasks = Task.query.filter(
            Task.id.in_(data['task_ids']),
            Task.user_id == current_user_id
        ).all()
        
        if not tasks:
            return jsonify({'error': '没有找到可删除的任务'}), 404
        
        deleted_count = len(tasks)
        
        for task in tasks:
            db.session.delete(task)
        
        db.session.commit()
        
        return jsonify({
            'message': f'成功删除 {deleted_count} 个任务',
            'deleted_count': deleted_count
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'批量删除任务失败: {str(e)}'}), 500

@bp_tasks.route('/tasks/stats', methods=['GET'])
@jwt_required()
def get_task_stats():
    """获取任务统计信息"""
    current_user_id = get_jwt_identity()
    
    try:
        # 统计各状态的任务数量
        stats = {
            'total': Task.query.filter_by(user_id=current_user_id).count(),
            'pending': Task.query.filter_by(user_id=current_user_id, task_status='pending').count(),
            'in_progress': Task.query.filter_by(user_id=current_user_id, task_status='in_progress').count(),
            'completed': Task.query.filter_by(user_id=current_user_id, task_status='completed').count(),
            'cancelled': Task.query.filter_by(user_id=current_user_id, task_status='cancelled').count()
        }
        
        # 统计各类型的任务数量
        type_stats = {}
        task_types = ['practice', 'review', 'test', 'homework', 'exam']
        for task_type in task_types:
            type_stats[task_type] = Task.query.filter_by(
                user_id=current_user_id, 
                task_type=task_type
            ).count()
        
        stats['by_type'] = type_stats
        
        return jsonify(stats), 200
        
    except Exception as e:
        return jsonify({'error': f'获取统计信息失败: {str(e)}'}), 500
    