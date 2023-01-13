from src.api import APIClient
from src.logger import Logger

class DeltaAPIClient(APIClient):
    def __init__(self, delta_base_url, api_token):
        # Define the Logger
        self.logger = Logger(self.__class__.__name__)

        # Set base URL and headers
        self.base_url = delta_base_url
        self.headers = {"X-Ripple-Token": api_token}

    # Nothing here yet...
