import socket
import time
from enum import Enum
import threading
from collections import deque

class CommandType(Enum):
    message = 1
    timeout = 2
    ban = 3
    pong = 4

class Command:
    type: CommandType
    payload: object

    def __init__(self, _type, _payload):
        self.type = _type
        self.payload = _payload

class QueueCommandSystem(threading.Thread):
    s: socket
    queue: deque
    rate: float

    def __init__(self, _s, _queue, _rate):
        super(QueueCommandSystem, self).__init__()
        self.s = _s
        self.queue = _queue
        self.rate = _rate

    def run(self):
        while True:
            if len(self.queue) != 0:
                command : Command = self.queue.popleft()
                if command.type == CommandType.message:
                    send_message(self.s, command.payload)
                elif command.type == CommandType.timeout:
                    timeout_user(self.s, command.payload)
                elif command.type == CommandType.ban:
                    ban_user(self.s, command.payload)
                elif command.type == CommandType.pong:
                    send_pong(self.s)
                time.sleep(1 / self.rate)

def send_message(s: socket, payload: object):
    s.send("PRIVMSG {} :{}\r\n".format(payload["channel"], payload["message"]).encode("utf-8"))

def ban_user(s: socket, payload: object):
    print("Banned User {} for {}".format(payload["username"], payload["reason"]))
    s.send("PRIVMSG {} :.ban {} {}\r\n".format(payload["channel"], payload["username"], payload["reason"]).encode("utf-8"))

def timeout_user(s: socket, payload: object):
    print("Timed Out User {} for {}".format(payload["username"], payload["reason"]))
    s.send("PRIVMSG {} :.timeout {} {} {}\r\n".format(payload["channel"], payload["username"], payload["time"], payload["reason"]).encode("utf-8"))

def send_pong(s: socket):
    print("Received PING, responding with PONG")
    s.send("PONG :tmi.twitch.tv\r\n".encode("utf-8"))
