import os
from datetime import timedelta

class Config:
    # 基础配置
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev'
    
    # 时区配置
    TIMEZONE = 'Asia/Shanghai'
    
    # 数据库配置
    SQLALCHEMY_DATABASE_URI = 'sqlite:///estate.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # 文件上传配置
    UPLOAD_FOLDER = os.path.join('static', 'uploads')
    MAX_CONTENT_LENGTH = 1024 * 1024 * 1024  # 设置最大上传限制为1GB
    ALLOWED_EXTENSIONS = {'xlsx'}

    # 增加请求大小限制
    MAX_CONTENT_LENGTH = 1024 * 1024 * 1024  # 1GB
    
    # 配置服务器接收大文件
    SEND_FILE_MAX_AGE_DEFAULT = 0
    
    # 数据库配置
    SQLALCHEMY_ENGINE_OPTIONS = {
        'pool_size': 10,
        'max_overflow': 20,
        'pool_timeout': 300,
    }