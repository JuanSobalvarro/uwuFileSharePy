# File: small_app/services/uwu_protocol/enums.py

from enum import Enum

class MessageType(str, Enum):
    REQUEST = "request"
    RESPONSE = "response"
    EVENT = "event"
    ERROR = "error"

class RequestAction(str, Enum):
    REGISTER = "register"
    GET_DHT = "get_dht"
    GET_FILE = "get_file"
    PEER_CONNECT = "peer_connect"
    PEER_DISCOVERY = "peer_discovery"
    DHT_UPDATE = "dht_update"
    FILE_DOWNLOAD = "file_download"

class ResponseAction(str, Enum):
    REGISTER_ACK = "register_ack"
    GET_DHT_RESPONSE = "get_dht_response"
    GET_FILE_RESPONSE = "get_file_response"
    PEER_LIST = "peer_list"
    DHT_UPDATE_RESPONSE = "dht_update_response"
    FILE_DOWNLOAD_RESPONSE = "file_download_response"
    ERROR = "error"
    TIMEOUT = "timeout"

class EventAction(str, Enum):
    PEER_JOINED = "peer_joined"
    PEER_LEFT = "peer_left"
