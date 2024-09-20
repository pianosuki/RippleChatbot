import requests
from typing import Any


class APIClientBase:
    def __init__(self, base_url: str, headers: dict[str, str]):
        self.base_url = base_url
        self.headers = headers

    def get(self, endpoint: str, query: str = "") -> Any:
        url = self.base_url + endpoint + query

        response = requests.get(url, headers=self.headers)
        return response.json()

    def post(self, endpoint: str, data: Any):
        url = self.base_url + endpoint

        response = requests.post(url, json=data, headers=self.headers)
        return response.json()
