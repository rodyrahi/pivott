import requests

class get_update():
    def __init__(self , version):
        super().__init__()
        self.url = "https://pivott.click/api"
        self.data_api = "https://pivott.click/api/data"
        self.version = version
    
    def update(self):
        headers = {
            "Content-Type": "application/json"
        }

        response = requests.post(self.url, json=self.version, headers=headers)

        if response.status_code == 200:
            print("POST request successful")
            return response.json()
        else:
            print(f"POST request failed with status code: {response.status_code}")
            return response.text
    
    def get_data(self , prompt):
        headers = {
            "Content-Type": "application/json"
        }

        response = requests.post(self.data_api, json=prompt, headers=headers)

        if response.status_code == 200:
            print("POST request successful")
            return response.json()
        else:
            print(f"POST request failed with status code: {response.status_code}")
            return response.text

