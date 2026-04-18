# 📁 builder_engine/signer.py
"""
توقيع APK تلقائياً
"""

import os
import subprocess
import tempfile
from pathlib import Path

class APKSigner:
    def __init__(self):
        self.keystore_path = "builder_engine/android.keystore"
        self.key_alias = "androidkey"
        self.keystore_password = "android123"
        self.key_password = "android123"
        
    def create_keystore(self):
        """إنشاء Keystore جديد"""
        if os.path.exists(self.keystore_path):
            print(f"[*] Keystore موجود مسبقاً: {self.keystore_path}")
            return True
        
        print("[*] إنشاء Keystore جديد...")
        
        cmd = [
            "keytool", "-genkey", "-v",
            "-keystore", self.keystore_path,
            "-alias", self.key_alias,
            "-keyalg", "RSA",
            "-keysize", "2048",
            "-validity", "10000",
            "-storepass", self.keystore_password,
            "-keypass", self.key_password,
            "-dname", "CN=Android, OU=Android, O=Android, L=Android, S=Android, C=US"
        ]
        
        try:
            # إدخال تلقائي للإجابات
            process = subprocess.run(
                cmd,
                input=b"\n\n\n\n\n\n\n",
                capture_output=True,
                text=True
            )
            
            if process.returncode == 0:
                print("[+] تم إنشاء Keystore بنجاح")
                return True
            else:
                print(f"[-] خطأ: {process.stderr}")
                return False
                
        except FileNotFoundError:
            print("[-] keytool غير مثبت. تأكد من تثبيت Java JDK")
            return False
    
    def sign_apk(self, apk_path, output_path=None):
        """توقيع APK"""
        
        if not self.create_keystore():
            return None
        
        if output_path is None:
            output_path = apk_path.replace('.apk', '_signed.apk')
        
        print(f"[*] توقيع APK: {apk_path}")
        
        # التوقيع باستخدام jarsigner
        sign_cmd = [
            "jarsigner", "-verbose",
            "-sigalg", "SHA1withRSA",
            "-digestalg", "SHA1",
            "-keystore", self.keystore_path,
            "-storepass", self.keystore_password,
            "-keypass", self.key_password,
            apk_path,
            self.key_alias
        ]
        
        try:
            # تنفيذ الأمر
            result = subprocess.run(sign_cmd, capture_output=True, text=True)
            
            if result.returncode != 0:
                print(f"[-] خطأ في التوقيع: {result.stderr}")
                return None
            
            print("[+] تم توقيع APK بنجاح")
            
            # تحسين APK باستخدام zipalign
            aligned_path = self._zipalign_apk(apk_path)
            if aligned_path and aligned_path != apk_path:
                os.rename(aligned_path, output_path)
            
            return output_path
            
        except Exception as e:
            print(f"[-] استثناء أثناء التوقيع: {e}")
            return None
    
    def _zipalign_apk(self, apk_path):
        """تحسين APK باستخدام zipalign"""
        
        # إنشاء ملف مؤقت للمحاذاة
        temp_dir = tempfile.gettempdir()
        aligned_path = os.path.join(temp_dir, f"aligned_{os.path.basename(apk_path)}")
        
        cmd = ["zipalign", "-v", "4", apk_path, aligned_path]
        
        try:
            result = subprocess.run(cmd, capture_output=True, text=True)
            
            if result.returncode == 0:
                print("[+] تم تحسين APK باستخدام zipalign")
                return aligned_path
            else:
                print(f"[-] خطأ في zipalign: {result.stderr}")
                return apk_path
                
        except FileNotFoundError:
            print("[-] zipalign غير مثبت. تخطي التحسين")
            return apk_path
    
    def verify_signature(self, apk_path):
        """التحقق من توقيع APK"""
        
        cmd = ["jarsigner", "-verify", "-verbose", apk_path]
        
        try:
            result = subprocess.run(cmd, capture_output=True, text=True)
            
            if "jar verified." in result.stdout or "jar is unsigned" not in result.stdout:
                print("[+] APK موقّع بشكل صحيح")
                return True
            else:
                print("[-] APK غير موقّع أو توقيع غير صحيح")
                return False
                
        except Exception as e:
            print(f"[-] خطأ في التحقق: {e}")
            return False