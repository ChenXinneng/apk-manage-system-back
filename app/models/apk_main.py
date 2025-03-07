from sqlalchemy import Column, DateTime, Float, Integer, String 
from sqlalchemy.dialects.mysql import VARCHAR
from app.extensions import db
from datetime import datetime
from flask import session
from app.models.base_model import BaseModel

class ApkMain(BaseModel):
    __tablename__ = 'apk_main'

    app_name = Column(VARCHAR(255), comment='app名称')
    package_name = Column(VARCHAR(255), comment='包名')
    main_activity = Column(VARCHAR(255), comment='主活动')
    android_version = Column(String(255), comment='安卓版本')
    parse_time = Column(DateTime, comment='解析时间')
    apk_size = Column(Float(10, True), comment='apk大小(MB)')
    file_md5 = Column(String(255), comment='md5值')
    file_sha1 = Column(String(255), comment='sha1值')
    file_sha256 = Column(String(255), comment='sha256值')
    apk_location = Column(String(255), comment='apk文件路径')
    apk_download_url = Column(String(255), comment='apk下载url')

    # Optional: SQLAlchemy automatically manages `id`, `create_user`, `create_time`, `update_user`, `update_time`
    # through inheritance from BaseModel

    # Constructor can be simplified since BaseModel already manages common fields
    def __init__(self, app_name=None, package_name=None, main_activity=None, 
                 android_version=None, parse_time=None, apk_size=None, 
                 file_md5=None, file_sha1=None, file_sha256=None, 
                 apk_location=None, apk_download_url=None, **kwargs):
        super().__init__(**kwargs)  # Initialize from BaseModel (id, create_user, create_time, update_user, update_time)
        self.app_name = app_name
        self.package_name = package_name
        self.main_activity = main_activity
        self.android_version = android_version
        self.parse_time = parse_time
        self.apk_size = apk_size
        self.file_md5 = file_md5
        self.file_sha1 = file_sha1
        self.file_sha256 = file_sha256
        self.apk_location = apk_location
        self.apk_download_url = apk_download_url

    def to_dict(self, date_format="%Y-%m-%d %H:%M:%S"):
        return {
            'id': self.id,
            'app_name': self.app_name,
            'package_name': self.package_name,
            'main_activity': self.main_activity,
            'android_version': self.android_version,
            'parse_time': self.parse_time.strftime(date_format) if self.parse_time else None,
            'apk_size': self.apk_size,
            'file_md5': self.file_md5,
            'file_sha1': self.file_sha1,
            'file_sha256': self.file_sha256,
            'apk_location': self.apk_location,
            'apk_download_url': self.apk_download_url,
            'create_user': self.create_user,
            'create_time': self.create_time.strftime(date_format) if self.create_time else None,
            'update_user': self.update_user,
            'update_time': self.update_time.strftime(date_format) if self.update_time else None,
        }