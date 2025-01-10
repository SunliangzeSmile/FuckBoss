#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time          : 2025/01/10 11:59
# @Author        : sunliangzesmile
# @Email         : sunliangzesmile@gmail.com
# @File          : BaseDb.py
# @Description   : 微信数据库
import os
from sqlmodel import Field, SQLModel,create_engine,Session,select

class WechatDB(SQLModel, table=False):
    """
    微信数据库
    """
    __engine__ =None
    __isOpen__=False
    def __init__(self,path:str,**kwargs):
        self.__isOpen__=False
        self.__initDatabase__(path,**kwargs)
    
    def __initDatabase__(self,path:str,**kwargs):
        """
        初始化数据库
        """
        if not os.path.exists(path):
            raise Exception("数据库文件不存在")
        self.__engine__=create_engine(f"sqlite:///{path}")
        self.__isOpen__=True


    def query(self,*filter):
        """
        数据查询
        """
        if not self.__isOpen__:
            raise Exception("数据库未打开")
        with Session(self.__engine__) as session:
            statement = select(self.__class__)
            result = session.exec(statement).all()
        return result

        

