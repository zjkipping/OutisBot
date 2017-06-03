import datetime
from enum import Enum
from types import SimpleNamespace

class IrcInfo:
    def __init__(self, _host: str, _port: str, _name: str, _oauth: str, _channel: str):
        self.host = _host
        self.port = _port
        self.name = _name
        self.oauth = _oauth
        self.channel = _channel
class IrcResponseType(Enum):
    ping = 1
    message = 2
    whisper = 3
    cheer = 4
    subscribe = 5
    join = 6
    part = 7
class IrcResponse:
    def __init__(self, _type: IrcResponseType, _timestamp: datetime, _args: SimpleNamespace):
        self.type = _type
        self.timestamp = _timestamp
        self.args = _args
class IrcCommandType(Enum):
    pong = 1
    message = 2
    timeout = 3
    ban = 4
class IrcCommand:
    def __init__(self, _type: IrcCommandType, _args: SimpleNamespace):
        self.type = _type
        self.args = _args
