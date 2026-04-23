# Utils module
import logging

logger = logging.getLogger(__name__)

class IPUtils:
    @staticmethod
    def validate_ip(ip_address):
        return True
    
    @staticmethod
    def get_local_ip():
        return "127.0.0.1"

class PortScanner:
    def __init__(self):
        pass
    
    def scan(self, host, ports):
        return {}

class LogManager:
    def __init__(self):
        self.logs = []
    
    def log(self, message, level='INFO'):
        self.logs.append((level, message))

if __name__ == '__main__':
    pass
