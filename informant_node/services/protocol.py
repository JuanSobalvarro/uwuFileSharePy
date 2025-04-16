"""
This module defines the UWU protocol for communication between nodes in the network.

UWUProtocol has RequestTypes and ResponseTypes enums to define the types of requests and responses that can be sent.
It provides methods to create requests and responses, parse incoming messages, and validate the format of requests and responses.

The protocol uses JSON for message formatting, and all messages are encoded to bytes before transmission.

Each request and response function/callback is defined in the RequestFunctions class, which is responsible for handling
specific request types (defined by the user).
"""
from enum import Enum
import json

class UWUProtocol:
    class RequestTypes(str, Enum):
        REGISTER = "register"
        GET_DHT = "get_dht"
        GET_FILE = "get_file"

    class ResponseTypes(str, Enum):
        SUCCESS = "success"
        ERROR = "error"

    @staticmethod
    def create_request(req_type: RequestTypes, **kwargs) -> bytes:
        return json.dumps({
            "type": req_type.value,
            **kwargs
        }).encode()

    @staticmethod
    def create_response(resp_type: ResponseTypes, **kwargs) -> bytes:
        return json.dumps({
            "status": resp_type.value,
            **kwargs
        }).encode()

    @staticmethod
    def parse_message(data: bytes) -> dict:
        try:
            return json.loads(data.decode())
        except Exception:
            raise ValueError("Invalid JSON format")

    @staticmethod
    def is_valid_request(msg: dict) -> bool:
        return "type" in msg and msg["type"] in UWUProtocol.RequestTypes._value2member_map_

    @staticmethod
    def is_valid_response(msg: dict) -> bool:
        return "status" in msg and msg["status"] in UWUProtocol.ResponseTypes._value2member_map_
