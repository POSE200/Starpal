"""
验证工具模块
"""
import functools
from flask import request, jsonify
from backend.models.user import User

def validate_request_data(data, required_fields):
    """
    验证请求数据
    
    Args:
        data: 请求数据字典
        required_fields: 必需字段列表
        
    Returns:
        tuple: (是否有效, 错误信息)
    """
    if not data:
        return False, '请求数据为空'
    
    missing_fields = [field for field in required_fields if not data.get(field)]
    if missing_fields:
        return False, f'缺少必要信息: {", ".join(missing_fields)}'
    
    return True, None

def validate_email(email):
    """
    验证邮箱格式
    
    Args:
        email: 邮箱地址
        
    Returns:
        bool: 是否为有效邮箱
    """
    import re
    pattern = r'^[\w\.-]+@[\w\.-]+\.\w+$'
    return re.match(pattern, email) is not None

def validate_password_strength(password):
    """
    验证密码强度
    
    Args:
        password: 密码
        
    Returns:
        tuple: (是否有效, 错误信息)
    """
    if len(password) < 6:
        return False, '密码长度至少6位'
    
    if len(password) > 20:
        return False, '密码长度不能超过20位'
        
    return True, None

def validate_token(f):
    """
    验证请求中的身份令牌（Authorization Header）
    作为装饰器使用，可以验证用户是否登录并提取当前用户信息
    
    Args:
        f: 被装饰的函数
        
    Returns:
        decorated: 装饰后的函数
    """
    @functools.wraps(f)
    def decorated(*args, **kwargs):
        # 获取Authorization Header
        auth_header = request.headers.get('Authorization')
        
        # 验证header格式
        if not auth_header or not auth_header.startswith('Bearer '):
            return jsonify({
                'success': False,
                'message': '请提供有效的认证令牌'
            }), 401
        
        # 提取令牌（这里只是简单示例，实际应使用JWT等更安全的方式）
        token = auth_header.split(' ')[1]
        
        # 从令牌中提取用户名（简单示例）
        # 实际项目中应该使用JWT或其他方式解析令牌获取用户信息
        username = token  # 这里假设token就是用户名，实际项目中需要更安全的验证方式
        
        # 验证用户是否存在
        user = User.find_by_username(username)
        if not user:
            return jsonify({
                'success': False,
                'message': '无效的用户令牌'
            }), 401
        
        # 将用户信息传递给被装饰的函数
        current_user = {
            'username': user.username,
            'name': user.name
        }
        
        return f(current_user=current_user, *args, **kwargs)
    
    return decorated
