from enum import Enum

class MessageType(str, Enum):
    REQUEST = "request"
    RESPONSE = "response"
    EVENT = "event"


class RequestAction(str, Enum):
    REGISTER = "register"
    GET_DHT = "get_dht"
    GET_FILE = "get_file"


class ResponseAction(str, Enum):
    """
    In response the actions is interpreted as the status of the request.
    """
    GET_DHT = "get_dht"
    GET_FILE = "get_file"
    REGISTER = "register"

class EventAction(str, Enum):
    """
    Event actions are events that once triggered are not expected to be answered and are sent to all peers connected
    to the informant node.
    """
    PEER_JOINED = "peer_joined"
    PEER_LEFT = "peer_left"