#! /usr/bin/env python
#coding:utf-8

from sqlalchemy import Column, Integer, String, Text, ForeignKey, DateTime, Boolean, create_engine
from sqlalchemy.orm import sessionmaker, relationship
from sqlalchemy.ext.declarative import declarative_base
from .settings import DBSETTINGS
from datetime import datetime
import urllib.request
import socket
import struct

Base = declarative_base()

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
      self.last_login_ip = urllib.request.urlopen('https://ident.me').read().decode('utf8')
      self.degree = -1
      self.exp = 0
      self.nationality = ''
    
    def __repr__(self):
        return "<User('%s')>" % (self.username)

class XpEvents(Base):
    __tablename__ = 'xp_events'
    
    xp_events_id = Column(Integer, primary_key=True)
    level = Column(Integer,nullable=False)
    min_xp = Column(Integer)
    
    def __repr__(self):
        return "<XpEvents('%s')>" % (self.level)

class ProjectGroup(Base):
    __tablename__ = 'project_group'
    
    project_group_id = Column(Integer, primary_key=True)
    project_group_name = Column(Text, nullable=False)
    
    def __init__(self, project_group_name):
        self.project_group_name = project_group_name
    
    def __repr__(self):
        return "<ProjectGroup('%s')>" % (self.project_group_name)

class Project(Base):
    __tablename__ = 'project'
    
    project_id = Column(Integer, primary_key=True)
    project_name = Column(String, nullable=False)
    created_on = Column(DateTime, nullable=False)
    project_project_group_id = Column(Integer,ForeignKey('project_group.project_group_id'))
    
    pproject_group = relationship('ProjectGroup', backref='project')
    
    def __init__(self, project_name, project_project_group_id):
        self.project_name = project_name
        self.created_on = datetime.now()
        self.project_project_group_id = project_project_group_id
        
    def __repr__(self):
        return "<Project('%s')>" % (self.project_name)

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