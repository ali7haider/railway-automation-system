import json
import os
from cryptography.fernet import Fernet

class SavingProjectManager:
    def __init__(self, key_file='encryption_key.key'):
        self.projects_folder = 'Projects'
        self.key_file = key_file
        self.encryption_key = self.load_or_generate_key()

        # Ensure the Projects folder exists
        os.makedirs(self.projects_folder, exist_ok=True)

    def load_or_generate_key(self):
        """Load an existing encryption key or generate a new one."""
        try:
            if os.path.exists(self.key_file):
                with open(self.key_file, 'rb') as key_file:
                    return key_file.read()
            else:
                key = Fernet.generate_key()
                with open(self.key_file, 'wb') as key_file:
                    key_file.write(key)
                return key
        except Exception as e:
            print(f"Error loading or generating encryption key: {e}")
            return None

    def encrypt_data(self, data):
        """Encrypt data using Fernet encryption."""
        try:
            fernet = Fernet(self.encryption_key)
            json_data = json.dumps(data).encode('utf-8')
            encrypted_data = fernet.encrypt(json_data)
            return encrypted_data
        except Exception as e:
            print(f"Error encrypting data: {e}")
            return None

    def decrypt_data(self, encrypted_data):
        """Decrypt data using Fernet encryption."""
        try:
            fernet = Fernet(self.encryption_key)
            decrypted_data = fernet.decrypt(encrypted_data)
            return json.loads(decrypted_data.decode('utf-8'))
        except Exception as e:
            print(f"Error decrypting data: {e}")
            return None

    def save_project(self, project_data):
        """Save project data to an encrypted JSON file."""
        try:
            # Convert the data to JSON string
            json_data = json.dumps(project_data, indent=4)
            
            # Encrypt the JSON data
            encrypted_data = self.encrypt_data(json_data)
            if not encrypted_data:
                raise Exception("Encryption failed. Data could not be saved.")
            
            # Get the project name and construct the file path
            project_name = project_data["Project_info"].get("Project Name", "Unnamed_Project")
            file_path = os.path.join(self.projects_folder, f"{project_name}.json")
            
            # Save encrypted data to a file
            with open(file_path, 'wb') as file:
                file.write(encrypted_data)

            print(f"Project '{project_name}' saved successfully.")
        except Exception as e:
            print(f"Error saving project: {e}")

    def load_project(self, project_name):
        """Load project data from an encrypted JSON file."""
        try:
            file_path = os.path.join(self.projects_folder, f"{project_name}.json")
            
            if not os.path.exists(file_path):
                raise FileNotFoundError(f"Project '{project_name}' does not exist.")
            
            with open(file_path, 'rb') as file:
                encrypted_data = file.read()
            
            # Decrypt the data
            decrypted_data = self.decrypt_data(encrypted_data)
            if not decrypted_data:
                raise Exception("Decryption failed. Data could not be loaded.")

            return decrypted_data
        except Exception as e:
            print(f"Error loading project: {e}")
            return None
