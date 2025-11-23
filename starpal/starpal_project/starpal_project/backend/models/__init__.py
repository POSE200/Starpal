"""
数据库初始化模块
"""
from flask_sqlalchemy import SQLAlchemy

# 创建数据库实例
db = SQLAlchemy()

def init_db(app):
    """
    初始化数据库
    
    Args:
        app: Flask应用实例
    """
    db.init_app(app)
    
    with app.app_context():
        # 创建所有表
        db.create_all()
        print("数据库初始化完成")
