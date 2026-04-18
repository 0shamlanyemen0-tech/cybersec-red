#!/usr/bin/env python3
"""
Base64 Encoding/Decoding Manager
"""

import base64
import zlib
import hashlib

class Base64Manager:
    @staticmethod
    def encode_file(file_path, compress=True):
        """
        Encode file to base64
        """
        try:
            with open(file_path, 'rb') as f:
                data = f.read()
            
            if compress:
                data = zlib.compress(data, level=9)
            
            encoded = base64.b64encode(data).decode('utf-8')
            return encoded
            
        except Exception as e:
            print(f"Error encoding file: {e}")
            return None
    
    @staticmethod
    def decode_file(encoded_data, output_path, decompress=True):
        """
        Decode base64 to file
        """
        try:
            decoded = base64.b64decode(encoded_data)
            
            if decompress:
                decoded = zlib.decompress(decoded)
            
            with open(output_path, 'wb') as f:
                f.write(decoded)
            
            return output_path
            
        except Exception as e:
            print(f"Error decoding file: {e}")
            return None
    
    @staticmethod
    def encode_string(text, encoding='utf-8'):
        """
        Encode string to base64
        """
        try:
            encoded = base64.b64encode(text.encode(encoding)).decode('utf-8')
            return encoded
        except:
            return None
    
    @staticmethod
    def decode_string(encoded_text, encoding='utf-8'):
        """
        Decode base64 to string
        """
        try:
            decoded = base64.b64decode(encoded_text).decode(encoding)
            return decoded
        except:
            return None
    
    @staticmethod
    def split_base64(data, chunk_size=76):
        """
        Split base64 into chunks for embedding in HTML/JS
        """
        chunks = []
        for i in range(0, len(data), chunk_size):
            chunk = data[i:i + chunk_size]
            chunks.append(f'"{chunk}"')
        
        return chunks
    
    @staticmethod
    def create_data_url(data, mime_type='application/octet-stream'):
        """
        Create data URL from base64
        """
        return f"data:{mime_type};base64,{data}"
    
    @staticmethod
    def calculate_hash(data):
        """
        Calculate hash of data for verification
        """
        if isinstance(data, str):
            data = data.encode('utf-8')
        
        md5 = hashlib.md5(data).hexdigest()
        sha256 = hashlib.sha256(data).hexdigest()
        
        return {
            'md5': md5,
            'sha256': sha256,
            'size': len(data)
        }

# Test the module
if __name__ == "__main__":
    manager = Base64Manager()
    
    # Test string encoding
    test_string = "Hello, UAMS Framework!"
    encoded = manager.encode_string(test_string)
    decoded = manager.decode_string(encoded)
    
    print(f"Original: {test_string}")
    print(f"Encoded: {encoded}")
    print(f"Decoded: {decoded}")
    print(f"Match: {test_string == decoded}")
    
    # Test hash
    hashes = manager.calculate_hash(test_string)
    print(f"\nHashes: {hashes}")