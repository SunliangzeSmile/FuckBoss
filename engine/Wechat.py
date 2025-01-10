#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time          : 2025/01/09 14:30
# @Author        : sunliangzesmile
# @Email         : sunliangzesmile@gmail.com
# @File          : Wechat.py
# @Description   : 微信信息

import binascii,os
from pymem import Pymem,process,pattern
from win32api import GetFileVersionInfo, HIWORD, LOWORD
from .Tools import readProcessMemory,readWeChatAccount,pattern_scan_all,readWinReg

class Wechat:
    """
    微信信息
    """
    def __init__(self,**kwargs):
        self.pm=Pymem("WeChat.exe")
        self.handle=self.pm.process_handle
        module=process.module_from_name(self.handle,"WeChatWin.dll")
        self.baseAddr=module.lpBaseOfDll
        self.imageSize=module.SizeOfImage
        self.machineBits=self.getMachineBit()


    def getMachineBit(self):
        """
        获取机器位数 64 or 32
        """
        address=self.baseAddr+self.pm.read_int(self.baseAddr+0x3C)+0x14
        sizeOfOptionalHeader=self.pm.read_short(address)
        return 0x40 if sizeOfOptionalHeader==0xF0 else 0x20
    
    def getVersion(self,**kwargs):
        """
        获取微信版本
        """
        applicationPath=None
        for module in self.pm.list_modules():
            if module.filename.endswith("WeChatWin.dll"):
                applicationPath=module.filename
                break
        if applicationPath is None:
            return False

        version = GetFileVersionInfo(applicationPath, "\\")
        msv = version['FileVersionMS']
        lsv = version['FileVersionLS']
        return f"{str(HIWORD(msv))}.{str(LOWORD(msv))}.{str(HIWORD(lsv))}.{str(LOWORD(lsv))}"
    

    def searchMemoryFeature(self,parent,child,**kwargs):
        """
        内存特征搜索
        """
        offset=[]
        index=-1
        while True:
            index=parent.find(child,index+1)
            if index==-1:
                break
            offset.append(index)
        return offset
    
    def checkKey(self,key,**kwargs):
        """
        检查公钥
        """
        if key is None or len(key)!=self.machineBits:
            return False
        else:
            return True

    
    def getKeyAddr(self,list=[],**kwargs):
        """
        获取公钥地址
        """
        result=[]
        buffer=self.pm.read_bytes(self.baseAddr,self.imageSize)
        byteLength=0x04 if self.machineBits==0x20 else 0x08
        for pubkey in list:
            keyBytes=pubkey.to_bytes(byteLength,byteorder='little',signed=True)
            offset=self.searchMemoryFeature(buffer,keyBytes)
            if offset is None or len(offset)==0x00:
                continue
            else:
                offset[:]=[x+self.baseAddr for x in offset]
                result+=offset
        return None if len(result)==0x00 else result

    def getInfo(self,**kwargs):
        """
        获取微信信息
        """
        version=self.getVersion()
        if version is False or version is None:
            print("微信版本获取失败")
            return

        pubKey=b'-----BEGIN PUBLIC KEY-----\n...'
        # 在内存中扫描公钥地址
        pubKeys=pattern.pattern_scan_all(self.pm.process_handle,pubKey, return_multiple=True)
        if len(pubKeys)==0x00:
            print("公钥获取失败")
            return
        else:
            pass
        
        pubKeyAddrs=self.getKeyAddr(pubKeys)
        keyLenOffset=0x8c if self.machineBits==0x20 else 0xd0
        key=None
        if pubKeyAddrs is None or len(pubKeyAddrs)==0x00:
            print("公钥地址获取失败")
            return
        else:
            for pubAddr in pubKeyAddrs:
                keyLen=self.pm.read_uchar(pubAddr-keyLenOffset)
                if self.machineBits==0x20:
                    key=self.pm.read_bytes(self.pm.read_int(pubAddr-0x90),keyLen)
                else:
                    key=self.pm.read_bytes(self.pm.read_longlong(pubAddr-0xd8),keyLen)
                key=binascii.b2a_hex(key).decode()

                if self.checkKey(key):
                    break
        wxid=self.getWxid(self.handle)
        return {
            'version': version,
            'pid': self.pm.process_id,
            'key': key,
            'wxid': wxid,
            'storePath': self.getStorePath(wxid)
            }
    
    def getWxid(self,handle):
        """
        获取登录的微信ID
        """
        find_num = 100
        addrs = pattern_scan_all(handle, br'\\Msg\\FTSContact', return_multiple=True, find_num=find_num)
        wxids = []
        for addr in addrs:
            result=readProcessMemory(handle,addr-0x1c,80)
            result = result.split("\\Msg")[0]
            result = result.split("\\")[-1]
            wxids.append(result)
        wxid = max(wxids, key=wxids.count) if wxids else "None"
        return wxid
    
    def getDefaultStorePath(self,wdir=None):
        """
          获取微信默认文件目录
        """
        if not wdir:
            user_profile = os.environ.get("USERPROFILE")
            path_3ebffe94 = os.path.join(user_profile, r"AppData\Roaming\Tencent\WeChat\All Users\config\3ebffe94.ini")
            with open(path_3ebffe94, "r", encoding="utf-8") as f:
                wdir = f.read()
        #读取文档实际目录路径
        documents_path =readWinReg(r"Software\Microsoft\Windows\CurrentVersion\Explorer\User Shell Folders","Personal")
        documents_paths = os.path.split(documents_path)
        if "%" in documents_paths[0]:
            wdir = os.environ.get(documents_paths[0].replace("%", ""))
            wdir = os.path.join(wdir,os.path.join(*documents_paths[1:]))
        else:
            wdir = documents_path
        return os.path.join(wdir, "WeChat Files")
    
    def getStorePath(self,wxid="all"):
        """
        获取微信文件目录
        """
        if not wxid:
            return "None"
        w_dir = readWinReg(r"Software\Tencent\WeChat", "FileSavePath")
        is_w_dir = True if w_dir == "MyDocument:" else False
        if not is_w_dir:
            w_dir=self.getDefaultStorePath()
        else:
            w_dir = self.getDefaultStorePath(w_dir)

        if wxid == "all" and os.path.exists(w_dir):
            return w_dir

        filePath = os.path.join(w_dir, wxid)
        return filePath if os.path.exists(filePath) else "None"
    

    def current(self,versions,**kwargs):
        """
          获取当前登录微信信息
        """
        info=self.getInfo()
        version=versions.get(info['version'],None)
        account=readWeChatAccount(self.handle,self.baseAddr,version);
        return {**info,**account}