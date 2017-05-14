from irc_client import IrcClient, IrcInfo, IrcCommand, CommandType, IrcResponse, ResponseType
import types
import cfg

config = IrcInfo(cfg.HOST, cfg.PORT, cfg.NICK, cfg.PASS, cfg.CHAN)
rate = cfg.RATE
channel = cfg.CHAN

client = IrcClient(config, rate, True)
while client.connected is False:
    pass

args = types.SimpleNamespace()
args.channel = channel
args.message = "Hello Chat!"
client.addCommand_front(IrcCommand(CommandType.message, args))

# need to move this while loop to a ChatSystem class, that is given info to create it's own IrcClient
running = True
while running:
    if client.hasResponses():
        response:IrcResponse = client.getResponse()
        if response.type == ResponseType.ping:
            client.addCommand_front(IrcCommand(CommandType.pong, types.SimpleNamespace()))
        elif response.type == ResponseType.message:
             print("{}: {}".format(response.properties.username, response.properties.message))

    # if input() == "exit":
    #     # Initiate Thread Stopping Here
    #     #   -> Need threads to PART from any connections they have to twitch servers
    #     #   -> Need threads that have data, to save them to corresponding files/database
    #     running = False
