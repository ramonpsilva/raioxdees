"""
Security module for the DEES Dashboard
Handles authentication, encryption, and data masking
"""
import streamlit as st
from cryptography.fernet import Fernet

class SecurityManager:
    """Manages encryption and decryption of data files using Fernet symmetric encryption"""
       
    def encrypt_file(self, input_file: str, output_file: str):
        """Encrypt a file"""
        # Use the key from Streamlit secrets
        XRAY_DEES_KEY = st.secrets["XRAY_DEES_KEY"]
        fernet = Fernet(XRAY_DEES_KEY)
        
        # Read the file
        with open(input_file, 'rb') as file:
            file_data = file.read()
        
        # Encrypt the data
        encrypted_data = fernet.encrypt(file_data)
        
        # Write encrypted data to output file
        with open(output_file, 'wb') as encrypted_file:
            encrypted_file.write(encrypted_data)
    
    def decrypt_file(self, encrypted_file: str) -> bytes:
        """Decrypt a file and return its content"""
        # Use the key from Streamlit secrets
        XRAY_DEES_KEY = st.secrets["XRAY_DEES_KEY"]
        fernet = Fernet(XRAY_DEES_KEY)
        
        with open(encrypted_file, 'rb') as file:
            encrypted_data = file.read()
        
        # Decrypt the data
        decrypted_data = fernet.decrypt(encrypted_data)
        return decrypted_data
    
    
