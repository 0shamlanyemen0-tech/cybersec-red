# 📁 utils/log_manager.py
"""
نظام تسجيل وتتبع الأحداث
"""

import logging
import sys
import json
from datetime import datetime
from pathlib import Path

class LogManager:
    def __init__(self, log_dir="logs", app_name="UAMS"):
        self.log_dir = Path(log_dir)
        self.log_dir.mkdir(exist_ok=True)
        
        self.app_name = app_name
        
        # إعداد logging الأساسي
        self._setup_logging()
        
        # ملفات سجلات مخصصة
        self.attack_log = self.log_dir / "attacks.json"
        self.session_log = self.log_dir / "sessions.json"
        
    def _setup_logging(self):
        """إعداد نظام logging"""
        
        # formatter
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        
        # ملف log رئيسي
        file_handler = logging.FileHandler(
            self.log_dir / f"{self.app_name}.log",
            encoding='utf-8'
        )
        file_handler.setFormatter(formatter)
        
        # console handler
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setFormatter(formatter)
        
        # إعداد الـ root logger
        root_logger = logging.getLogger()
        root_logger.setLevel(logging.INFO)
        root_logger.addHandler(file_handler)
        root_logger.addHandler(console_handler)
        
        self.logger = logging.getLogger(self.app_name)
    
    def log_attack(self, attack_type: str, target: str, details: dict):
        """تسجيل هجوم"""
        log_entry = {
            'timestamp': datetime.now().isoformat(),
            'type': attack_type,
            'target': target,
            'details': details,
            'success': details.get('success', False)
        }
        
        self._append_json_log(self.attack_log, log_entry)
        self.logger.info(f"Attack: {attack_type} on {target}")
    
    def log_session(self, session_id: str, event: str, data: dict):
        """تسجيل حدث جلسة"""
        log_entry = {
            'timestamp': datetime.now().isoformat(),
            'session_id': session_id,
            'event': event,
            'data': data
        }
        
        self._append_json_log(self.session_log, log_entry)
        self.logger.info(f"Session {session_id}: {event}")
    
    def log_command(self, session_id: str, command: str, result: str, success: bool = True):
        """تسجيل أمر تم تنفيذه"""
        log_entry = {
            'timestamp': datetime.now().isoformat(),
            'session_id': session_id,
            'command': command,
            'result_length': len(result),
            'success': success
        }
        
        # تسجيل مختصر في log العادي
        self.logger.info(f"Command [{session_id}]: {command[:50]}...")
    
    def log_error(self, module: str, error: str, details: dict = None):
        """تسجيل خطأ"""
        error_entry = {
            'timestamp': datetime.now().isoformat(),
            'module': module,
            'error': error,
            'details': details or {}
        }
        
        error_file = self.log_dir / "errors.json"
        self._append_json_log(error_file, error_entry)
        
        self.logger.error(f"{module}: {error}")
    
    def log_system_event(self, event: str, data: dict = None):
        """تسجيل حدث نظام"""
        self.logger.info(f"System: {event}")
        
        if data:
            self.logger.debug(f"System data: {json.dumps(data, indent=2)}")
    
    def get_recent_logs(self, log_type: str = "all", limit: int = 100) -> list:
        """الحصول على أحدث السجلات"""
        logs = []
        
        if log_type in ["all", "attacks"]:
            logs.extend(self._read_json_log(self.attack_log)[-limit:])
        
        if log_type in ["all", "sessions"]:
            logs.extend(self._read_json_log(self.session_log)[-limit:])
        
        if log_type in ["all", "errors"]:
            error_file = self.log_dir / "errors.json"
            logs.extend(self._read_json_log(error_file)[-limit:])
        
        # ترتيب حسب الوقت
        logs.sort(key=lambda x: x.get('timestamp', ''), reverse=True)
        
        return logs[:limit]
    
    def _append_json_log(self, file_path: Path, entry: dict):
        """إضافة مدخل لملف JSON"""
        try:
            # قراءة الملف الحالي
            if file_path.exists():
                with open(file_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
            else:
                data = []
            
            # إضافة المدخل الجديد
            data.append(entry)
            
            # حفظ الملف
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
        
        except Exception as e:
            self.logger.error(f"Failed to write JSON log: {e}")
    
    def _read_json_log(self, file_path: Path) -> list:
        """قراءة ملف JSON"""
        try:
            if file_path.exists():
                with open(file_path, 'r', encoding='utf-8') as f:
                    return json.load(f)
        except Exception as e:
            self.logger.error(f"Failed to read JSON log: {e}")
        
        return []
    
    def cleanup_old_logs(self, days: int = 30):
        """تنظيف السجلات القديمة"""
        from datetime import datetime, timedelta
        
        cutoff_date = datetime.now() - timedelta(days=days)
        
        for log_file in self.log_dir.glob("*.json"):
            try:
                with open(log_file, 'r', encoding='utf-8') as f:
                    logs = json.load(f)
                
                # تصفية السجلات القديمة
                filtered_logs = [
                    log for log in logs 
                    if datetime.fromisoformat(log['timestamp']) > cutoff_date
                ]
                
                # حفظ الملف المصفى
                with open(log_file, 'w', encoding='utf-8') as f:
                    json.dump(filtered_logs, f, indent=2, ensure_ascii=False)
                
                self.logger.info(f"Cleaned {log_file.name}: {len(logs) - len(filtered_logs)} entries removed")
                
            except Exception as e:
                self.logger.error(f"Failed to clean {log_file}: {e}")