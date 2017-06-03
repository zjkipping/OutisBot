# When file is edited to your liking, rename to "cfg.py"

HOST          = "irc.twitch.tv" # The "Twitch IRC" server
PORT          = 6667 # Always use port 6667!
NICK          = "" # Your bot's twitch username (lowercase)
BOT_SECRET    = "" # Your bot's twitch oauth token
CASTER_SECRET = "" # The caster's twitch oauth token (for api.twitch.tv calls)
CHAN          = "" # The channel you want to join (must lowercase)
RATE          = (20/30) # messages per second (100/30 if mod in channel, 20/30 else wise)
PATT          = [ # Words/patterns to timeout/ban a user for, use template below
                    r"word",
                    r"^pattern$" # Using RegEx patterns
                ]

# Keeping the config as a .py file for now, because of the convenience in importing.
#   - Need to swap this over to (probably) json eventually
