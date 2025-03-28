import os
from datetime import timedelta
class Config:
    SECRET_KEY = os.getenv('SECRET_KEY', '12345')  # 用于JWT加密
    JWT_ACCESS_TOKEN_EXPIRES = os.getenv('JWT_ACCESS_TOKEN_EXPIRES', timedelta(hours=1))  # JWT过期时间

    MYSQL_HOST = os.getenv('MYSQL_HOST', 'localhost')
    MYSQL_USER = os.getenv('MYSQL_USER', 'root')
    MYSQL_PASSWORD = os.getenv('MYSQL_PASSWORD', 'root')
    MYSQL_DB = os.getenv('MYSQL_DB', 'apk_manage_system')

    # 设置SQLAlchemy的数据库URI
    SQLALCHEMY_DATABASE_URI = f"mysql+pymysql://{MYSQL_USER}:{MYSQL_PASSWORD}@{MYSQL_HOST}/{MYSQL_DB}"
    SQLALCHEMY_TRACK_MODIFICATIONS = False  # 防止SQLAlchemy发出警告

    EXCEL_UPLOAD_FOLDER = os.path.join(os.getcwd(), 'apk-manage-system-back','app','temp')  # 上传Excel文件的临时存储路径

    # 自定义参数
    # 模拟器exe路径
    EMULATOR_PATH = r"D:\MuMu Player 12\shell\MuMuPlayer.exe"
    # ADB IP端口
    ADB_IP_PORT = r"127.0.0.1:16384"
    # ADB 命令路径
    ADB_PATH = "adb"  # ADB命令路径（已配置环境变量）
