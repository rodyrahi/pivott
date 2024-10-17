import requests
import json
import subprocess
import sys









class AutoUpdater:
    def __init__(self, current_version, version_url):
        """
        Initialize the AutoUpdater.
        
        Args:
            current_version (str): The current version of the software.
            version_url (str): The URL to the version manifest (JSON) on the remote server.
        """
        self.current_version = float(current_version)
        self.version_url = version_url

    def check_for_updates(self):
        """Check for updates by comparing the current version with the remote version."""
        try:
            response = requests.get(self.version_url)
            data = json.loads(response.text)
            latest_version = float(data["version"])
            
            print(f"Current Version: {self.current_version} , Latest Version: {latest_version}")
            if latest_version > self.current_version:
                return data["update_url"]
            else:
                return None
        except Exception as e:
            print(f"Error checking for updates: {e}")
            return None

    def download_update(self, update_url, progress_callback=None):
        """Download the update with progress tracking.
        
        Args:
            update_url (str): The URL of the update installer.
            progress_callback (callable): Function to update progress (optional).
        """
        try:
            response = requests.get(update_url, stream=True)
            total_size = int(response.headers.get('content-length', 0))
            downloaded_size = 0
            file_path = "latest_setup.exe"
            
            with open(file_path, "wb") as f:
                for chunk in response.iter_content(chunk_size=8192):
                    if chunk:
                        f.write(chunk)
                        downloaded_size += len(chunk)
                        
                        if progress_callback:
                            progress_callback(downloaded_size, total_size)
                            
            return file_path
        except Exception as e:
            print(f"Error downloading update: {e}")
            return None

    def apply_update(self, installer_path):
        """Run the installer and close the current application.
        
        Args:
            installer_path (str): Path to the downloaded installer.
        """
        try:
            subprocess.Popen([installer_path])
            sys.exit()  # Exit the current application
        except Exception as e:
            print(f"Error applying update: {e}")
