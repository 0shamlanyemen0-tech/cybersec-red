#!/usr/bin/env python3
"""
إنشاء شهادات SSL ذاتية التوقيع
"""

from cryptography import x509
from cryptography.x509.oid import NameOID
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.backends import default_backend
from datetime import datetime, timedelta
import os

def generate_ssl_certificates():
    """إنشاء شهادات SSL"""
    
    ssl_dir = "web_server/ssl"
    os.makedirs(ssl_dir, exist_ok=True)
    
    print("🔐 إنشاء شهادات SSL ذاتية التوقيع...")
    
    try:
        # 1. إنشاء مفتاح خاص
        print("  1. إنشاء المفتاح الخاص...")
        private_key = rsa.generate_private_key(
            public_exponent=65537,
            key_size=2048,
            backend=default_backend()
        )
        
        # 2. إنشاء شهادة
        print("  2. إنشاء الشهادة...")
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
            private_key.public_key()
        ).serial_number(
            x509.random_serial_number()
        ).not_valid_before(
            datetime.now()
        ).not_valid_after(
            datetime.now() + timedelta(days=365)
        ).add_extension(
            x509.SubjectAlternativeName([
                x509.DNSName("localhost"),
                x509.DNSName("127.0.0.1"),
                x509.DNSName("uams.local")
            ]),
            critical=False,
        ).sign(private_key, hashes.SHA256(), default_backend())
        
        # 3. حفظ المفتاح الخاص
        print("  3. حفظ الملفات...")
        key_path = os.path.join(ssl_dir, "private.key")
        with open(key_path, "wb") as f:
            f.write(private_key.private_bytes(
                encoding=serialization.Encoding.PEM,
                format=serialization.PrivateFormat.TraditionalOpenSSL,
                encryption_algorithm=serialization.NoEncryption()
            ))
        
        # 4. حفظ الشهادة
        cert_path = os.path.join(ssl_dir, "certificate.pem")
        with open(cert_path, "wb") as f:
            f.write(cert.public_bytes(serialization.Encoding.PEM))
        
        # 5. إنشاء ملف PEM كامل (لـ Flask)
        pem_path = os.path.join(ssl_dir, "ssl.pem")
        with open(pem_path, "wb") as f:
            f.write(private_key.private_bytes(
                encoding=serialization.Encoding.PEM,
                format=serialization.PrivateFormat.TraditionalOpenSSL,
                encryption_algorithm=serialization.NoEncryption()
            ))
            f.write(cert.public_bytes(serialization.Encoding.PEM))
        
        # 6. إنشاء CSR (طلب توقيع الشهادة)
        csr = x509.CertificateSigningRequestBuilder().subject_name(
            subject
        ).sign(private_key, hashes.SHA256(), default_backend())
        
        csr_path = os.path.join(ssl_dir, "csr.pem")
        with open(csr_path, "wb") as f:
            f.write(csr.public_bytes(serialization.Encoding.PEM))
        
        print("✅ تم إنشاء الشهادات بنجاح!")
        print(f"   📁 المفتاح الخاص: {key_path}")
        print(f"   📁 الشهادة: {cert_path}")
        print(f"   📁 ملف PEM كامل: {pem_path}")
        print(f"   📁 CSR: {csr_path}")
        
        return True
        
    except ImportError:
        print("❌ مكتبة cryptography غير مثبتة")
        print("🔧 قم بتشغيل: pip install cryptography")
        return False
    except Exception as e:
        print(f"❌ خطأ: {e}")
        return False

def create_dummy_certificates():
    """إنشاء شهادات وهمية (بدون cryptography)"""
    
    ssl_dir = "web_server/ssl"
    os.makedirs(ssl_dir, exist_ok=True)
    
    print("🔐 إنشاء شهادات SSL وهمية...")
    
    # مفتاح خاص وهمي
    dummy_key = """-----BEGIN PRIVATE KEY-----
MIIEvQIBADANBgkqhkiG9w0BAQEFAASCBKcwggSjAgEAAoIBAQCzKLZI3f6H9Q7R
1XK7L8F6n4Y5Y2T8GkLmNpOqRtUvWxZyD8nHjK7MpQsTqRwYlNtB8rPwS5XvHjLm
... (مختصر للعرض) ...
-----END PRIVATE KEY-----
"""
    
    # شهادة وهمية
    dummy_cert = """-----BEGIN CERTIFICATE-----
MIIDXTCCAkWgAwIBAgIUYOzM9fJjK7NpQsTqRwYlNtB8rPwwDQYJKoZIhvcNAQEL
BQAwTjELMAkGA1UEBhMCVVMxEzARBgNVBAgMClNvbWUtU3RhdGUxITAfBgNVBAoM
... (مختصر للعرض) ...
-----END CERTIFICATE-----
"""
    
    # حفظ الملفات
    with open(os.path.join(ssl_dir, "private.key"), "w") as f:
        f.write(dummy_key)
    
    with open(os.path.join(ssl_dir, "certificate.pem"), "w") as f:
        f.write(dummy_cert)
    
    with open(os.path.join(ssl_dir, "ssl.pem"), "w") as f:
        f.write(dummy_key + dummy_cert)
    
    print("✅ تم إنشاء شهادات وهمية (للتجربة فقط)")
    return True

if __name__ == "__main__":
    # محاولة إنشاء شهادات حقيقية
    if not generate_ssl_certificates():
        # إذا فشلت، أنشئ شهادات وهمية
        create_dummy_certificates()