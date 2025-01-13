#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time          : 2025/01/10 11:59
# @Author        : sunliangzesmile
# @Email         : sunliangzesmile@gmail.com
# @File          : BaseDb.py
# @Description   : 微信数据库
import os
from dataclasses import dataclass, fields
from sqlmodel import Field, SQLModel,create_engine,Session,select

@dataclass
class WeChatDB(SQLModel, table=False):
    """
    微信数据库
    """
    __engine__ =None
    __isOpen__=False
    __fields__=dict()
    def __init__(self,path:str,**kwargs):
        super(SQLModel,self).__init__(**kwargs)
        self.__isOpen__=False
        self.__initDatabase__(path,**kwargs)
        for field in fields(self.__class__):
            self.__fields__[field.name]=field
    
    def __initDatabase__(self,path:str,**kwargs):
        """
        初始化数据库
        """
        if not os.path.exists(path):
            raise Exception("数据库文件不存在")
        self.__engine__=create_engine(f"sqlite:///{path}")
        self.__isOpen__=True


    def query(self,**kwargs):
        """
        数据查询
        """
        if not self.__isOpen__:
            raise Exception("数据库未打开")
        with Session(self.__engine__) as session:
            statement = select(self.__class__)
            statement=self.__build_filter__(statement,**kwargs)
            result = session.exec(statement).all()
        return result
    

    def __build_filter__(self,statement,**kwargs):
        """
        构建查询条件
        """
        for key,value in kwargs.items():
            field=self.__fields__[key]
            if isinstance(value,dict): # 字典查询
                if 'type' in value and 'value' in value:
                    typeText=value['type'].lower()
                    if typeText == 'range' and isinstance(value['value'],list):
                        statement=self.__build_filter__(statement,**{key:value['value']})
                    elif typeText == 'in' and isinstance(value['value'],list):
                        statement=statement.where(field.default.in_(value['value']))
            elif isinstance(value,list): # range查询
                if len(value)>=1:
                    statement=statement.where(field.default>=value[0])
                if len(value)>=2:
                    statement=statement.where(field.default<=value[-1])
            else: # 等值查询
                statement=statement.where(field.default==value)
        return statement
    





        

