from datetime import datetime
from flask import session
from app import db  # 假设你的 db 对象是通过 Flask-SQLAlchemy 初始化的
from sqlalchemy import event
from sqlalchemy import Column, DateTime, Float, Integer, String
from app.utils import get_current_user

class BaseModel(db.Model):
    __abstract__ = True  # 告诉 SQLAlchemy 这是一个抽象类，不会生成表格

    id = Column(Integer, primary_key=True, comment='主键')
    create_user = Column(String(255), comment='创建人')
    create_time = Column(DateTime, comment='创建时间')
    update_user = Column(String(255), comment='更新人')
    update_time = Column(DateTime, comment='更新时间')

    def to_dict(self, date_format="%Y-%m-%d %H:%M:%S"):
        """
        Convert the object to a dictionary representation, optionally format the datetime fields.
        """
        return {
            'id': self.id,
            'create_user': self.create_user,
            'create_time': self.create_time.strftime(date_format) if self.create_time else None,
            'update_user': self.update_user,
            'update_time': self.update_time.strftime(date_format) if self.update_time else None,
        }

# 监听 before_insert 事件，自动填充 create_user 和 create_time
@event.listens_for(BaseModel, 'before_insert', propagate=True)
def before_insert(mapper, connection, target):
    # 自动填充 create_user 和 create_time 字段
    if not target.create_user:
        target.create_user = get_current_user()  # 获取当前用户
    if not target.create_time:
        target.create_time = datetime.now()  # 填充当前时间

# 监听 before_update 事件，自动填充 update_user 和 update_time
@event.listens_for(BaseModel, 'before_update', propagate=True)
def before_update(mapper, connection, target):
    # 自动填充 update_user 和 update_time 字段
    target.update_user = get_current_user()  # 获取当前用户
    target.update_time = datetime.now()  # 填充当前时间
