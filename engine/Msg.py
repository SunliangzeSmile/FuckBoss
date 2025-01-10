#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time          : 2025/01/10 17:08
# @Author        : sunliangzesmile
# @Email         : sunliangzesmile@gmail.com
# @File          : Msg.py
# @Description   : 微信文本消息
from .BaseDb import WechatDB
from typing import Optional
from sqlmodel import Field


class WeChatMsg(WechatDB, table=True):
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


