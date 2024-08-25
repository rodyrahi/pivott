import os
from dotenv import load_dotenv
import subprocess
import requests

import json

# Load version from config.json
with open('config.json', 'r') as config_file:
    config = json.load(config_file)
    version = config.get('VERSION')

print(version)

# Define file paths and server details
local_file_path = r'C:\Users\Raj\Desktop\raj.txt'
remote_file_path = '/root/app/api_pivott/static/'
remote_server = 'root@165.232.151.6'

# Use SCP to transfer the file
scp_command = f'scp {local_file_path} {remote_server}:{remote_file_path}'
try:
    subprocess.run(scp_command, shell=True, check=True, stderr=subprocess.PIPE, text=True)
except subprocess.CalledProcessError as e:
    print(f"SCP Error: {e.stderr}")
    exit(1)

# Define the API endpoint and headers
url = "https://pivott.click/api/setversion"
headers = {"Content-Type": "application/json"}
data = {"version": version}

# Send POST request to the API
response = requests.post(url, headers=headers, json=data)

# Print the response status code and content
print(f"Response Status Code: {response.status_code}")
print(f"Response Content: {response.text}")
