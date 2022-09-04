from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker
from sqlalchemy.ext.declarative import declarative_base


engine = create_engine("mysql+pymysql://root:123456@39.104.53.248:3306/test?charset=utf8")
db_session = scoped_session(sessionmaker(autocommit=False, autoflush=False, bind=engine))
Base = declarative_base()
Base.query = db_session.query_property()
from sqlalchemy import Column, Integer, String,DateTime,Text,ForeignKey

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

# Base.metadata.drop_all(bind=engine)
Base.metadata.create_all(bind=engine)
# u = User('bell','dhsfkjchzx')
# db_session.add(u)
# db_session.commit()
# db_session.query(User).filter(User.id==1).delete()
#
# db_session.commit()
res=db_session.query(User).filter(User.id==2).first()
res.username='title'
res.password='content'
db_session.add(res)
db_session.commit()
