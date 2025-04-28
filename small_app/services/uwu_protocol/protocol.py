"""
This module defines the UWU protocol for communication between nodes in the network.

UWUProtocol has RequestTypes and ResponseTypes enums to define the types of requests and responses that can be sent.
It provides methods to create requests and responses, parse incoming messages, and validate the format of requests and responses.

The protocol uses JSON for message formatting, and all messages are encoded to bytes before transmission.

Each request and response function/callback is defined in the RequestFunctions class, which is responsible for handling
specific request types (defined by the user).
"""
from .enums import MessageType, RequestAction, ResponseAction, EventAction
import json


class UWUProtocol:
    @staticmethod
    def create_message(msg_type: MessageType, action: str, peer_info: dict, data: dict) -> bytes:
        return json.dumps({
            "type": msg_type.value,
            "action": action,
            "peer_info": peer_info,
            "data": data
        }).encode()

    @staticmethod
    def parse_message(raw: bytes) -> dict:
        try:
            return json.loads(raw.decode())
        except json.JSONDecodeError:
            raise ValueError(f"[PROTOCOL] Invalid JSON format. JSON decode error: {raw.decode()}")

    @staticmethod
    def is_valid(msg: dict) -> bool:
        return (
            isinstance(msg, dict) and
            "type" in msg and
            "action" in msg and
            "data" in msg and
            "peer_info" in msg and
            msg["type"] in MessageType._value2member_map_ and
            UWUProtocol._is_valid_action(msg["action"])
        )

    @staticmethod
    def _is_valid_action(action: str):
        return action in RequestAction._value2member_map_ or action in ResponseAction._value2member_map_ or action in EventAction._value2member_map_