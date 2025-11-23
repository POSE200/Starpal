"""
聊天相关路由
包括AI对话功能
"""
from flask import Blueprint, request, Response
from backend.services.ai_service import ai_service
from backend.services.validation import validate_request_data

# 创建蓝图
chat_bp = Blueprint('chat', __name__, url_prefix='/api')

@chat_bp.route('/chat', methods=['POST'])
def chat():
    """
    AI聊天接口（流式响应）
    
    请求参数:
        message: 用户消息
        username: 用户名
        chat_id: 对话ID
        system_prompt: (可选) 系统提示词
        
    返回:
        流式响应，Server-Sent Events格式
    """
    try:
        data = request.get_json()
        
        # 验证请求数据
        is_valid, error_msg = validate_request_data(data, ['message', 'username', 'chat_id'])
        if not is_valid:
            return Response(
                f"data: {{'error': '{error_msg}'}}\n\n",
                mimetype='text/event-stream'
            ), 400

        message = data['message'].strip()
        username = data['username'].strip()
        chat_id = data['chat_id'].strip()
        
        # 获取可选的系统提示词
        system_prompt = data.get('system_prompt')
        
        # 验证消息长度
        if not message:
            return Response(
                f"data: {{'error': '消息不能为空'}}\n\n",
                mimetype='text/event-stream'
            ), 400
            
        if len(message) > 1000:
            return Response(
                f"data: {{'error': '消息长度不能超过1000个字符'}}\n\n",
                mimetype='text/event-stream'
            ), 400

        # 调用通义千问AI服务进行流式聊天
        def generate():
            """生成器函数，用于流式响应"""
            try:
                for chunk in ai_service.chat_stream(message, username, chat_id, system_prompt):
                    yield chunk
            except Exception as e:
                print(f"通义千问聊天流式响应错误: {e}")
                yield f"data: {{'error': '通义千问AI服务暂时不可用，请检查API配置或稍后重试'}}\n\n"

        return Response(generate(), mimetype='text/event-stream')

    except Exception as e:
        print(f"通义千问聊天错误: {e}")
        return Response(
            f"data: {{'error': '通义千问AI服务暂时不可用，请检查API配置或稍后重试'}}\n\n",
            mimetype='text/event-stream'
        ), 500

@chat_bp.route('/clear_memory', methods=['POST'])
def clear_memory():
    """
    清除对话记忆接口
    
    请求参数:
        username: 用户名
        chat_id: 对话ID
        
    返回:
        JSON响应
    """
    try:
        data = request.get_json()
        
        # 验证请求数据
        is_valid, error_msg = validate_request_data(data, ['username', 'chat_id'])
        if not is_valid:
            return {'message': error_msg}, 400

        username = data['username'].strip()
        chat_id = data['chat_id'].strip()
        
        # 清除对话记忆
        ai_service.clear_user_memory(username, chat_id)
        
        return {'message': '对话记忆已清除'}, 200

    except Exception as e:
        print(f"清除记忆错误: {e}")
        return {'message': '清除记忆失败，请稍后重试'}, 500

@chat_bp.route('/memory_stats', methods=['GET'])
def memory_stats():
    """
    获取内存使用统计
    
    返回:
        JSON响应包含记忆统计信息
    """
    try:
        stats = {
            'active_conversations': ai_service.get_memory_count(),
            'status': 'healthy'
        }
        return stats, 200
        
    except Exception as e:
        print(f"获取统计信息错误: {e}")
        return {'message': '获取统计信息失败'}, 500

@chat_bp.route('/set_system_prompt', methods=['POST'])
def set_system_prompt():
    """
    设置系统提示词接口
    
    请求参数:
        username: 用户名
        chat_id: 对话ID
        system_prompt: 系统提示词，如果为null则使用默认提示词
        
    返回:
        JSON响应
    """
    try:
        data = request.get_json()
        
        # 验证请求数据
        is_valid, error_msg = validate_request_data(data, ['username', 'chat_id'])
        if not is_valid:
            return {'message': error_msg}, 400

        username = data['username'].strip()
        chat_id = data['chat_id'].strip()
        system_prompt = data.get('system_prompt')  # 可以为None，表示使用默认提示词
        
        # 设置系统提示词
        ai_service.set_system_prompt(username, chat_id, system_prompt)
        
        return {'message': '系统提示词已设置', 'success': True}, 200

    except Exception as e:
        print(f"设置系统提示词错误: {e}")
        return {'message': '设置系统提示词失败，请稍后重试', 'success': False}, 500

@chat_bp.route('/get_system_prompt', methods=['POST'])
def get_system_prompt():
    """
    获取当前系统提示词接口
    
    请求参数:
        username: 用户名
        chat_id: 对话ID
        
    返回:
        JSON响应，包含当前系统提示词
    """
    try:
        data = request.get_json()
        
        # 验证请求数据
        is_valid, error_msg = validate_request_data(data, ['username', 'chat_id'])
        if not is_valid:
            return {'message': error_msg}, 400

        username = data['username'].strip()
        chat_id = data['chat_id'].strip()
        
        # 获取系统提示词
        system_prompt = ai_service.get_system_prompt(username, chat_id)
        
        return {
            'system_prompt': system_prompt,
            'success': True
        }, 200

    except Exception as e:
        print(f"获取系统提示词错误: {e}")
        return {'message': '获取系统提示词失败，请稍后重试', 'success': False}, 500
