# 📁 utils/ip_utils.py
"""
أدوات إدارة عناوين IP
"""

import socket
import ipaddress
import netifaces
import requests

class IPUtils:
    @staticmethod
    def get_local_ip() -> str:
        """الحصول على IP المحلي"""
        try:
            # محاولة الاتصال بالإنترنت للحصول على IP العام
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.connect(("8.8.8.8", 80))
            local_ip = s.getsockname()[0]
            s.close()
            return local_ip
        except:
            return "127.0.0.1"
    
    @staticmethod
    def get_public_ip() -> str:
        """الحصول على IP العام"""
        try:
            response = requests.get('https://api.ipify.org', timeout=5)
            return response.text
        except:
            return "غير متاح"
    
    @staticmethod
    def get_network_interfaces() -> dict:
        """الحصول على معلومات واجهات الشبكة"""
        interfaces = {}
        
        for iface in netifaces.interfaces():
            addrs = netifaces.ifaddresses(iface)
            
            if netifaces.AF_INET in addrs:
                ipv4_info = addrs[netifaces.AF_INET][0]
                interfaces[iface] = {
                    'ip': ipv4_info.get('addr', ''),
                    'netmask': ipv4_info.get('netmask', ''),
                    'broadcast': ipv4_info.get('broadcast', '')
                }
        
        return interfaces
    
    @staticmethod
    def validate_ip(ip_str: str) -> bool:
        """التحقق من صحة عنوان IP"""
        try:
            ipaddress.ip_address(ip_str)
            return True
        except ValueError:
            return False
    
    @staticmethod
    def validate_port(port: int) -> bool:
        """التحقق من صحة المنفذ"""
        return 1 <= port <= 65535
    
    @staticmethod
    def is_local_ip(ip_str: str) -> bool:
        """التحقق إذا كان IP محلي"""
        try:
            ip = ipaddress.ip_address(ip_str)
            return ip.is_private or ip.is_loopback or ip_str == "localhost"
        except:
            return False
    
    @staticmethod
    def get_available_port(start_port: int = 8000, end_port: int = 9000) -> int:
        """العثور على منفذ متاح"""
        for port in range(start_port, end_port + 1):
            try:
                with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                    s.bind(('0.0.0.0', port))
                    return port
            except:
                continue
        return 0
    
    @staticmethod
    def create_tunnel_url(local_port: int, service: str = "ngrok") -> str:
        """إنشاء عنوان نفق للوصول الخارجي"""
        if service == "ngrok":
            try:
                import pyngrok
                from pyngrok import ngrok
                
                # تشغيل نفق ngrok
                tunnel = ngrok.connect(local_port, "http")
                return tunnel.public_url
            except:
                return "ngrok غير مثبت"
        
        elif service == "localtunnel":
            return f"https://lt-{local_port}.loca.lt"
        
        return f"http://localhost:{local_port}"