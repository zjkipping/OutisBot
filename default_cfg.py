# When file is edited to your liking, rename to "cfg.py"
HOST   = "irc.twitch.tv" # The "Twitch IRC" server
PORT   = 6667 # Always use port 6667!
NICK   = "" # Your bot's twitch username (lowercase)
PASS   = "" # Your bot's twitch oauth token
SECRET = "" # Your bot's client_id/secret for api.twitch.tv
CHAN   = "#" # The channel you want to join (must include # in front of it)
RATE   = (20/30) # messages per second (100/30 if mod in channel, 20/30 else wise)
CHAT   = 'http://tmi.twitch.tv/group/user/<channel>/chatters' # link to your channel's user list (possibly outdated refer to SECRET)
PATT   = [ # Words/patterns to timeout/ban a user for, use template below
             r"word",
             r"^pattern$" # Using RegEx patterns
         ]
