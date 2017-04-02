import socket
import re
import threading
from collections import deque
from command_issuer import CommandType, Command

class ChatInterpreter(threading.Thread):
    s: socket
    queue: deque
    channel: str
    patterns: list

    def __init__(self, _s, _queue, _channel, _patterns):
        super(ChatInterpreter, self).__init__()
        self.s = _s
        self.queue = _queue
        self.channel = _channel
        self.patterns = _patterns

    def run(self):
        while True :
            try :
                response = self.s.recv(1024).decode("utf-8")
                if response == "PING :tmi.twitch.tv\r\n" :
                    self.queue.appendleft(Command(CommandType.pong, {}))
                else :
                    checkCommands(response, self.channel, self.queue, self.patterns)
            except socket.error :
                '''No Responses Yet'''

def checkCommands(response, channel: str, queue: deque, patterns: list):
    CHAT_MSG = re.compile(r"^:\w+!\w+@\w+\.tmi\.twitch\.tv PRIVMSG #\w+ :")
    SMACK_COMMAND = re.compile(r"^!smack \w+$")
    HELLO_COMMAND = re.compile(r"^!hello$")
    username = re.search(r"\w+", response).group(0)
    message = CHAT_MSG.sub("", response).rstrip()
    if not languagePrecisionTest(patterns, message) :
        queue.insert(1, Command(CommandType.timeout, {'channel': channel, 'username': username, 'time': 60, 'reason': "Precision of Language"}))
    else:
        print("{}: {}".format(username, message))
        if re.match(HELLO_COMMAND, message):
            print("<-- Command Hit: <!hello> -->")
            queue.append(Command(CommandType.message, {'channel': channel, 'message': "Hello, {}!".format(username)}))
        elif re.match(SMACK_COMMAND, message):
            person = message.split()[1]
            print("<-- Command Hit: <!smack [person]> -->")
            queue.append(Command(CommandType.message, {'channel': channel, 'message': "/me smacked {}!".format(person)}))

def languagePrecisionTest(patterns: list, message: str):
    for pattern in patterns:
        if re.match(pattern, message):
            return False
    return True
