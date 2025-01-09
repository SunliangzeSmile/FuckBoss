from engine import Wechat


if __name__ == '__main__':
    wechat=Wechat()
    info=wechat.getInfo()
    print(info)