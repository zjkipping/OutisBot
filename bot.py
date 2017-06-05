import time, cfg
from library.irc_client import IrcClient
from types import SimpleNamespace
from library.resources.common import IrcInfo, IrcCommand, IrcCommandType, IrcResponse, IrcResponseType

info = IrcInfo(cfg.HOST, cfg.PORT, cfg.NICK, cfg.BOT_SECRET, cfg.CHAN)
client = IrcClient(info, True, cfg.RATE)
timeout = [1, 2, 2, 2, 4, 4, 4, 8, 8, 8, 16, 16, 16, 32, 32, 32, 64]
count = 0
while client.hasInternetConnection() is False:
    print("No Internet Connection ... timeout: {}".format(timeout[count]))
    time.sleep(timeout[count])
    if count < len(timeout) - 1:
        count += 1
count = 0
client.connect()
while client.hasServerConnection() is False:
    print("Failed to connect to Twitch IRC Server ... timeout: {}".format(timeout[count]))
    client.disconnect()
    time.sleep(timeout[count])
    if count < len(timeout) - 1:
        count += 1
    client.connect()
client.start()
print("Bot Connected Successfully")
while True:
    while client.hasServerConnection() is True and client.hasInternetConnection() is True:
        if client.hasResponses():
            response: IrcResponse = client.getResponse()
            if response.type == IrcResponseType.ping:
                client.addCommandLeft(IrcCommand(IrcCommandType.pong, SimpleNamespace()))
                print("Responded to Ping!")
            elif response.type == IrcResponseType.message:
                if response.args.message == "ban me":
                    args = SimpleNamespace()
                    args.channel = info.channel
                    args.username = response.args.login
                    args.reason = "Precision of Language"
                    # client.addCommandRight(IrcCommand(IrcCommandType.ban, args))
                elif response.args.message == "time me out":
                    args = SimpleNamespace()
                    args.channel = info.channel
                    args.username = response.args.login
                    args.duration = 5
                    args.reason = "Precision of Language"
                    # client.addCommandRight(IrcCommand(IrcCommandType.timeout, args))
                else:
                    # print("({}) {}: {}".format(response.timestamp, response.args.display, response.args.message))
                    '''getting user messages from chat'''
            elif response.type == IrcResponseType.whisper:
                '''dealing with whispers from users'''
                print("WHISPER ({}) {}: {}".format(response.timestamp, response.args.display, response.args.message))
            elif response.type == IrcResponseType.cheer:
                args = SimpleNamespace()
                args.message = "Thanks for the {} bit cheer, {}!".format(response.args.amount, response.args.display)
                args.channel = info.channel
                print("{} bits - {}".format(response.args.amount, response.args.display))
                # client.addCommandRight(IrcCommand(IrcCommandType.message, args))
            elif response.type == IrcResponseType.subscribe:
                args = SimpleNamespace()
                if response.args.type == "sub":
                    args.message = "Thanks {} for subscribing to the channel!".format(response.args.display)
                    args.channel = info.channel
                    print("{} subscribed".format(response.args.display))
                else:
                    args.message = "{} subscribed for {} months in a row. Thanks for the continued support!".format(response.args.display, response.args.duration)
                    args.channel = info.channel
                    print("{} re-subscribed for {} months".format(response.args.display, response.args.duration))
                # client.addCommandRight(IrcCommand(IrcCommandType.message, args))
    if client.hasInternetConnection() is False:
        count = 0
        client.disconnect()
        client.stop()
        while client.hasInternetConnection() is False:
            print("No Internet Connection ... timeout: {}".format(timeout[count]))
            time.sleep(timeout[count])
            if count < len(timeout) - 1:
                count += 1
        print("Internet Connection Back Up!")
    elif client.hasServerConnection() is False:
        count = 0
        if client.isRunning() is True:
            client.disconnect()
            client.stop()
        client.connect()
        while client.hasServerConnection() is False:
            client.disconnect()
            print("Failed to connect to Twitch IRC Server ... timeout: {}".format(timeout[count]))
            time.sleep(timeout[count])
            if count < len(timeout) - 1:
                count += 1
            client.connect()
        client.start()
        print("Reconnected To Twitch IRC Server!")
