from engine import Wechat,WeChatMsg,WeChatContact
import json
VERSION_LIST_PATH = "version_list.json"
VERSION_LIST=None

with open(VERSION_LIST_PATH, "r", encoding="utf-8") as f:
    VERSION_LIST = json.load(f)


if __name__ == '__main__':
    # 读取微信
    # wechat=Wechat()
    # info=wechat.current(VERSION_LIST)
    # wechat.transform(info['key'],info['wxid'],info['wxid'])
    # print(info)
    # 读取微信消息
    # msg=WeChatMsg(r'laibazanliaohui\MSG0.db')
    # messages=msg.query(WeChatMsg.strTalker=='34711172551@chatroom')
    # print(messages)

    contact=WeChatContact(r'laibazanliaohui\FTSContact.db')
    result=contact.query(docid=[95,98])
    print(result)