from .api_base import APIClientBase
from .logger import Logger


class RippleAPIClient(APIClientBase):
    def __init__(self, ripple_base_url, api_token):
        self.logger = Logger(self.__class__.__name__)

        super().__init__(ripple_base_url, {"X-Ripple-Token": api_token})

    def get_users(self, **kwargs) -> dict:
        endpoint = "/users"
        query_params = []

        for key, value in kwargs.items():
            match key:
                case "username":
                    query_params.append("nname={}".format(value))
                case "user_id":
                    query_params.append("iid={}".format(value))
                case "privileges":
                    query_params.append("privileges={}".format(value))
                case "has_privileges":
                    query_params.append("has_privileges={}".format(value))
                case "has_not_privileges":
                    query_params.append("has_not_privileges={}".format(value))
                case "country":
                    query_params.append("country={}".format(value))
                case "name_aka":
                    query_params.append("name_aka={}".format(value))
                case "privilege_group":
                    query_params.append("privilege_group={}".format(value))
                case "ids":
                    for item in value:
                        query_params.append("ids={}".format(item))
                case "names":
                    for item in value:
                        query_params.append("names={}".format(item))
                case "names_aka":
                    for item in value:
                        query_params.append("names_aka={}".format(item))
                case "countries":
                    for item in value:
                        query_params.append("countries={}".format(item))
                case "sort":
                    query_params.append("sort={}".format(value))

        query = "?" + "&".join(query_params)

        response = self.get(endpoint, query)
        return response

    def get_user_id(self, username: str) -> int:
        response = self.get_users(username=username)
        return response["users"][0]["id"]
