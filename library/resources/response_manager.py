import socket, re, threading, datetime
from types import SimpleNamespace
from collections import deque
from library.resources.common import IrcResponse, IrcResponseType

def decodeCheer(response: str):
    args = SimpleNamespace()
    args.login = re.search("\w+", response.split(" ", 1)[1]).group(0)
    args.display = None
    headers = response.split(" ", 1)[0].split(";")
    for header in headers:
        parts = header.split("=")
        if parts[0] == "display-name":
            args.display = parts[1]
        elif parts[0] == "user-id":
            args.id = parts[1]
        elif parts[0] == "bits":
            args.amount = parts[1]
    if args.display is None or args.display == "":
        args.display = args.login
    return args
def decodeUserNotice(response: str):
    args = SimpleNamespace()
    headers = response.split(" ", 1)[0].split(";")
    args.display = None
    args.login = None
    for header in headers:
        parts = header.split("=")
        if parts[0] == "display-name":
            args.display = parts[1]
        elif parts[0] == "login":
            args.login = parts[1]
        elif parts[0] == "user-id":
            args.id = parts[1]
        elif parts[0] == "msg-id":
            args.type = parts[1]
        elif parts[0] == "msg-param-months":
            args.duration = parts[1]
        elif parts[0] == "msg-param-sub-plan":
            args.plan = parts[1]
    if args.display is None or args.display == "":
        args.display = args.login
    return args
def decodeWhisper(response: str):
    args = SimpleNamespace()
    headers = response.split(" ", 1)[0].split(";")
    irc = response.split(" ", 1)[1]
    args.display = None
    for header in headers:
        parts = header.split("=")
        if parts[0] == "user-id":
            args.id = parts[1]
        elif parts[0] == "display-name":
            args.display = parts[1]
    WHISPER_MESSAGE = re.compile(r"^:\w+!\w+@\w+\.tmi\.twitch\.tv WHISPER \w+ :")
    args.message = WHISPER_MESSAGE.sub("", irc).rstrip()
    args.login = re.search("\w+", irc).group(0)
    if args.display is None or args.display == "":
        args.display = args.login
    return args
def decodeMessageBasic(response: str):
    args = SimpleNamespace()
    CHAT_MESSAGE = re.compile(r"^:\w+!\w+@\w+\.tmi\.twitch\.tv PRIVMSG #\w+ :")
    args.message = CHAT_MESSAGE.sub("", response).rstrip()
    args.login = re.search("\w+", response).group(0)
    args.display = args.login
    args.id = None
    args.sub = None
    args.mod = None
    return args
def decodeMessageAdvanced(response: str):
    headers = response.split(" ", 1)[0].split(";")
    irc = response.split(" ", 1)[1]
    args = decodeMessageBasic(irc)
    args.display = None
    for header in headers:
        parts = header.split("=")
        if parts[0] == "user-id":
            args.id = parts[1]
        elif parts[0] == "display-name":
            args.display = parts[1]
        elif parts[0] == "mod":
            args.mod = parts[1]
        elif parts[0] == "subscriber":
            args.sub = parts[1]
    if args.display is None or args.display == "":
        args.display = args.login
    return args

class ResponseManager(threading.Thread):
    def __init__(self, _responses: deque):
        super(ResponseManager, self).__init__()
        self.__mode = False
        self.__responses = _responses
        self.__connection = socket.socket()
        self.__running = True
    def setup(self, _mode, _connection):
        self.__mode = _mode
        self.__connection = _connection
    def run(self):
        while self.__running:
            try:
                responses = self.__connection.recv(1024).decode("utf-8").split("\r\n")
                if responses:
                    for response in responses:
                        if response is not '':
                            if re.match(r"^PING :tmi\.twitch\.tv", response) is not None:
                                self.__responses.appendleft(IrcResponse(IrcResponseType.ping, datetime.datetime.utcnow(), SimpleNamespace()))
                            elif re.match(r"^:\w+!\w+@\w+\.tmi\.twitch\.tv PRIVMSG #\w+ :\w*", response) is not None:
                                self.__responses.append(IrcResponse(IrcResponseType.message, datetime.datetime.utcnow(), decodeMessageBasic(response)))
                            elif self.__mode:
                                if len(response.split(" ", 1)) > 1:
                                    headers = response.split(" ", 1)[0]
                                    irc = response.split(" ", 1)[1]
                                    if re.match(r"^:\w+!\w+@\w+\.tmi\.twitch\.tv PRIVMSG #\w+ :\w*", irc) is not None:
                                        if re.search(r"bits=\w+;", headers) is not None:
                                            self.__responses.append(IrcResponse(IrcResponseType.cheer, datetime.datetime.utcnow(), decodeCheer(response)))
                                        else:
                                            self.__responses.append(IrcResponse(IrcResponseType.message, datetime.datetime.utcnow(), decodeMessageAdvanced(response)))
                                            pass
                                    elif re.match(r"^:\w+!\w+@\w+\.tmi\.twitch\.tv WHISPER \w+ :\w*", irc) is not None:
                                        self.__responses.append(IrcResponse(IrcResponseType.whisper, datetime.datetime.utcnow(), decodeWhisper(response)))
                                    elif re.match(r"^:tmi\.twitch\.tv USERNOTICE #\w+", irc) is not None:
                                        if "msg-id=resub;" in headers or "msg-id=sub;" in headers:
                                            self.__responses.appendleft(IrcResponse(IrcResponseType.subscribe, datetime.datetime.utcnow(), decodeUserNotice(response)))
                                        else:
                                            print(response)
                                            '''Other Notices From Twitch'''
                else:
                    self.__running = False
            except (socket.error, UnicodeDecodeError):
                '''No Responses Yet'''
    def stop(self):
        self.__running = False
    def isRunning(self):
        return self.__running
