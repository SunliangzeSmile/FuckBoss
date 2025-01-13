#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time          : 2025/01/10 17:08
# @Author        : sunliangzesmile
# @Email         : sunliangzesmile@gmail.com
# @File          : Msg.py
# @Description   : 微信实体
from .BaseDb import WeChatDB
from typing import Optional
from sqlmodel import Field

from dataclasses import dataclass

@dataclass
class WeChatContact(WeChatDB, table=True):
    """
    微信通讯录
    """
    __tablename__ = 'FTSContact15_content'
    docid:Optional[int] = Field(default=None,primary_key=True)
    c0alias:Optional[str] = Field(default=None)
    c1nickname:Optional[str] = Field(default=None)
    c2remark:Optional[str] = Field(default=None)


class WeChatMsg(WeChatDB, table=True):
    """
    微信消息
    """
    __tablename__ = 'MSG'
    localId:Optional[int] = Field(default=None,primary_key=True)
    talkerId:Optional[int] = Field(default=None)
    type:Optional[int] = Field(default=None)
    subType:Optional[int] = Field(default=None)
    isSender:Optional[int] = Field(default=None)
    createTime:Optional[int] = Field(default=None)
    status:Optional[int] = Field(default=None)
    strTalker:Optional[str] = Field(default=None)
    strContent:Optional[str] = Field(default=None)
    msgSvrID:Optional[int] = Field(default=None)
    displayContent:Optional[str] = Field(default=None)


    def __init__(self,path):
        super(WeChatMsg,self).__init__(path)


