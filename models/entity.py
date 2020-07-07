#! /usr/bin/env python
#coding:utf-8

from sqlalchemy import Column, Integer, String, Text, ForeignKey, DateTime, Boolean, create_engine
from sqlalchemy.orm import sessionmaker, relationship
from sqlalchemy.ext.declarative import declarative_base
from .settings import DBSETTINGS
from datetime import datetime
import socket
import fcntl
import struct

Base = declarative_base()

def get_ip_address(ifname):
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    return socket.inet_ntoa(fcntl.ioctl(
        s.fileno(),
        0x8915,  # SIOCGIFADDR
        struct.pack('256s', ifname[:15])
    )[20:24])

class Account(Base):
    __tablename__ = 'account'
    
    user_id = Column(Integer, primary_key=True)
    username = Column(String, nullable=False)
    password = Column(String, nullable=False)
    email = Column(String)
    phone_number = Column(String)
    line_id = Column(String)
    wechat_id = Column(String)
    skype_id = Column(String)
    created_on = Column(DateTime, nullable=False)
    last_login = Column(DateTime)
    last_login_ip = Column(String)
    degree = Column(Integer)
    exp = Column(Integer)
    nationality = Column(String)
    
    def __init__(self, username, password, email):
      self.username = username
      self.password = password
      self.email = email
      self.phone_number = ''
      self.line_id = ''
      self.wechat_id = ''
      self.skype_id = ''
      self.created_on = datetime.now()
      self.last_login = datetime.now()
      self.last_login_ip = get_ip_address('eth0')
      self.degree = -1
      self.exp = 0
      self.nationality = ''
    
    def __repr__(self):
        return "<User('%s')>" % (self.username)

def getDBURL():
   return 'postgresql+psycopg2://%s:%s@%s:%d/%s' % (DBSETTINGS['db_user'], DBSETTINGS['db_password'], DBSETTINGS['db_host'], DBSETTINGS['db_port'], DBSETTINGS['db_name'])

class DB_Session(object):
    def __init__(self):
        engine = create_engine(getDBURL())
        self.Session = sessionmaker(bind=engine)

    @property
    def getSession(self):
        return self.Session()

db_session = DB_Session()