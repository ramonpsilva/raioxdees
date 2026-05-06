"""
Script to encrypt a data file
Run this script once to encrypt your file
"""
import os
from security import SecurityManager

def encrypt_file(input_file: str):
    """Encrypt the data file"""
    security_manager = SecurityManager()
        
    output_file = f'{input_file}.encrypted'
    
    try:
        security_manager.encrypt_file(input_file, output_file)
        print(f"✅ File {input_file} successfully encrypted to {output_file}")
        print("⚠️  Keep the key 🔑 secure and don't commit it to public repositories!")
    except FileNotFoundError:
        print(f"❌ File {input_file} not found!")
    except Exception as e:
        print(f"❌ Error encrypting file: {str(e)}")

if __name__ == "__main__":
    data_dir = 'data'
    for filename in os.listdir(data_dir):
        filepath = os.path.join(data_dir, filename)
        if os.path.isfile(filepath):
            encrypt_file(filepath)