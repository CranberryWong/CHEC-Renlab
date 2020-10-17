#! /usr/bin/env python
#coding:utf-8

from sqlalchemy import Column, Integer, String, Text, ForeignKey, DateTime, Boolean, create_engine
from sqlalchemy.orm import sessionmaker, relationship, backref
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.ext.associationproxy import association_proxy
from .settings import DBSETTINGS
from datetime import datetime
from datetime import timedelta
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
    
    projects=association_proxy('project_member','project')
    
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
    project_group_id = Column(Integer,ForeignKey('project_group.project_group_id'))
    
    pproject_group = relationship('ProjectGroup', backref='project')
    
    def __init__(self, project_name, project_group_id):
        self.project_name = project_name
        self.created_on = datetime.now()
        self.project_group_id = project_group_id
        
    def __repr__(self):
        return "<Project('%s')>" % (self.project_name)

class ProjectMember(Base):
    __tablename__ = 'project_member'
    
    project_member_id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('account.user_id'))
    project_id = Column(Integer, ForeignKey('project.project_id'))
    
    # bidirectional attribute/collection of "user"/"project_member"
    user = relationship(Account, backref=backref("project_member", cascade="all, delete-orphan"))
    
    #reference to the "Project" object
    project = relationship('Project')
    
    def __init__(self, user_id, project_id):
        self.user_id = user_id
        self.project_id = project_id

class WeeklyReport(Base):
    __tablename__ = 'weekly_report'
    
    weekly_report_id = Column(Integer, primary_key=True)
    date_range_start = Column(DateTime, nullable=False)
    date_range_end = Column(DateTime, nullable=False)
    
    def __init__(self, date_range_start):
        self.date_range_start = date_range_start
        self.date_range_end = date_range_start + timedelta(days=6)
        
    def __repr__(self):
        return "<WeeklyReport('%s')>" % (self.date_range_start)
    
class Reflection(Base):
    __tablename__ = 'reflection'
    
    reflection_id = Column(Integer, primary_key=True)
    reflection_rate = Column(Integer, nullable=False)
    reflection_text = Column(Text, nullable=False)
    created_on = Column(DateTime, nullable=False)
    weekly_report_id = Column(Integer, ForeignKey('weekly_report.weekly_report_id'))
    user_id = Column(Integer, ForeignKey('account.user_id'))
    
    reflection_report = relationship('WeeklyReport', backref='reflection')
    reflection_user = relationship('Account', backref='reflection')
    
    def __init__(self, reflection_rate, reflection_text, weekly_report_id,user_id):
        self.reflection_rate = reflection_rate
        self.reflection_text = reflection_text
        self.created_on = datetime.now()
        self.weekly_report_id = weekly_report_id
        self.user_id = user_id
    
    def __repr__(self):
        return "<Reflection('%s')>" % (self.reflection_rate)

class Activity(Base):
    __tablename__ = 'activity'
    
    activity_id = Column(Integer, primary_key=True)
    activity_name = Column(Text, nullable=False)
    priority = Column(Integer)
    progress_percentage = Column(Integer)
    created_on = Column(DateTime, nullable=False)
    last_modify = Column(DateTime)
    project_id = Column(Integer, ForeignKey('project.project_id'))
    user_id = Column(Integer, ForeignKey('account.user_id'))
    weekly_report_id = Column(Integer, ForeignKey('weekly_report.weekly_report_id'))
    
    activity_project = relationship('Project', backref='activity')
    activity_user = relationship('Account', backref='activity')
    activity_weeklyreport = relationship ('WeeklyReport', backref='activity')
    
    def __init__(self, activity_name, priority, progress_percentage, project_id, user_id, weekly_report_id):
        self.activity_name = activity_name
        self.priority = priority
        self.progress_percentage = progress_percentage
        self.project_id = project_id 
        self.user_id = user_id
        self.weekly_report_id = weekly_report_id 
        self.created_on = datetime.now()
        self.last_modify = datetime.now() 
    
    def __repr__(self):
        return "<Activity('%s')>" % (self.activity_name)

class SeenBy(Base):
    __tablename__ = "seen_by"
    
    seen_by_id = Column(Integer, primary_key = True)
    weekly_report_id = Column(Integer, ForeignKey('weekly_report.weekly_report_id'))
    user_id = Column(Integer)
    date_seen = Column(DateTime)
    seen_by_user_id = Column(Integer, ForeignKey('account.user_id'))
    
    seenby_weeklyreport = relationship('WeeklyReport', backref='seen_by')
    seenby_userid = relationship('Account', backref='seen_by')
    
    def __init__(self, weekly_report_id, user_id, date_seen, seen_by_user_id):
        self.weekly_report_id = weekly_report_id
        self.user_id = user_id
        self.date_seen = date_seen
        self.seen_by_user_id = seen_by_user_id
        
    def __repr__(self):
        return "<SeenBy('%s')>" % (self.seen_by_id)
    
class Comment(Base):
    __tablename__ = "comment"
    
    comment_id = Column(Integer, primary_key = True)
    comment_text = Column(Text, nullable = False)
    user_id = Column(Integer)
    commented_by = Column(Integer, ForeignKey('account.user_id'))
    weekly_report_id = Column(Integer, ForeignKey('weekly_report.weekly_report_id'))
    like_count = Column(Integer)
    stars = Column(Integer)
    created_on = Column(DateTime)
    
    def __init__(self, comment_text, user_id, commented_by, weekly_report_id, like_count, stars):
        self.comment_text = comment_text
        self.user_id = user_id
        self.commented_by = commented_by
        self.weekly_report_id = weekly_report_id
        self.like_count = like_count
        self.stars = stars
        self.created_on = datetime.now()
    
    def __repr__(self):
        return "<Comment('%s')>" % (self.comment_id)

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