"""
记忆管理路由模块
提供长期记忆管理的API接口
"""
from flask import Blueprint, request, jsonify, current_app
from backend.services.ai_service import ai_service
from backend.services.validation import validate_token

# 创建蓝图
memory_bp = Blueprint('memory', __name__, url_prefix='/api/memory')

@memory_bp.route('/status', methods=['GET'])
@validate_token
def get_memory_status(current_user):
    """获取记忆服务状态"""
    return jsonify({
        'success': True,
        'short_term_memory_count': ai_service.get_memory_count(),
        'long_term_memory_enabled': ai_service.mem0_enabled
    })

@memory_bp.route('/long-term', methods=['GET'])
@validate_token
def get_long_term_memories(current_user):
    """获取用户的长期记忆"""
    username = current_user['username']
    limit = request.args.get('limit', default=10, type=int)
    
    result = ai_service.get_long_term_memories(username, limit)
    return jsonify(result)

@memory_bp.route('/long-term', methods=['DELETE'])
@validate_token
def clear_long_term_memories(current_user):
    """清除用户的长期记忆"""
    username = current_user['username']
    
    success, message = ai_service.clear_long_term_memory(username)
    return jsonify({
        'success': success,
        'message': message
    })

@memory_bp.route('/long-term/<memory_id>', methods=['PUT'])
@validate_token
def update_memory(current_user, memory_id):
    """更新特定的长期记忆"""
    data = request.get_json()
    
    if not data or 'text' not in data:
        return jsonify({
            'success': False,
            'message': '缺少必要的记忆内容'
        }), 400
    
    metadata = data.get('metadata')
    success, message = ai_service.update_long_term_memory(memory_id, data['text'], metadata)
    
    return jsonify({
        'success': success,
        'message': message
    })

@memory_bp.route('/long-term/<memory_id>', methods=['DELETE'])
@validate_token
def delete_memory(current_user, memory_id):
    """删除特定的长期记忆"""
    success, message = ai_service.delete_long_term_memory(memory_id)
    
    return jsonify({
        'success': success,
        'message': message
    })
