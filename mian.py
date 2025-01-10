from engine import Wechat
import json
VERSION_LIST_PATH = "version_list.json"
VERSION_LIST=None

with open(VERSION_LIST_PATH, "r", encoding="utf-8") as f:
    VERSION_LIST = json.load(f)


if __name__ == '__main__':
    wechat=Wechat()
    info=wechat.current(VERSION_LIST)
    print(info)