from sqlalchemy import Column, Integer, String,DateTime,Text,ForeignKey
from test import Base
import datetime


class User(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True)
    username = Column(String(255), unique=True)
    password = Column(String(255), unique=True)

    def __init__(self, username=None, password=None):
        self.username = username
        self.password = password

    def __repr__(self):
        return f'<User 用户id={self.id!r},用户名称={self.username!r}>'

class Blog(Base):
    __tablename__ = 'blogs'
    id = Column(Integer, primary_key=True)
    title = Column(String(255), unique=True)
    content = Column(String(255), unique=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    datetime=Column(String(255), unique=True)

    def __init__(self,title=None,content=None,user_id=None,datetime=None):
        self.title=title
        self.content=content
        self.user_id = user_id
        self.datetime=datetime

    def __repr__(self):
        return f'<Blog 博客id={self.id!r},博客标题={self.title!r}>'
