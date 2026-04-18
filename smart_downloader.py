#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# smart_base_apk_downloader.py - محمل ذكي ومتين لـ base.apk

import os
import sys
import json
import time
import hashlib
import requests
import tempfile
import zipfile
from typing import Optional, Tuple, List
from datetime import datetime, timedelta
from urllib.parse import urlparse

# ==================== إعدادات متقدمة ====================

class APKDownloader:
    """
    محمل ذكي لملفات APK مع:
    - مصادر متعددة (12+ مصدر)
    - التحقق من السلامة
    - إعادة المحاولة
    - تخزين مؤقت
    - تجاوز الحظر
    """
    
    def __init__(self):
        self.base_path = os.path.join("builder_engine", "templates", "base_app")
        self.apk_path = os.path.join(self.base_path, "base.apk")
        self.cache_file = os.path.join(self.base_path, ".apk_cache.json")
        
        # قائمة موسعة من المصادر الموثوقة
        self.sources = self._build_source_list()
        
        # إعدادات الجلسة
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            'Accept': '*/*',
            'Accept-Language': 'en-US,en;q=0.9',
            'Accept-Encoding': 'gzip, deflate, br',
        })
        
        # بروكسيات احتياطية (لتجاوز الحظر)
        self.proxies = [
            None,  # بدون بروكسي أولاً
            {'http': 'http://proxy.example.com:8080'},  # ضع بروكسي حقيقي هنا
        ]
        
    def _build_source_list(self) -> List[dict]:
        """
        بناء قائمة موسعة من المصادر مع أولويات
        """
        return [
            # الفئة A: تطبيقات بسيطة ومفتوحة المصدر (الأفضل)
            {
                'url': 'https://github.com/SimpleMobileTools/Simple-Flashlight/releases/download/5.3.1/flashlight-101-fdroid.apk',
                'name': 'Simple Flashlight',
                'priority': 1,
                'expected_hash': None,  # لا نتحقق من الهاش (سنتحقق من الحجم فقط)
                'min_size_mb': 1.0,
                'max_size_mb': 10.0,
                'source_type': 'github'
            },
            {
                'url': 'https://github.com/SimpleMobileTools/Simple-Calculator/releases/download/5.2.0/calculator-102-fdroid.apk',
                'name': 'Simple Calculator',
                'priority': 1,
                'min_size_mb': 1.5,
                'max_size_mb': 8.0,
                'source_type': 'github'
            },
            {
                'url': 'https://github.com/SimpleMobileTools/Simple-Notes/releases/download/6.16.1/notes-111-fdroid.apk',
                'name': 'Simple Notes',
                'priority': 1,
                'min_size_mb': 2.0,
                'max_size_mb': 12.0,
                'source_type': 'github'
            },
            {
                'url': 'https://github.com/SimpleMobileTools/Simple-Gallery/releases/download/6.26.0/gallery-226-fdroid.apk',
                'name': 'Simple Gallery',
                'priority': 1,
                'min_size_mb': 3.0,
                'max_size_mb': 15.0,
                'source_type': 'github'
            },
            
            # الفئة B: تطبيقات من F-Droid (مستقرة)
            {
                'url': 'https://f-droid.org/repo/com.simplemobiletools.flashlight_36.apk',
                'name': 'Flashlight (F-Droid)',
                'priority': 2,
                'min_size_mb': 1.0,
                'max_size_mb': 5.0,
                'source_type': 'fdroid'
            },
            {
                'url': 'https://f-droid.org/repo/com.simplemobiletools.calculator_47.apk',
                'name': 'Calculator (F-Droid)',
                'priority': 2,
                'min_size_mb': 1.5,
                'max_size_mb': 6.0,
                'source_type': 'fdroid'
            },
            {
                'url': 'https://f-droid.org/repo/com.simplemobiletools.notes.pro_111.apk',
                'name': 'Notes (F-Droid)',
                'priority': 2,
                'min_size_mb': 2.0,
                'max_size_mb': 8.0,
                'source_type': 'fdroid'
            },
            {
                'url': 'https://f-droid.org/repo/com.simplemobiletools.clock_21.apk',
                'name': 'Clock (F-Droid)',
                'priority': 2,
                'min_size_mb': 2.0,
                'max_size_mb': 7.0,
                'source_type': 'fdroid'
            },
            {
                'url': 'https://f-droid.org/repo/com.simplemobiletools.voicerecorder_33.apk',
                'name': 'Voice Recorder (F-Droid)',
                'priority': 2,
                'min_size_mb': 2.5,
                'max_size_mb': 9.0,
                'source_type': 'fdroid'
            },
            
            # الفئة C: مصادر بديلة (احتياطية)
            {
                'url': 'https://archive.org/download/simple-flashlight-apk/flashlight.apk',
                'name': 'Flashlight (Archive.org)',
                'priority': 3,
                'min_size_mb': 1.0,
                'max_size_mb': 5.0,
                'source_type': 'archive'
            },
            {
                'url': 'https://gitlab.com/SimpleMobileTools/Simple-Flashlight/-/raw/master/app/release/app-release.apk',
                'name': 'Flashlight (GitLab)',
                'priority': 3,
                'min_size_mb': 1.0,
                'max_size_mb': 5.0,
                'source_type': 'gitlab'
            },
            {
                'url': 'https://codeberg.org/SimpleMobileTools/Simple-Flashlight/releases/download/5.3.1/flashlight.apk',
                'name': 'Flashlight (Codeberg)',
                'priority': 3,
                'min_size_mb': 1.0,
                'max_size_mb': 5.0,
                'source_type': 'codeberg'
            },
        ]
    
    def _check_existing_file(self) -> bool:
        """
        التحقق من وجود ملف APK صالح
        """
        if not os.path.exists(self.apk_path):
            return False
        
        file_size = os.path.getsize(self.apk_path)
        size_mb = file_size / (1024 * 1024)
        
        # التحقق من الحجم
        if size_mb < 0.5:  # أقل من 0.5 MB مشبوه
            print(f"⚠️ base.apk موجود لكن حجمه صغير جداً: {size_mb:.2f} MB")
            return False
        
        if size_mb > 50:  # أكبر من 50 MB كبير جداً
            print(f"⚠️ base.apk موجود لكن حجمه كبير جداً: {size_mb:.2f} MB")
            return False
        
        # التحقق من أنه ملف ZIP حقيقي (APK هو ZIP)
        try:
            with zipfile.ZipFile(self.apk_path, 'r') as zf:
                # التحقق من وجود AndroidManifest.xml
                if 'AndroidManifest.xml' not in zf.namelist():
                    print("⚠️ الملف لا يحتوي على AndroidManifest.xml")
                    return False
                
                # التحقق من وجود classes.dex
                if 'classes.dex' not in zf.namelist():
                    print("⚠️ الملف لا يحتوي على classes.dex")
                    return False
                
        except zipfile.BadZipFile:
            print("⚠️ الملف ليس ZIP صالحاً")
            return False
        
        print(f"✅ base.apk موجود وصالح: {size_mb:.2f} MB")
        return True
    
    def _verify_apk(self, file_path: str, source_info: dict) -> bool:
        """
        التحقق من صحة ملف APK المحمل
        """
        try:
            file_size = os.path.getsize(file_path)
            size_mb = file_size / (1024 * 1024)
            
            # التحقق من الحجم
            min_size = source_info.get('min_size_mb', 0.5)
            max_size = source_info.get('max_size_mb', 20)
            
            if size_mb < min_size:
                print(f"   ⚠️ حجم الملف صغير جداً: {size_mb:.2f} MB (الحد الأدنى: {min_size} MB)")
                return False
            
            if size_mb > max_size:
                print(f"   ⚠️ حجم الملف كبير جداً: {size_mb:.2f} MB (الحد الأقصى: {max_size} MB)")
                return False
            
            # التحقق من توقيع ZIP
            with open(file_path, 'rb') as f:
                header = f.read(4)
                if header[:2] != b'PK':
                    print(f"   ⚠️ الملف ليس ZIP (APK يجب أن يكون ZIP)")
                    return False
            
            # التحقق من محتوى ZIP
            with zipfile.ZipFile(file_path, 'r') as zf:
                file_list = zf.namelist()
                
                # يجب أن يحتوي على AndroidManifest.xml
                if 'AndroidManifest.xml' not in file_list:
                    print(f"   ⚠️ الملف لا يحتوي على AndroidManifest.xml")
                    return False
                
                # يجب أن يحتوي على classes.dex
                if 'classes.dex' not in file_list:
                    print(f"   ⚠️ الملف لا يحتوي على classes.dex")
                    return False
            
            # التحقق من الهاش (إذا كان محدداً)
            expected_hash = source_info.get('expected_hash')
            if expected_hash:
                with open(file_path, 'rb') as f:
                    file_hash = hashlib.sha256(f.read()).hexdigest()
                    if file_hash != expected_hash:
                        print(f"   ⚠️ هاش الملف غير متطابق")
                        return False
            
            return True
            
        except Exception as e:
            print(f"   ⚠️ فشل التحقق من الملف: {e}")
            return False
    
    def _download_with_retry(self, url: str, source_info: dict, max_retries: int = 3) -> Optional[str]:
        """
        تحميل ملف مع إعادة المحاولة وتغيير البروكسي
        """
        for attempt in range(max_retries):
            try:
                # تغيير البروكسي في كل محاولة
                proxy = self.proxies[attempt % len(self.proxies)] if self.proxies else None
                
                print(f"   🔄 محاولة {attempt + 1}/{max_retries}...")
                
                # إضافة تأخير تصاعدي
                if attempt > 0:
                    time.sleep(attempt * 2)
                
                # إرسال الطلب
                response = self.session.get(
                    url,
                    timeout=(15, 60),  # (connection timeout, read timeout)
                    stream=True,
                    proxies=proxy,
                    allow_redirects=True
                )
                
                if response.status_code != 200:
                    print(f"   ⚠️ استجابة HTTP {response.status_code}")
                    
                    # إذا كان 404، لا داعي لإعادة المحاولة
                    if response.status_code == 404:
                        return None
                    
                    continue
                
                # التحقق من نوع المحتوى
                content_type = response.headers.get('content-type', '')
                if 'html' in content_type.lower():
                    print(f"   ⚠️ استلمنا HTML بدلاً من APK (ربما رابط معطل)")
                    continue
                
                # حفظ الملف مؤقتاً
                with tempfile.NamedTemporaryFile(delete=False, suffix='.apk') as tmp_file:
                    # قراءة أول 2 بايت للتحقق
                    first_chunk = response.raw.read(2)
                    if first_chunk != b'PK':
                        print(f"   ⚠️ الملف ليس APK (يبدأ بـ {first_chunk})")
                        os.unlink(tmp_file.name)
                        continue
                    
                    tmp_file.write(first_chunk)
                    
                    # كتابة الباقي
                    for chunk in response.iter_content(chunk_size=8192):
                        if chunk:
                            tmp_file.write(chunk)
                    
                    tmp_path = tmp_file.name
                
                # التحقق من الملف المحمل
                if self._verify_apk(tmp_path, source_info):
                    return tmp_path
                else:
                    os.unlink(tmp_path)
                    continue
                    
            except requests.exceptions.Timeout:
                print(f"   ⚠️ انتهت مهلة الاتصال")
            except requests.exceptions.ConnectionError:
                print(f"   ⚠️ فشل الاتصال")
            except Exception as e:
                print(f"   ⚠️ خطأ: {type(e).__name__}: {e}")
        
        return None
    
    def _create_fallback_apk(self) -> bool:
        """
        إنشاء APK وهمي كحل أخير
        """
        print("\n⚠️ جميع المحاولات فشلت. جاري إنشاء APK وهمي للتجارب...")
        
        try:
            os.makedirs(self.base_path, exist_ok=True)
            
            with zipfile.ZipFile(self.apk_path, 'w', zipfile.ZIP_DEFLATED) as apk:
                # AndroidManifest.xml بسيط
                manifest = '''<?xml version="1.0" encoding="utf-8"?>
<manifest xmlns:android="http://schemas.android.com/apk/res/android"
    package="com.example.fallback"
    android:versionCode="1"
    android:versionName="1.0">
    <uses-permission android:name="android.permission.INTERNET"/>
    <application android:label="Test App">
        <activity android:name=".MainActivity" android:exported="true">
            <intent-filter>
                <action android:name="android.intent.action.MAIN"/>
                <category android:name="android.intent.category.LAUNCHER"/>
            </intent-filter>
        </activity>
    </application>
</manifest>'''
                apk.writestr("AndroidManifest.xml", manifest.encode('utf-8'))
                
                # classes.dex بسيط
                dex_header = bytes([
                    0x64, 0x65, 0x78, 0x0A, 0x30, 0x33, 0x35, 0x00,
                    0x00, 0x00, 0x00, 0x00,
                    0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
                    0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
                    0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
                    0x70, 0x00, 0x00, 0x00, 0x78, 0x56, 0x34, 0x12,
                    0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
                    0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
                    0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
                    0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
                ])
                apk.writestr("classes.dex", dex_header)
                
                # resources.arsc
                apk.writestr("resources.arsc", bytes([0x02, 0x00, 0x0C, 0x00] + [0x00] * 28))
            
            print(f"✅ تم إنشاء APK وهمي (للتجارب فقط)")
            print(f"⚠️ تحذير: هذا الملف لن يعمل كتطبيق حقيقي!")
            return True
            
        except Exception as e:
            print(f"❌ فشل إنشاء APK وهمي: {e}")
            return False
    
    def download(self) -> bool:
        """
        الدالة الرئيسية للتحميل
        """
        print("\n" + "="*60)
        print("🔍 البحث عن base.apk...")
        print("="*60)
        
        # 1. التحقق من وجود ملف صالح
        if self._check_existing_file():
            return True
        
        # 2. ترتيب المصادر حسب الأولوية
        sorted_sources = sorted(self.sources, key=lambda x: x.get('priority', 999))
        
        print(f"\n📥 جاري تجربة {len(sorted_sources)} مصدر...")
        
        # 3. تجربة كل مصدر
        for i, source in enumerate(sorted_sources, 1):
            url = source['url']
            name = source.get('name', urlparse(url).netloc)
            
            print(f"\n📍 المصدر {i}/{len(sorted_sources)}: {name}")
            print(f"   🔗 {url}")
            
            # تحميل الملف
            tmp_path = self._download_with_retry(url, source)
            
            if tmp_path:
                # نقل الملف إلى المكان النهائي
                os.makedirs(self.base_path, exist_ok=True)
                
                # إذا كان هناك ملف قديم، احذفه
                if os.path.exists(self.apk_path):
                    os.remove(self.apk_path)
                
                os.rename(tmp_path, self.apk_path)
                
                size_mb = os.path.getsize(self.apk_path) / (1024 * 1024)
                print(f"\n✅ تم تحميل base.apk بنجاح!")
                print(f"📦 المصدر: {name}")
                print(f"📏 الحجم: {size_mb:.2f} MB")
                print(f"📍 المسار: {self.apk_path}")
                
                # حفظ معلومات التحميل في الكاش
                self._save_cache({
                    'source': name,
                    'url': url,
                    'size_mb': size_mb,
                    'timestamp': datetime.now().isoformat()
                })
                
                return True
        
        # 4. جميع المحاولات فشلت - إنشاء APK وهمي
        print(f"\n❌ فشل التحميل من جميع المصادر!")
        
        # سؤال المستخدم (في بيئة Railway سننشئ وهمياً تلقائياً)
        if os.environ.get('RAILWAY_ENVIRONMENT'):
            print("🚂 Railway detected: إنشاء APK وهمي تلقائياً...")
            return self._create_fallback_apk()
        else:
            print("\nالرجاء اختيار أحد الخيارات:")
            print("1. إنشاء APK وهمي للتجارب")
            print("2. الخروج")
            
            try:
                choice = input("اختيارك (1/2): ").strip()
                if choice == '1':
                    return self._create_fallback_apk()
                else:
                    return False
            except:
                return False
    
    def _save_cache(self, info: dict):
        """حفظ معلومات التحميل في الكاش"""
        try:
            with open(self.cache_file, 'w') as f:
                json.dump(info, f, indent=2)
        except:
            pass


# ==================== الدالة الرئيسية ====================

def download_base_apk() -> bool:
    """
    دالة مبسطة للاستخدام المباشر
    """
    downloader = APKDownloader()
    return downloader.download()


# ==================== نقطة الدخول ====================

if __name__ == "__main__":
    print("""
╔══════════════════════════════════════════════════════════╗
║     🧠 Smart APK Downloader - المتين والذكي              ║
║              للاستخدام التعليمي فقط                      ║
╚══════════════════════════════════════════════════════════╝
    """)
    
    if download_base_apk():
        print("\n✅ جاهز للبدء!")
        # هنا تستدعي start_unified_server()
    else:
        print("\n❌ فشل توفير base.apk. لا يمكن المتابعة.")
        sys.exit(1)