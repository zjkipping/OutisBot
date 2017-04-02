HOST = "irc.twitch.tv" # the Twitch IRC server
PORT = 6667 # always use port 6667!
NICK = "OutisBot" # your Bot's Twitch username, lowercase
PASS = "oauth:ski5v46el29vm1qv4vc1vtgxz9ok9d" # your Bot's Twitch OAuth token
CHAN = "#the_outis" # the channel you want to join
RATE = (100/30) # messages per second
CHATTERS = 'http://tmi.twitch.tv/group/user/the_outis/chatters' # link to your channel's user list
PATT = [ # words/patterns to timeout/ban a user for use template below (r"<word>")
    r"die",
    r"death"
]
