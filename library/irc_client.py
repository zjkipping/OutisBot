import re, socket
from collections import deque
from library.resources.common import IrcInfo
from library.resources.command_manager import CommandManager
from library.resources.response_manager import ResponseManager
from library.resources.internet_connection import InternetConnection

class IrcClient:
    def __init__(self, _info: IrcInfo, _mode: bool, _rate: float):
        self.__responses: deque = deque([])
        self.__commands: deque = deque([])
        self.__socket: socket = socket.socket()
        self.__info: IrcInfo = _info
        self.__mode: bool = _mode
        self.__rate = _rate
        self.__rm: ResponseManager = ResponseManager(self.__responses)
        self.__cm: CommandManager = CommandManager(self.__commands)
        self.__int_conn: InternetConnection = InternetConnection()
        self.__int_conn.start()
        self.__ser_conn: bool = False
        self.__running = False
    def addCommandLeft(self, _command):
        self.__commands.appendleft(_command)
    def addCommandRight(self, _command):
        self.__commands.append(_command)
    def getResponse(self):
        if self.hasResponses():
            return self.__responses.popleft()
        return None
    def hasResponses(self):
        return len(self.__responses) != 0
    def hasServerConnection(self):
        if self.__ser_conn is True:
            if self.__rm.isRunning() is True:
                return True
            else:
                if self.isRunning() is True:
                    self.__ser_conn = False
                    return False
                else:
                    return True
        else:
            return False
    def hasInternetConnection(self):
        return self.__int_conn.get()
    def isRunning(self):
        return self.__running
    def connect(self):
        if self.hasInternetConnection() is True:
            self.__socket = socket.socket()
            self.__socket.connect((self.__info.host, self.__info.port))
            self.__socket.send("PASS oauth:{}\r\n".format(self.__info.oauth).encode("utf-8"))
            self.__socket.send("NICK {}\r\n".format(self.__info.name).encode("utf-8"))
            if self.__mode:
                self.__socket.send("CAP REQ :twitch.tv/membership\r\n".encode("utf-8"))
                self.__socket.send("CAP REQ :twitch.tv/commands\r\n".encode("utf-8"))
                self.__socket.send("CAP REQ :twitch.tv/tags\r\n".encode("utf-8"))
            self.__socket.send("JOIN #{}\r\n".format(self.__info.channel).encode("utf-8"))
            self.__socket.setblocking(0)
            response = ""
            while re.search("NAMES", response) is None:
                try:
                    response = self.__socket.recv(1024).decode("utf-8")
                    if response:
                        self.__ser_conn = True
                    else:
                        self.__ser_conn = False
                except socket.error:
                    '''No Responses Yet'''
    def disconnect(self):
        if self.__ser_conn is True:
            self.__socket.send("PART {}\r\n".format(self.__info.channel).encode("utf-8"))
            self.__socket.shutdown(1)
            self.__socket.close()
            self.__ser_conn = False
    def start(self):
        self.__rm = ResponseManager(self.__responses)
        self.__rm.setup(self.__mode, self.__socket)
        self.__rm.setDaemon(True)
        self.__rm.start()
        self.__cm = CommandManager(self.__commands)
        self.__cm.setup(self.__rate, self.__socket)
        self.__cm.setDaemon(True)
        self.__cm.start()
        self.__running = True
    def stop(self):
        self.__rm.stop()
        self.__cm.stop()
        self.__running = False
