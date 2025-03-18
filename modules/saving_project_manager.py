import json
import os
from cryptography.fernet import Fernet

class SavingProjectManager:
    def __init__(self, key_file='encryption_key.key'):
        self.projects_folder = 'Projects'
        self.key_file = key_file
        self.encryption_key = self.load_or_generate_key()

    def load_or_generate_key(self):
        """Load an existing encryption key or generate a new one."""
        if os.path.exists(self.key_file):
            with open(self.key_file, 'rb') as key_file:
                return key_file.read()
        else:
            key = Fernet.generate_key()
            with open(self.key_file, 'wb') as key_file:
                key_file.write(key)
            return key

    def encrypt_data(self, data):
        """Encrypt data using Fernet encryption."""
        fernet = Fernet(self.encryption_key)
        json_data = json.dumps(data).encode('utf-8')
        encrypted_data = fernet.encrypt(json_data)
        return encrypted_data

    def decrypt_data(self, encrypted_data):
        """Decrypt data using Fernet encryption."""
        fernet = Fernet(self.encryption_key)
        decrypted_data = fernet.decrypt(encrypted_data)
        return json.loads(decrypted_data.decode('utf-8'))

    def save_project(self, project_name, project_data):
        """Save project data to an encrypted JSON file."""
        if not os.path.exists(self.projects_folder):
            os.makedirs(self.projects_folder)
        
        encrypted_data = self.encrypt_data(project_data)
        
        file_path = os.path.join(self.projects_folder, f"{project_name}.json")
        
        with open(file_path, 'wb') as file:
            file.write(encrypted_data)
        
        print(f"Project '{project_name}' saved successfully.")

    def load_project(self, project_name):
        """Load project data from an encrypted JSON file."""
        file_path = os.path.join(self.projects_folder, f"{project_name}.json")
        
        if not os.path.exists(file_path):
            print(f"Project '{project_name}' does not exist.")
            return None
        
        with open(file_path, 'rb') as file:
            encrypted_data = file.read()
        
        return self.decrypt_data(encrypted_data)
