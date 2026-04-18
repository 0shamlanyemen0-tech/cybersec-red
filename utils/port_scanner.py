# 📁 utils/port_scanner.py
"""
مسح المنافذ والشبكات
"""

import socket
import threading
from concurrent.futures import ThreadPoolExecutor, as_completed

class PortScanner:
    def __init__(self, timeout=1, max_threads=100):
        self.timeout = timeout
        self.max_threads = max_threads
    
    def scan_port(self, target_ip: str, port: int) -> dict:
        """مسح منفذ واحد"""
        result = {
            'port': port,
            'open': False,
            'service': 'unknown',
            'banner': ''
        }
        
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.settimeout(self.timeout)
                
                if s.connect_ex((target_ip, port)) == 0:
                    result['open'] = True
                    
                    # محاولة الحصول على الـ banner
                    try:
                        s.send(b'HEAD / HTTP/1.0\r\n\r\n')
                        banner = s.recv(1024).decode('utf-8', errors='ignore')
                        result['banner'] = banner[:200]
                        
                        # تحديد الخدمة من المنفذ
                        result['service'] = self._guess_service(port, banner)
                    except:
                        result['service'] = self._guess_service(port)
        
        except Exception as e:
            result['error'] = str(e)
        
        return result
    
    def scan_ports(self, target_ip: str, ports: list) -> list:
        """مسح قائمة منافذ"""
        results = []
        
        with ThreadPoolExecutor(max_workers=self.max_threads) as executor:
            future_to_port = {
                executor.submit(self.scan_port, target_ip, port): port 
                for port in ports
            }
            
            for future in as_completed(future_to_port):
                result = future.result()
                if result['open']:
                    results.append(result)
        
        return sorted(results, key=lambda x: x['port'])
    
    def scan_range(self, target_ip: str, start_port: int = 1, end_port: int = 1000) -> list:
        """مسح نطاق منافذ"""
        ports = list(range(start_port, end_port + 1))
        return self.scan_ports(target_ip, ports)
    
    def scan_common_ports(self, target_ip: str) -> list:
        """مسح المنافذ الشائعة"""
        common_ports = [
            21, 22, 23, 25, 53, 80, 110, 111, 135, 139, 143, 443,
            445, 993, 995, 1723, 3306, 3389, 5900, 8080, 8443
        ]
        return self.scan_ports(target_ip, common_ports)
    
    def _guess_service(self, port: int, banner: str = "") -> str:
        """تخمين الخدمة من المنفذ والبanner"""
        
        services = {
            20: "FTP Data", 21: "FTP", 22: "SSH", 23: "Telnet",
            25: "SMTP", 53: "DNS", 80: "HTTP", 110: "POP3",
            143: "IMAP", 443: "HTTPS", 445: "SMB", 3306: "MySQL",
            3389: "RDP", 5900: "VNC", 8080: "HTTP Proxy",
            8443: "HTTPS Alt", 4444: "Metasploit", 5555: "ADB"
        }
        
        if port in services:
            return services[port]
        
        # البحث في banner
        banner_lower = banner.lower()
        if 'apache' in banner_lower:
            return "Apache"
        elif 'nginx' in banner_lower:
            return "nginx"
        elif 'iis' in banner_lower:
            return "IIS"
        elif 'ssh' in banner_lower:
            return "SSH"
        
        return f"Port {port}"
    
    def network_scan(self, network: str = "192.168.1.0/24", ports: list = [80, 443, 22]) -> dict:
        """مسح شبكة كاملة"""
        import ipaddress
        
        results = {}
        
        try:
            network_obj = ipaddress.ip_network(network, strict=False)
            
            for ip in network_obj.hosts():
                ip_str = str(ip)
                print(f"Scanning {ip_str}...")
                
                open_ports = []
                for port in ports:
                    result = self.scan_port(ip_str, port)
                    if result['open']:
                        open_ports.append(result)
                
                if open_ports:
                    results[ip_str] = open_ports
        
        except Exception as e:
            print(f"Network scan error: {e}")
        
        return results