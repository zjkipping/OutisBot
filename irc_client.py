import re
import time
import threading
import socket
import types
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
    print("<---- Replied To Server's Ping ---->")
    connection.send("PONG :tmi.twitch.tv\r\n".encode("utf-8"))

def send_message(connection: socket, args: types.SimpleNamespace):
    connection.send("PRIVMSG {} :{}\r\n".format(args.channel, args.message).encode("utf-8"))
    print("<---- Bot Message: '{}' ---->".format(args.message))

def timeout_user(connection: socket, args: types.SimpleNamespace):
    print("<---- Timed Out User {} for {} ---->".format(args.username, args.reason))
    connection.send("PRIVMSG {} :.timeout {} {} {}\r\n".format(args.channel, args.username, args.time, args.reason).encode("utf-8"))

def ban_user(connection: socket, args: types.SimpleNamespace):
    print("<---- Banned User {} for {} ---->".format(args.username, args.reason))
    connection.send("PRIVMSG {} :.ban {} {}\r\n".format(args.channel, args.username, args.reason).encode("utf-8"))

class CommandQueue(threading.Thread):
    connection: socket
    commands: deque
    rate: float
    cap_mode: bool

    def __init__(self, _connection: socket, _commands: deque, _rate: float, _cap_mode):
        super(CommandQueue, self).__init__()
        self.connection = _connection
        self.rate = _rate
        self.commands = _commands
        self.cap_mode = _cap_mode

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
                # if self.cap_mode:
                #     if command.type == CommandType.
                time.sleep(1 / self.rate)

class ResponseType(Enum):
    ping = 1
    message = 2
    join = 3
    part = 4
    subscribe = 5
    follow = 6
    cheer = 7

class IrcResponse:
    type: ResponseType
    properties: types.SimpleNamespace

    def __init__(self, _type: ResponseType, _properties: types.SimpleNamespace):
        self.type = _type
        self.properties = _properties

def getCapProps(props: list):
    properties = types.SimpleNamespace()
    properties.badges = props[0].split("=")[1]
    properties.color = props[1].split("=")[1]
    properties.display_name = props[2].split("=")[1]
    properties.emotes = props[3].split("=")[1]
    properties.id = props[4].split("=")[1]
    properties.mod = props[5].split("=")[1]
    properties.room_id = props[6].split("=")[1]
    properties.sent_ts = props[7].split("=")[1]
    properties.subscriber = props[8].split("=")[1]
    properties.tmi_sent_ts = props[9].split("=")[1]
    properties.turbo = props[10].split("=")[1]
    properties.user_id = props[11].split("=")[1]
    properties.user_type = props[12].split("=")[1]
    return properties

def decodeMessage(response: str, cap_mode: bool):
    CHAT_MSG = re.compile(r"^:\w+!\w+@\w+\.tmi\.twitch\.tv PRIVMSG #\w+ :")
    properties = types.SimpleNamespace()
    if cap_mode:
        parts = response.split(" ", 1)
        cap_props = parts[0].split(";")
        msg = parts[1]
        properties.username = re.search(r"\w+", msg).group(0)
        properties.message = CHAT_MSG.sub("", msg).rstrip()
        properties.info = getCapProps(cap_props)
    else:
        properties.username = re.search(r"\w+", response).group(0)
        properties.message = CHAT_MSG.sub("", response).rstrip()
    return properties

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
            properties = types.SimpleNamespace()
            try:
                response = self.connection.recv(1024).decode("utf-8")
                if re.search(r"PING", response) is not None:
                    self.responses.appendleft(IrcResponse(ResponseType.ping, properties))
                elif re.search(r"PRIVMSG", response) is not None:
                    properties = decodeMessage(response, self.cap_mode)
                    self.responses.append(IrcResponse(ResponseType.message, properties))
                if self.cap_mode:
                    if re.search(r"JOIN", response):
                        # need to decode JOIN
                        self.responses.append(IrcResponse(ResponseType.join, properties))
                    elif re.search(r"PART", response):
                        # need to decode PART
                        self.responses.append(IrcResponse(ResponseType.part, properties))
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
        while re.search(r"Welcome", response) is None:
            try:
                response = self.connection.recv(1024).decode("utf-8")
            except socket.error:
                '''No Responses Yet'''

        self.connected = True

        self.rq = ResponseQueue(self.connection, self.responses, _rate, cap_mode)
        self.rq.setDaemon(True)
        self.rq.start()

        self.cq = CommandQueue(self.connection, self.commands, _rate, cap_mode)
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
