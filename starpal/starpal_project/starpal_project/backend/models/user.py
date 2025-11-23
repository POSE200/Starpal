"""
用户数据模型
"""
from backend.models import db
from datetime import datetime

class User(db.Model):
    """
    用户模型
    
    Attributes:
        id: 用户唯一标识
        username: 用户名（邮箱）
        password: 密码（实际项目中应加密存储）
        name: 用户显示名称
        created_at: 创建时间
        updated_at: 更新时间
    """
    
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True, comment='用户ID')
    username = db.Column(db.String(80), unique=True, nullable=False, comment='用户名')
    password = db.Column(db.String(120), nullable=False, comment='密码')
    name = db.Column(db.String(80), nullable=False, comment='显示名称')
    created_at = db.Column(db.DateTime, default=datetime.utcnow, comment='创建时间')
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, comment='更新时间')

    def __repr__(self):
        """字符串表示"""
        return f'<User {self.name}>'
    
    def to_dict(self):
        """转换为字典"""
        return {
            'id': self.id,
            'username': self.username,
            'name': self.name,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
    
    @staticmethod
    def find_by_username(username):
        """
        根据用户名查找用户
        
        Args:
            username: 用户名
            
        Returns:
            User: 用户对象或None
        """
        return User.query.filter_by(username=username).first()
    
    @staticmethod
    def create_user(username, password, name):
        """
        创建新用户
        
        Args:
            username: 用户名
            password: 密码
            name: 显示名称
            
        Returns:
            User: 新创建的用户对象
        """
        user = User(username=username, password=password, name=name)
        db.session.add(user)
        db.session.commit()
        return user
    
    def update_password(self, new_password):
        """
        更新密码
        
        Args:
            new_password: 新密码
        """
        self.password = new_password
        self.updated_at = datetime.utcnow()
        db.session.commit()
    
    def verify_password(self, password):
        """
        验证密码
        
        Args:
            password: 待验证的密码
            
        Returns:
            bool: 密码是否正确
        """
        return self.password == password
