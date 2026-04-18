#!/usr/bin/env python3
"""
تدوير وتنظيف السجلات
"""

import os
import gzip
import shutil
from datetime import datetime, timedelta
from pathlib import Path

class LogRotator:
    """مدير تدوير السجلات"""
    
    def __init__(self, logs_dir="web_server/logs", max_days=30):
        self.logs_dir = Path(logs_dir)
        self.max_days = max_days
    
    def rotate_logs(self):
        """تدوير السجلات"""
        print("🔄 تدوير ملفات السجلات...")
        
        log_files = [
            "access.log",
            "error.log", 
            "uams_web.log",
            "downloads.log"
        ]
        
        for log_file in log_files:
            file_path = self.logs_dir / log_file
            
            if file_path.exists() and file_path.stat().st_size > 0:
                # إنشاء نسخة مضغوطة
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                backup_name = f"{log_file}.{timestamp}.gz"
                backup_path = self.logs_dir / "archive" / backup_name
                
                # إنشاء مجلد الأرشيف
                backup_path.parent.mkdir(exist_ok=True)
                
                # ضغط الملف
                with open(file_path, 'rb') as f_in:
                    with gzip.open(backup_path, 'wb') as f_out:
                        shutil.copyfileobj(f_in, f_out)
                
                # إفراغ الملف الأصلي
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(f"# Log rotated at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
                    f.write("# Previous log archived to: " + backup_name + "\n")
                    f.write("="*80 + "\n")
                
                print(f"  ✅ {log_file} → {backup_name}")
        
        print("✅ تم تدوير جميع السجلات")
    
    def cleanup_old_logs(self):
        """تنظيف السجلات القديمة"""
        print("🧹 تنظيف السجلات القديمة...")
        
        archive_dir = self.logs_dir / "archive"
        if not archive_dir.exists():
            return
        
        cutoff_date = datetime.now() - timedelta(days=self.max_days)
        deleted_count = 0
        
        for log_file in archive_dir.glob("*.gz"):
            file_time = datetime.fromtimestamp(log_file.stat().st_mtime)
            
            if file_time < cutoff_date:
                log_file.unlink()
                deleted_count += 1
        
        print(f"✅ تم حذف {deleted_count} ملف سجل قديم")
    
    def get_log_stats(self):
        """الحصول على إحصائيات السجلات"""
        stats = {
            'total_files': 0,
            'total_size': 0,
            'files': []
        }
        
        for log_file in self.logs_dir.glob("*.log"):
            if log_file.is_file():
                size = log_file.stat().st_size
                stats['total_files'] += 1
                stats['total_size'] += size
                stats['files'].append({
                    'name': log_file.name,
                    'size': size,
                    'size_human': self._human_readable_size(size),
                    'modified': datetime.fromtimestamp(log_file.stat().st_mtime).strftime('%Y-%m-%d %H:%M:%S')
                })
        
        stats['total_size_human'] = self._human_readable_size(stats['total_size'])
        
        return stats
    
    def _human_readable_size(self, size):
        """تحويل الحجم إلى صيغة مقروءة"""
        for unit in ['B', 'KB', 'MB', 'GB']:
            if size < 1024.0:
                return f"{size:.1f} {unit}"
            size /= 1024.0
        return f"{size:.1f} TB"

if __name__ == "__main__":
    rotator = LogRotator()
    
    print("📊 إحصائيات السجلات:")
    stats = rotator.get_log_stats()
    
    print(f"   الملفات: {stats['total_files']}")
    print(f"   الحجم الإجمالي: {stats['total_size_human']}")
    
    for file_info in stats['files']:
        print(f"   📄 {file_info['name']}: {file_info['size_human']} (آخر تعديل: {file_info['modified']})")
    
    # تدوير السجلات
    # rotator.rotate_logs()
    
    # تنظيف القديمة
    # rotator.cleanup_old_logs()