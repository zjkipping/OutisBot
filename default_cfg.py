HOST = "irc.twitch.tv" # the Twitch IRC server
PORT = 6667 # always use port 6667!
NICK = "" # your Bot's Twitch username, lowercase
PASS = "" # your Bot's Twitch OAuth token
CHAN = "#<channel>" # the channel you want to join
RATE = (100/30) # messages per second
CHATTERS = 'http://tmi.twitch.tv/group/user/<channele>/chatters' # link to your channel's user list
PATT = [ # words/patterns to timeout/ban a user for use template below (r"<word>")
    r"word",
    r"^pattern$" # Using RegEx patterns
]
