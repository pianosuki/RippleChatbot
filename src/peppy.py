from .api_base import APIClientBase
from .logger import Logger


class PeppyAPIClient(APIClientBase):
    def __init__(self, peppy_base_url):
        self.logger = Logger(self.__class__.__name__)

        super().__init__(peppy_base_url, {})

    def get_beatmaps(self, **kwargs) -> list[dict]:
        endpoint = "/get_beatmaps"
        query_params = []

        for key, value in kwargs.items():
            match key:
                case "h":
                    query_params.append("h={}".format(value))

        query = "?" + "&".join(query_params)

        response = self.get(endpoint, query)
        return response
