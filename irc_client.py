import re
import time
import threading
import socket
import types
import datetime # I believe any times given from api.twitch.tv are given in UTC date format (need to confirm)
from enum import Enum
from collections import deque

class CommandType(Enum):
    pong = 1
    message = 2
    timeout = 3
    ban = 4

class IrcCommand:
    type: CommandType
    args: types.SimpleNamespace

    def __init__(self, _type: CommandType, _args: types.SimpleNamespace):
        self.type = _type
        self.args = _args

def send_pong(connection: socket):
    print("|{}| replied to server's ping".format(datetime.datetime.utcnow()))
    connection.send("PONG :tmi.twitch.tv\r\n".encode("utf-8"))

def send_message(connection: socket, args: types.SimpleNamespace):
    connection.send("PRIVMSG {} :{}\r\n".format(args.channel, args.message).encode("utf-8"))
    print("|{}| {}(bot): {}".format(datetime.datetime.utcnow(), args.username, args.message))

def timeout_user(connection: socket, args: types.SimpleNamespace):
    print("|{}| TIMED OUT '{}' for '{}'".format(datetime.datetime.utcnow(), args.username, args.reason))
    connection.send("PRIVMSG {} :.timeout {} {} {}\r\n".format(args.channel, args.username, args.time, args.reason).encode("utf-8"))

def ban_user(connection: socket, args: types.SimpleNamespace):
    print("|{}| BANNED '{}' for '{}'".format(datetime.datetime.utcnow(), args.username, args.reason))
    connection.send("PRIVMSG {} :.ban {} {}\r\n".format(args.channel, args.username, args.reason).encode("utf-8"))

class CommandQueue(threading.Thread):
    connection: socket
    commands: deque
    rate: float

    def __init__(self, _connection: socket, _commands: deque, _rate: float):
        super(CommandQueue, self).__init__()
        self.connection = _connection
        self.rate = _rate
        self.commands = _commands

    def run(self):
        while True:
            if len(self.commands) != 0:
                command: IrcCommand = self.commands.popleft()
                if command.type == CommandType.pong:
                    send_pong(self.connection)
                elif command.type == CommandType.message:
                    send_message(self.connection, command.args)
                elif command.type == CommandType.timeout:
                    timeout_user(self.connection, command.args)
                elif command.type == CommandType.ban:
                    ban_user(self.connection, command.args)
                time.sleep(1 / self.rate)

class ResponseType(Enum):
    ping = 1
    message = 2
    whisper = 3
    join = 4
    part = 5
    subscribe = 6
    cheer = 7

class IrcResponse:
    type: ResponseType
    properties: types.SimpleNamespace

    def __init__(self, _type: ResponseType, _properties: types.SimpleNamespace):
        self.type = _type
        self.properties = _properties

def getMessageProps(props: list):
    properties = types.SimpleNamespace()
    for prop in props:
        parts = prop.split("=")
        if parts[0] == "@badges":
            properties.badges = parts[1]
        elif parts[0] == "mod":
            properties.mod = parts[1]
        elif parts[0] == "subscriber":
            properties.subscriber = parts[1]
        elif parts[0] == "user-id":
            properties.user_id = parts[1]
        elif parts[0] == "user-type":
            properties.user_type = parts[1]
    return properties
def decodeMessage(response: str, cap_mode: bool):
    CHAT_MSG = re.compile(r"^:\w+!\w+@\w+\.tmi\.twitch\.tv \w+ #\w+ :")
    properties = types.SimpleNamespace()
    if cap_mode:
        parts = response.split(" ", 1)
        cap_props = parts[0].split(";")
        msg = parts[1]
        properties.username = re.search(r"\w+", msg).group(0)
        properties.message = CHAT_MSG.sub("", msg).rstrip()
        properties.info = getMessageProps(cap_props)
    else:
        properties.username = re.search(r"\w+", response).group(0)
        properties.message = CHAT_MSG.sub("", response).rstrip()
        properties.info = types.SimpleNamespace()
    return properties

def getWhisperProps(props: list):
    properties = types.SimpleNamespace()
    for prop in props:
        parts = prop.split("=")
        if parts[0] == "@badges":
            properties.badges = parts[1]
        elif parts[0] == "user-id":
            properties.user_id = parts[1]
        elif parts[0] == "user-type":
            properties.user_type = parts[1]
    return properties

def decodeWhisper(response: str, cap_mode: bool):
    CHAT_MSG = re.compile(r"^:\w+!\w+@\w+\.tmi\.twitch\.tv \w+ #\w+ :")
    properties = types.SimpleNamespace()
    if cap_mode:
        parts = response.split(" ", 1)
        cap_props = parts[0].split(";")
        msg = parts[1]
        properties.username = re.search(r"\w+", msg).group(0)
        properties.message = CHAT_MSG.sub("", msg).rstrip()
        properties.info = getWhisperProps(cap_props)
    else:
        properties.username = re.search(r"\w+", response).group(0)
        properties.message = CHAT_MSG.sub("", response).rstrip()
        properties.info = types.SimpleNamespace()
    return properties

def decodeJoinPart(response: str):
    properties = types.SimpleNamespace()
    properties.username = re.search(r"\w+", response).group(0)
    return properties

def decodeUserNotice(response: str):
    properties = types.SimpleNamespace
    "@badges=subscriber/0,premium/1;color=;display-name=Hazarddaking;emotes=;id=eca43c17-c085-4983-bb10-a7c7bb3bbf51;login=hazarddaking;mod=0;msg-id=resub;" \
    "msg-param-months=2;msg-param-sub-plan-name=Channel\sSubscription\s(summit1g);msg-param-sub-plan=Prime;room-id=26490481;subscriber=1;" \
    "system-msg=Hazarddaking\sjust\ssubscribed\swith\sTwitch\sPrime.\sHazarddaking\ssubscribed\sfor\s2\smonths\sin\sa\srow!;tmi-sent-ts=1494983687845;turbo=0;user-id=103321354;" \
    "user-type= :tmi.twitch.tv USERNOTICE #summit1g :Keep it up man!"
    # still need to do something with this, using Summit1G's chat as reference for some responses

class ResponseQueue(threading.Thread):
    connection: socket
    responses: deque
    rate: float
    cap_mode: bool
    def __init__(self, _connection: socket, _responses: deque, _rate: float, _cap_mode):
        super(ResponseQueue, self).__init__()
        self.connection = _connection
        self.responses = _responses
        self.rate = _rate
        self.cap_mode = _cap_mode

    def run(self):
        while True:
            try:
                response = self.connection.recv(1024).decode("utf-8")
                if re.search(r"PING", response) is not None:
                    properties = types.SimpleNamespace()
                    properties.timestamp = datetime.datetime.utcnow()
                    self.responses.appendleft(IrcResponse(ResponseType.ping, properties))
                elif re.search(r"PRIVMSG", response) is not None:
                    properties = decodeMessage(response, self.cap_mode)
                    properties.timestamp = datetime.datetime.utcnow()
                    self.responses.append(IrcResponse(ResponseType.message, properties))
                elif self.cap_mode:
                    if re.search(r"JOIN", response):
                        properties = decodeJoinPart(response)
                        properties.timestamp = datetime.datetime.utcnow()
                        self.responses.append(IrcResponse(ResponseType.join, properties))
                    elif re.search(r"PART", response):
                        properties = decodeJoinPart(response)
                        properties.timestamp = datetime.datetime.utcnow()
                        self.responses.append(IrcResponse(ResponseType.part, properties))
                    elif re.search(r"WHISPER", response):
                        properties = decodeWhisper(response, self.cap_mode)
                        properties.timestamp = datetime.datetime.utcnow()
                        self.responses.append(IrcResponse(ResponseType.whisper, properties))
                    elif re.search(r"USERNOTICE", response): # usually a subscription
                        print("response: " + response)
                    else:
                        print("Un-Documented Response: {}".format(response))
            except socket.error:
                '''No Responses Yet'''

class IrcInfo:
    host: str
    port: int
    nickname: str
    password: str
    channel: str

    def __init__(self, _host: str, _port: int, _nick: str, _pass: str, _chan: str):
        self.host = _host
        self.port = _port
        self.nickname = _nick
        self.password = _pass
        self.channel = _chan

class IrcClient:
    connection: socket
    responses: deque
    commands: deque
    info: IrcInfo
    connected: bool = False

    def __init__(self, _info: IrcInfo, _rate: float, cap_mode):
        self.responses = deque([])
        self.commands = deque([])
        self.info = _info

        self.connection = socket.socket()
        self.connection.connect((self.info.host, self.info.port))
        self.connection.send("PASS {}\r\n".format(self.info.password).encode("utf-8"))
        self.connection.send("NICK {}\r\n".format(self.info.nickname).encode("utf-8"))
        if cap_mode:
            self.connection.send("CAP REQ :twitch.tv/membership\r\n".encode("utf-8"))
            self.connection.send("CAP REQ :twitch.tv/commands\r\n".encode("utf-8"))
            self.connection.send("CAP REQ :twitch.tv/tags\r\n".encode("utf-8"))
        self.connection.send("JOIN {}\r\n".format(self.info.channel).encode("utf-8"))
        self.connection.setblocking(0)

        response = ""
        while re.search(r"NAMES", response) is None:
            try:
                response = self.connection.recv(1024).decode("utf-8")
            except socket.error:
                '''No Responses Yet'''

        self.connected = True

        self.rq = ResponseQueue(self.connection, self.responses, _rate, cap_mode)
        self.rq.setDaemon(True)
        self.rq.start()

        self.cq = CommandQueue(self.connection, self.commands, _rate)
        self.cq.setDaemon(True)
        self.cq.start()

    def addCommand_front(self, _command: IrcCommand):
        self.commands.appendleft(_command)

    def addCommand_back(self, _command: IrcCommand):
        self.commands.append(_command)

    def hasResponses(self):
        return len(self.responses) != 0

    def getResponse(self):
        if len(self.responses) != 0:
            return self.responses.popleft()
        else:
            return None
