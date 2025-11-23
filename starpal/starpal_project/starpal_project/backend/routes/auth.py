"""
认证相关路由
包括用户注册、登录、修改密码等功能
"""
from flask import Blueprint, request, jsonify
from backend.models.user import User
from backend.services.validation import validate_request_data, validate_email, validate_password_strength

# 创建蓝图
auth_bp = Blueprint('auth', __name__, url_prefix='/api')

@auth_bp.route('/register', methods=['POST'])
def register():
    """
    用户注册接口
    
    请求参数:
        username: 用户名（邮箱）
        password: 密码
        name: 显示名称
        
    返回:
        JSON响应包含成功或错误信息
    """
    try:
        data = request.get_json()
        
        # 验证请求数据
        is_valid, error_msg = validate_request_data(data, ['username', 'password', 'name'])
        if not is_valid:
            return jsonify({'message': error_msg}), 400

        username = data['username'].strip()
        password = data['password']
        name = data['name'].strip()
        
        # 验证邮箱格式
        if not validate_email(username):
            return jsonify({'message': '邮箱格式不正确'}), 400
        
        # 验证密码强度
        is_valid, error_msg = validate_password_strength(password)
        if not is_valid:
            return jsonify({'message': error_msg}), 400
        
        # 验证姓名长度
        if not name or len(name) > 20:
            return jsonify({'message': '姓名不能为空且长度不超过20个字符'}), 400

        # 检查用户是否已存在
        if User.find_by_username(username):
            return jsonify({'message': '该账号已存在！'}), 400

        # 创建新用户
        User.create_user(username, password, name)
        
        return jsonify({'message': '注册成功，请登录！'}), 201

    except Exception as e:
        print(f"注册错误: {e}")
        return jsonify({'message': '注册失败，请稍后重试'}), 500

@auth_bp.route('/login', methods=['POST'])
def login():
    """
    用户登录接口
    
    请求参数:
        username: 用户名（邮箱）
        password: 密码
        
    返回:
        JSON响应包含用户信息或错误信息
    """
    try:
        data = request.get_json()
        
        # 验证请求数据
        is_valid, error_msg = validate_request_data(data, ['username', 'password'])
        if not is_valid:
            return jsonify({'message': error_msg}), 400

        username = data['username'].strip()
        password = data['password']
        
        # 查找用户
        user = User.find_by_username(username)
        if not user:
            return jsonify({'message': '用户不存在，请先注册！'}), 404

        # 验证密码
        if not user.verify_password(password):
            return jsonify({'message': '密码错误！'}), 401

        # 登录成功，返回用户信息
        return jsonify({
            'message': '登录成功',
            'username': user.username,
            'name': user.name
        }), 200

    except Exception as e:
        print(f"登录错误: {e}")
        return jsonify({'message': '登录失败，请稍后重试'}), 500

@auth_bp.route('/change_password', methods=['POST'])
def change_password():
    """
    修改密码接口
    
    请求参数:
        username: 用户名
        oldpwd: 原密码
        newpwd: 新密码
        
    返回:
        JSON响应包含成功或错误信息
    """
    try:
        data = request.get_json()
        
        # 验证请求数据
        is_valid, error_msg = validate_request_data(data, ['username', 'oldpwd', 'newpwd'])
        if not is_valid:
            return jsonify({'message': error_msg}), 400

        username = data['username'].strip()
        old_password = data['oldpwd']
        new_password = data['newpwd']
        
        # 验证新密码强度
        is_valid, error_msg = validate_password_strength(new_password)
        if not is_valid:
            return jsonify({'message': error_msg}), 400

        # 查找用户
        user = User.find_by_username(username)
        if not user:
            return jsonify({'message': '账号不存在！'}), 404

        # 验证原密码
        if not user.verify_password(old_password):
            return jsonify({'message': '原密码错误！'}), 401

        # 更新密码
        user.update_password(new_password)
        
        return jsonify({'message': '密码修改成功，请使用新密码登录！'}), 200

    except Exception as e:
        print(f"修改密码错误: {e}")
        return jsonify({'message': '修改密码失败，请稍后重试'}), 500
