import chat_users
import socket
import cfg
import re
from collections import deque
from chat_reader import ChatInterpreter
from command_issuer import QueueCommandSystem
from threading import Thread

# ALl of this needs to be pushed into the IRC Client system
s = socket.socket()
s.connect((cfg.HOST, cfg.PORT))
s.send("PASS {}\r\n".format(cfg.PASS).encode("utf-8"))
s.send("NICK {}\r\n".format(cfg.NICK).encode("utf-8"))
s.send("JOIN {}\r\n".format(cfg.CHAN).encode("utf-8"))
s.setblocking(0)
response = ""
while re.search(r"\bJOIN\b", response) is None :
    try:
        response = s.recv(1024).decode("utf-8")
    except socket.error:
        '''No Responses Yet'''
#
print("<----------  Connected to Chat  ---------->")

queue = deque([])
chat_interpreter = ChatInterpreter(s, queue, cfg.CHAN, cfg.PATT)
chat_interpreter.setDaemon(True)
chat_interpreter.start()
queue_system = QueueCommandSystem(s, queue, cfg.RATE)
queue_system.setDaemon(True)
queue_system.start()

# Need to make these into Class based threads to overwrite the default functionality
t1 = Thread(target = chat_users.run)
t1.setDaemon(True)
t1.start()
# -----

running = True
while running :
    if input() == "exit":
        # Initiate Thread Stopping Here
        #   -> Need threads to PART from any connections they have to twitch servers
        #   -> Need threads that have data, to save them to corresponding files/database
        running = False
