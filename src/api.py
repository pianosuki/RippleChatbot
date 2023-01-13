import requests

class APIClient:
    def __init__(self):
        # Define the Logger
        self.logger = Logger(self.__class__.__name__)

    def get(self, endpoint, query = ""):
        url = self.base_url + endpoint + query
        response = requests.get(url, headers = self.headers)
        return response.json()

    def post(self, endpoint, data):
        url = self.base_url + endpoint
        response = requests.post(url, json = data, headers = self.headers)
        return response.json()
