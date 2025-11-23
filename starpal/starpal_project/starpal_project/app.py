"""
StarPal AI聊天应用主文件
重构后的模块化版本
"""
import os
import pymysql
from flask import Flask
from flask_cors import CORS

from backend.config.config import config
from backend.models import init_db
from backend.routes.auth import auth_bp
from backend.routes.chat import chat_bp
from backend.routes.memory import memory_bp

# 加载 PyMySQL 驱动
pymysql.install_as_MySQLdb()

def create_app(config_name=None):
    """
    应用工厂函数
    
    Args:
        config_name: 配置名称 ('development', 'production')
        
    Returns:
        Flask: 配置好的Flask应用实例
    """
    
    # 创建Flask应用
    app = Flask(__name__, static_folder='static')
    
    # 加载配置
    if config_name is None:
        config_name = os.environ.get('FLASK_ENV', 'default')
    
    app.config.from_object(config[config_name])
    
    # 启用CORS支持
    CORS(app)
    
    # 初始化数据库
    init_db(app)
    
    # 注册蓝图（路由模块）
    app.register_blueprint(auth_bp)
    app.register_blueprint(chat_bp)
    app.register_blueprint(memory_bp)
    
    # 注册错误处理器
    register_error_handlers(app)
    
    # 健康检查路由
    @app.route('/health')
    def health_check():
        """健康检查接口"""
        return {'status': 'healthy', 'service': 'StarPal AI Chat'}, 200
    
    return app

def register_error_handlers(app):
    """
    注册全局错误处理器
    
    Args:
        app: Flask应用实例
    """
    
    @app.errorhandler(404)
    def not_found(error):
        """404错误处理"""
        return {'message': '请求的资源不存在'}, 404
    
    @app.errorhandler(500)
    def internal_error(error):
        """500错误处理"""
        return {'message': '服务器内部错误'}, 500
    
    @app.errorhandler(400)
    def bad_request(error):
        """400错误处理"""
        return {'message': '请求参数错误'}, 400

if __name__ == '__main__':
    # 创建应用实例
    app = create_app()
    
    # 获取配置
    port = app.config.get('PORT', 5000)
    debug = app.config.get('DEBUG', False)
    
    print(f"StarPal AI Chat 服务启动中...")
    print(f"访问地址: http://localhost:{port}")
    print(f"调试模式: {'开启' if debug else '关闭'}")
    
    # 运行应用
    app.run(debug=debug, port=port, host='0.0.0.0')
