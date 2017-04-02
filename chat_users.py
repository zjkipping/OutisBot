import cfg
import requests
import time
from munch import munchify
from enum import Enum

class ViewerType(Enum):
    normal = 1
    moderator = 2
    staff = 3


class Viewer:
    username: str
    type: ViewerType

    def __init__(self, _username, _type):
        self.username = _username
        self.type = _type

def run():
    while True:
        old_viewer_list: list = []
        viewer_list: list = []
        r = requests.get(cfg.CHATTERS)
        chat_data = munchify(r.json())
        if viewer_list is not None:
            old_viewer_list = viewer_list
        viewer_list = buildUserList(chat_data.chatters, chat_data.chatter_count)
        time.sleep(1)

def buildUserList(chatter_data, count):
    viewers: list = []
    for staff_member in chatter_data.staff:
        viewers.append(Viewer(staff_member, ViewerType.staff))
    for global_mod in chatter_data.global_mods:
        viewers.append(Viewer(global_mod, ViewerType.staff))
    for admin in chatter_data.admins:
        viewers.append(Viewer(admin, ViewerType.staff))
    for moderator in chatter_data.moderators:
        viewers.append(Viewer(moderator, ViewerType.moderator))
    for viewer in chatter_data.viewers:
        viewers.append(Viewer(viewer, ViewerType.normal))
    return viewers
