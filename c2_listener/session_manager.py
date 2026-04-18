# 📁 c2_listener/session_manager.py
"""
إدارة جلسات Reverse Shell
"""

import threading
import time
import json
from datetime import datetime
from typing import Dict, List, Optional

class SessionManager:
    def __init__(self):
        self.sessions: Dict[str, dict] = {}
        self.session_lock = threading.Lock()
        self.command_history: Dict[str, List[dict]] = {}
    
    def add_session(self, session_id: str, client_socket, client_address: tuple):
        """إضافة جلسة جديدة"""
        with self.session_lock:
            session_data = {
                'id': session_id,
                'socket': client_socket,
                'address': client_address,
                'ip': client_address[0],
                'port': client_address[1],
                'connected_at': datetime.now(),
                'last_seen': datetime.now(),
                'status': 'connected',
                'device_info': {},
                'commands_executed': 0
            }
            
            self.sessions[session_id] = session_data
            self.command_history[session_id] = []
            
            print(f"[+] جلسة جديدة: {session_id} من {client_address}")
            return session_data
    
    def remove_session(self, session_id: str):
        """إزالة جلسة"""
        with self.session_lock:
            if session_id in self.sessions:
                session = self.sessions.pop(session_id)
                session['status'] = 'disconnected'
                session['disconnected_at'] = datetime.now()
                
                # إغلاق السوكيت
                try:
                    session['socket'].close()
                except:
                    pass
                
                print(f"[-] جلسة مغلقة: {session_id}")
                return True
            return False
    
    def update_session(self, session_id: str, updates: dict):
        """تحديث بيانات الجلسة"""
        with self.session_lock:
            if session_id in self.sessions:
                self.sessions[session_id].update(updates)
                self.sessions[session_id]['last_seen'] = datetime.now()
                return True
            return False
    
    def get_session(self, session_id: str) -> Optional[dict]:
        """الحصول على جلسة"""
        with self.session_lock:
            return self.sessions.get(session_id)
    
    def get_all_sessions(self) -> List[dict]:
        """الحصول على جميع الجلسات"""
        with self.session_lock:
            return list(self.sessions.values())
    
    def get_active_sessions(self) -> List[dict]:
        """الحصول على الجلسات النشطة فقط"""
        with self.session_lock:
            return [s for s in self.sessions.values() if s['status'] == 'connected']
    
    def add_command_to_history(self, session_id: str, command: str, result: str = "", success: bool = True):
        """إضافة أمر لتاريخ الجلسة"""
        with self.session_lock:
            if session_id not in self.command_history:
                self.command_history[session_id] = []
            
            command_entry = {
                'timestamp': datetime.now().isoformat(),
                'command': command,
                'result': result[:500],  # تقليل النتيجة إذا كانت طويلة
                'success': success
            }
            
            self.command_history[session_id].append(command_entry)
            
            # تحديث عدد الأوامر في الجلسة
            if session_id in self.sessions:
                self.sessions[session_id]['commands_executed'] += 1
    
    def get_command_history(self, session_id: str) -> List[dict]:
        """الحصول على تاريخ أوامر الجلسة"""
        with self.session_lock:
            return self.command_history.get(session_id, [])
    
    def cleanup_inactive_sessions(self, timeout_seconds: int = 300):
        """تنظيف الجلسات غير النشطة"""
        with self.session_lock:
            now = datetime.now()
            to_remove = []
            
            for session_id, session in self.sessions.items():
                if session['status'] == 'connected':
                    last_seen = session['last_seen']
                    inactive_time = (now - last_seen).total_seconds()
                    
                    if inactive_time > timeout_seconds:
                        to_remove.append(session_id)
            
            for session_id in to_remove:
                self.remove_session(session_id)
            
            if to_remove:
                print(f"[*] تم تنظيف {len(to_remove)} جلسة غير نشطة")
    
    def get_session_stats(self) -> dict:
        """الحصول على إحصائيات الجلسات"""
        with self.session_lock:
            total = len(self.sessions)
            active = len([s for s in self.sessions.values() if s['status'] == 'connected'])
            
            total_commands = sum(len(cmds) for cmds in self.command_history.values())
            
            return {
                'total_sessions': total,
                'active_sessions': active,
                'inactive_sessions': total - active,
                'total_commands': total_commands,
                'average_commands_per_session': total_commands / total if total > 0 else 0
            }
    
    def export_session_data(self, session_id: str) -> dict:
        """تصدير بيانات الجلسة كـ JSON"""
        session = self.get_session(session_id)
        if not session:
            return {}
        
        # نسخة من بيانات الجلسة بدون السوكيت
        export_data = session.copy()
        export_data.pop('socket', None)  # إزالة السوكيت
        
        # إضافة تاريخ الأوامر
        export_data['command_history'] = self.get_command_history(session_id)
        
        # تحويل التواريخ لـ string
        for key in ['connected_at', 'last_seen', 'disconnected_at']:
            if key in export_data and export_data[key]:
                if isinstance(export_data[key], datetime):
                    export_data[key] = export_data[key].isoformat()
        
        return export_data