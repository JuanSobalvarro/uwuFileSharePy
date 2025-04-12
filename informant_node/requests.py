from enum import Enum


class RequestTypes(Enum):
    """
    Enum that defines the actions a client can request from the informant node.
    """
    REGISTER = "register"
    GET_DHT = "get_dht"
    GET_FILE = "get_file"


class RequestFunctions:
    def __init__(self):
        self.request_types = self.build_dict()

    def build_dict(self):
        request_types = {}

        for request_type in RequestTypes:
            request_types[request_type.value] = getattr(self, f"request_{request_type.value}", None)

        return request_types

    def get_requests(self):
        """
        Returns a dictionary of request types and their corresponding functions.
        """
        return self.request_types

    def request_register(self):
        pass

    def request_get_dht(self):
        pass

    def request_get_file(self):
        pass