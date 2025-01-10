#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time          : 2025/01/09 16:21
# @Author        : sunliangzesmile
# @Email         : sunliangzesmile@gmail.com
# @File          : Tools.py
# @Description   : 工具集
import ctypes,sys,winreg,os,hmac,hashlib
from pymem import pattern as Pattern
from Cryptodome.Cipher import AES
ReadProcessMemory = ctypes.windll.kernel32.ReadProcessMemory
void_p = ctypes.c_void_p


KEY_SIZE = 0x20
DEFAULT_PAGESIZE = 4096
DEFAULT_ITER = 64000
SQLITE_FILE_HEADER = "SQLite format 3\x00"  # SQLite文件头


def readProcessMemory(handle, address, n_size=0x40):
    """
    读取进程内存信息
    """
    array = ctypes.create_string_buffer(n_size)
    if ReadProcessMemory(handle, void_p(address), array, n_size, 0x00) == 0x00: return "None"
    array = bytes(array).split(b"\x00")[0x00] if b"\x00" in array else bytes(array)
    text = array.decode('utf-8', errors='ignore')
    return text.strip() if text.strip() != "" else "None"


def readWeChatAccount(handle,addr,version):
    """
    读取微信账户信息
    """
    return {
         "account": readProcessMemory(handle, addr + version[0x00],0x20) if version[1] != 0x00 else "None",
         "mobile": readProcessMemory(handle, addr + version[0x01],0x40) if version[2] !=  0x00 else "None",
         "name": readProcessMemory(handle, addr + version[0x02],0x40) if version[0] !=  0x00 else "None",
         "mail": readProcessMemory(handle, addr + version[0x03],0x40) if version[3] !=  0x00 else "None",
    }


def readWinReg(route,path):
    """
    读取注册表
    """
    key=None
    try:
        key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, route, 0x00, winreg.KEY_READ)
        value, _ = winreg.QueryValueEx(key, path)
    except:
        value = "MyDocument:"
    finally:
        if key is not None:
            winreg.CloseKey(key)
    return value
     


def pattern_scan_all(handle, pattern, *, return_multiple=False, find_num=100):
    """
    句柄关联文件扫描
    """
    next_region = 0
    found = []
    user_space_limit = 0x7FFFFFFF0000 if sys.maxsize > 2 ** 32 else 0x7fff0000
    while next_region < user_space_limit:
        next_region, page_found =Pattern.scan_pattern_page(
                handle,
                next_region,
                pattern,
                return_multiple=return_multiple
        )
        if not return_multiple and page_found:
            return page_found
        if page_found:
            found += page_found
        if len(found) > find_num:
            break
    return found



def decrypt(dbPath: str, key: str,outPath:str):
    """
    解密数据库
    """
    key = key.strip()
    dbPath = dbPath.strip()
    if not os.path.exists(dbPath) or not os.path.isfile(dbPath):
        return False, f"数据库文件不存在: {dbPath}"
    
    if not key and len(key) != 0x40:
        return False, "密钥不能为空" if not key else "密钥长度不正确"
    
    with open(dbPath, "rb") as f:
        db = f.read()

    salt = db[:0x10]
    if len(db) < 0x10:
        return False, "数据库文件{dbPath}文件错误"
    first=db[0x10:DEFAULT_PAGESIZE]
    password=bytes.fromhex(key)
    byteKey=hashlib.pbkdf2_hmac('sha1', password, salt, DEFAULT_ITER, KEY_SIZE)

    macSalt=bytes([salt[i]^0x3A for i in range(16)])
    macKey=hashlib.pbkdf2_hmac('sha1', byteKey, macSalt, 2, KEY_SIZE)
    hashMac=hmac.new(macKey, first[:-32], hashlib.sha1)
    hashMac.update(b"\x01\x00\x00\x00")
    if hashMac.digest() != first[-32:-12]:
        return False, "数据库文件{dbPath}密钥错误"
    newDb=[db[i:i+DEFAULT_PAGESIZE] for i in range(DEFAULT_PAGESIZE, len(db), DEFAULT_PAGESIZE)]
    # 创建输出文件夹
    if not os.path.exists(os.path.dirname(outPath)):
        os.makedirs(os.path.dirname(outPath))
        
    # 写入解密后的文件
    with open(outPath, "wb") as f:
        f.write(SQLITE_FILE_HEADER.encode())
        t=AES.new(byteKey, AES.MODE_CBC, first[-48:-32])
        decrypted=t.decrypt(first[:-48])
        f.write(decrypted)
        f.write(first[-48:])
        for page in newDb:
            t=AES.new(byteKey, AES.MODE_CBC, page[-48:-32])
            decrypted=t.decrypt(page[:-48])
            f.write(decrypted)
            f.write(page[-48:])
    return True,[dbPath,outPath,key]

