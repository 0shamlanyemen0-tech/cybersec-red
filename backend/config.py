# 📁 backend/config.py
"""
إعدادات النظام المتغير
"""

import os
from dataclasses import dataclass

@dataclass
class Config:
    """إعدادات التطبيق"""
    
    # إعدادات الويب
    SECRET_KEY = os.getenv('UAMS_SECRET', 'uams_super_secret_key_2024')
    DEBUG = False
    HOST = '0.0.0.0'
    PORT = 8080
    
    # إعدادات قاعدة البيانات
    DATABASE_PATH = 'backend/database/uams.db'
    DATABASE_URI = f'sqlite:///{DATABASE_PATH}'
    
    # إعدادات C2
    C2_HOST = '0.0.0.0'
    C2_PORT = 4444
    C2_PASSWORD = 'uams_c2_password'
    
    # إعدادات التشفير
    ENCRYPTION_KEY = 'uams_encryption_key_2024'
    ENCRYPTION_METHOD = 'xor'  # xor, aes, fernet
    
    # المسارات
    PAYLOADS_DIR = 'payloads'
    GENERATED_PAGES_DIR = 'generated_pages'
    LOGS_DIR = 'logs'
    
    # السماح بعناوين IP
    ALLOWED_IPS = ['127.0.0.1', '192.168.1.0/24', '10.0.0.0/8']
    
    # الإعدادات الأمنية
    MAX_FILE_SIZE = 50 * 1024 * 1024  # 50MB
    SESSION_TIMEOUT = 3600  # 1 ساعة
    
    @classmethod
    def init_dirs(cls):
        """إنشاء المجلدات المطلوبة"""
        dirs = [cls.PAYLOADS_DIR, cls.GENERATED_PAGES_DIR, cls.LOGS_DIR]
        for dir_path in dirs:
            os.makedirs(dir_path, exist_ok=True)

# تهيئة المجلدات عند الاستيراد
Config.init_dirs()