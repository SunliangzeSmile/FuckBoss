#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time          : 2025/01/09 16:21
# @Author        : sunliangzesmile
# @Email         : sunliangzesmile@gmail.com
# @File          : Tools.py
# @Description   : 工具集
import ctypes,sys,winreg,os
from pymem import pattern as Pattern
ReadProcessMemory = ctypes.windll.kernel32.ReadProcessMemory
void_p = ctypes.c_void_p


def readProcessMemory(handle, address, n_size=64):
    """
    读取进程内存信息
    """
    array = ctypes.create_string_buffer(n_size)
    if ReadProcessMemory(handle, void_p(address), array, n_size, 0) == 0: return "None"
    array = bytes(array).split(b"\x00")[0] if b"\x00" in array else bytes(array)
    text = array.decode('utf-8', errors='ignore')
    return text.strip() if text.strip() != "" else "None"


def readWeChatAccount(handle,addr,version):
    """
    读取微信账户信息
    """
    return {
         "account": readProcessMemory(handle, addr + version[0],32) if version[1] != 0 else "None",
         "mobile": readProcessMemory(handle, addr + version[1],64) if version[2] != 0 else "None",
         "name": readProcessMemory(handle, addr + version[2],64) if version[0] != 0 else "None",
         "mail": readProcessMemory(handle, addr + version[3],64) if version[3] != 0 else "None",
    }


def readWinReg(route,path):
    """
    读取注册表
    """
    key=None
    try:
        key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, route, 0, winreg.KEY_READ)
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

