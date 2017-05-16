from irc_client import IrcClient, IrcInfo, IrcCommand, CommandType, IrcResponse, ResponseType
import types
import cfg

# Currently this file is just a test for the IRC Client

config = IrcInfo(cfg.HOST, cfg.PORT, cfg.NICK, cfg.PASS, cfg.CHAN)
rate = cfg.RATE
channel = cfg.CHAN
name = cfg.NICK

client = IrcClient(config, rate, True)
while client.connected is False:
    pass

args = types.SimpleNamespace()
args.channel = channel
args.username = name
args.message = "Hello Chat!"
client.addCommand_back(IrcCommand(CommandType.message, args))

# need to move this while loop to a ChatSystem class, that is given info to create it's own IrcClient
# also need to make functions out of the command types, to condense code

running = True
while running:
    if client.hasResponses():
        response: IrcResponse = client.getResponse()
        if response.type == ResponseType.ping:
            client.addCommand_front(IrcCommand(CommandType.pong, types.SimpleNamespace()))
        elif response.type == ResponseType.message:
            if response.properties.message == "die":
                args = types.SimpleNamespace()
                args.channel = channel
                args.username = response.properties.username
                args.reason = "Precision of Language"
                args.time = 5
                client.addCommand_back(IrcCommand(CommandType.timeout, args))
            else:
                print("|{}| {}({}): {}".format(response.properties.timestamp, response.properties.username, response.properties.info.user_id, response.properties.message))
        elif response.type == ResponseType.join:
            print("|{}| '{}' joined the chat".format(response.properties.timestamp, response.properties.username))
        elif response.type == ResponseType.part:
            print("|{}| '{}' parted from the chat".format(response.properties.timestamp, response.properties.username))

    # if input() == "exit":
    #     # Initiate Thread Stopping Here
    #     #   -> Need threads to PART from any connections they have to twitch servers
    #     #   -> Need threads that have data, to save them to corresponding files/database
    #     running = False
