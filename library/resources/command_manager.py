import threading, socket
from collections import deque
from types import SimpleNamespace
from library.resources.common import IrcCommand, IrcCommandType

def sendPong(connection: socket):
    connection.send("PONG :tmi.twitch.tv\r\n".encode("utf-8"))
def sendMessage(args: SimpleNamespace, connection: socket):
    connection.send("PRIVMSG #{} :{}\r\n".format(args.channel, args.message).encode("utf-8"))
def sendTimeout(args: SimpleNamespace, connection: socket):
    connection.send("PRIVMSG #{} :.timeout {} {} {}\r\n".format(args.channel, args.username, args.duration, args.reason).encode("utf-8"))
def sendBan(args: SimpleNamespace, connection: socket):
    connection.send("PRIVMSG #{} :.ban {} {}\r\n".format(args.channel, args.username, args.reason).encode("utf-8"))
def dispatchCommand(command: IrcCommand, connection: socket):
    if command.type == IrcCommandType.pong:
        sendPong(connection)
    elif command.type == IrcCommandType.message:
        sendMessage(command.args, connection)
    elif command.type == IrcCommandType.timeout:
        sendTimeout(command.args, connection)
    elif command.type == IrcCommandType.ban:
        sendBan(command.args, connection)

class CommandManager(threading.Thread):
    def __init__(self, _commands: deque):
        super(CommandManager, self).__init__()
        self.__commands = _commands
        self.__rate = 20/30
        self.__connection = socket.socket()
        self.__running = True
    def setup(self, _rate, _connection):
        self.__rate = _rate
        self.__connection = _connection
    def run(self):
        while self.__running:
            if len(self.__commands) != 0:
                command: IrcCommand = self.__commands.popleft()
                dispatchCommand(command, self.__connection)
        self.__endSequence()
    def stop(self):
        self.__running = False
    def __endSequence(self):
        while len(self.__commands) != 0:
            command: IrcCommand = self.__commands.popleft()
            dispatchCommand(command, self.__connection)
