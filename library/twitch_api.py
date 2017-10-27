 # Need to restart this entire part of the library
 # The new api is using purely json objects now and more concise user objects. Finally...
import cfg
import requests

#using the caster secret provided grab the user_id and authenticated client_id of the caster
res = requests.get("https://api.twitch.tv/kraken", headers = {"Accept": "application/vnd.twitchtv.v5+json", "Authorization": "OAuth {}".format(cfg.CASTER_SECRET)})
user_id = res.json()['token']['user_id']
client_id = res.json()['token']['client_id']
# get follows from twitch API includes count and also a sampling of the users
new_res = requests.get("https://api.twitch.tv/kraken/channels/{}/follows".format(user_id), headers = {"Accept": "application/vnd.twitchtv.v5+json", "Client-ID": client_id})
print(new_res.json())
