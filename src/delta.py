import re

from .api_base import APIClientBase
from .logger import Logger


class DeltaAPIClient(APIClientBase):
    def __init__(self, delta_base_url, api_token):
        self.logger = Logger(self.__class__.__name__)

        super().__init__(delta_base_url, {"X-Ripple-Token": api_token})

    def get_client(self, client_identifier: str | int) -> dict:
        endpoint = "/clients"
        api_identifier_pattern = r"^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$"

        if isinstance(client_identifier, int) or (isinstance(client_identifier, str) and re.match(api_identifier_pattern, client_identifier)):
            endpoint += f"/{client_identifier}"
        else:
            raise ValueError("client_identifier must be a valid API Identifier or an integer")

        response = self.get(endpoint)
        return response

    def is_online(self, client_identifier: str | int) -> bool:
        return bool(self.get_client(client_identifier)["clients"])
