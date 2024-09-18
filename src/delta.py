from .api_base import APIClientBase
from .logger import Logger


class DeltaAPIClient(APIClientBase):
    def __init__(self, delta_base_url, api_token):
        self.logger = Logger(self.__class__.__name__)

        super().__init__(delta_base_url, {"X-Ripple-Token": api_token})

    # Nothing here yet...
