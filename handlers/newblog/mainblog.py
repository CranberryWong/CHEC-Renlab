#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import tornado
import tornado.locale
import markdown
import os
import uuid
import hashlib
import time
import json
import boto3 
import botocore
import urllib.request

from handlers.util import *
from handlers.base import BaseHandler
from models.entity import Account, XpEvents, ProjectGroup, Project, ProjectMember, WeeklyReport, Reflection, Activity, SeenBy, Comment
from models.entity import db_session
from datetime import datetime
from datetime import timedelta
from boto3 import Session
from PIL import Image
from io import BytesIO 
from sqlalchemy import exists, extract, func

# AWS S3 Configuration
BUCKET_NAME = 'chec-static'
session = Session()
credentials = session.get_credentials()
current_credentials = credentials.get_frozen_credentials()
s3 = boto3.resource('s3')
s3c = boto3.client('s3',aws_access_key_id=current_credentials.access_key,aws_secret_access_key=current_credentials.secret_key,aws_session_token=current_credentials.token)

# AWS S3 access bucket
myBucket = s3.Bucket(BUCKET_NAME)
config = s3c._client_config
config.signature_version = botocore.UNSIGNED

class homeBase(BaseHandler):
    def init(self):
        self.session = db_session.getSession
        self.signeduser = tornado.escape.to_basestring(BaseHandler.get_current_user(self))
        self.params = {'Bucket': BUCKET_NAME, 'Key': 'members/' + self.signeduser  + '/avatar.png'}
        self.avatarURL = s3c.generate_presigned_url('get_object', self.params)
        self.day_of_the_week = datetime.today() - timedelta(days=datetime.today().weekday() % 7)
        self.start_following_week = self.day_of_the_week + timedelta(days=7)
        if self.session.query(~exists().where(WeeklyReport.date_range_start+timedelta(days=1) >= self.day_of_the_week).where(WeeklyReport.date_range_start < self.start_following_week)).scalar():
            self.newweeklyreport = WeeklyReport(self.day_of_the_week)
            self.session.add(self.newweeklyreport)
            self.session.commit()
        self.weeklyreport = self.session.query(WeeklyReport).filter(WeeklyReport.date_range_start+timedelta(days=1) >= self.day_of_the_week).filter(WeeklyReport.date_range_start < self.start_following_week).first()
        
        end_following_week = self.start_following_week + timedelta(days=14)
        if self.session.query(~exists().where(WeeklyReport.date_range_start+timedelta(days=1) >= self.start_following_week).where(WeeklyReport.date_range_start < end_following_week)).scalar():
            self.newweeklyreport = WeeklyReport(self.start_following_week)
            self.session.add(self.newweeklyreport)
            self.session.commit()
        self.nextweeklyreport = self.session.query(WeeklyReport).filter(WeeklyReport.date_range_start+timedelta(days=1) >= self.start_following_week).filter(WeeklyReport.date_range_start < end_following_week).first()
        
        self.user = self.session.query(Account).filter(Account.username == self.signeduser).first()
        self.projectgrouplist = self.session.query(ProjectGroup).order_by(ProjectGroup.project_group_name.asc()).all()
        self.user_projectlist = self.session.query(Project).outerjoin(ProjectMember).outerjoin(Account).filter(ProjectMember.user_id == self.user.user_id).all()
        
        self.user_level = self.session.query(func.max(XpEvents.level)).filter(self.user.exp - XpEvents.min_xp >= 0).scalar()
        self.maxexp = self.session.query(XpEvents.min_xp).filter(self.user_level + 1 == XpEvents.level).scalar()
        self.session.close()

class MainHandler(BaseHandler):
    @tornado.web.authenticated
    def get(self, userName):
        homeBase.init(self)
        self.title = userName+" - New Blog"
        self.menu = 1
        reflection_exists = 0 
        reflection_content = ''         
        
        date=self.get_argument('date', None)
        
        if date != None:             
            self.date_start = datetime.strptime(date, "%Y-%m-%d %H:%M:%S.%f") - timedelta(days=datetime.strptime(date, "%Y-%m-%d %H:%M:%S.%f").weekday() % 7) 
            self.date_end = self.date_start + timedelta(days = 7)
            
            if self.session.query(~exists().where(WeeklyReport.date_range_start+timedelta(days=1) >= self.date_start).where(WeeklyReport.date_range_start < self.date_end)).scalar():
                self.newweeklyreport = WeeklyReport(self.date_start)
                self.session.add(self.newweeklyreport)
                self.session.commit()
                
            self.weeklyreport = self.session.query(WeeklyReport).filter(WeeklyReport.date_range_start+timedelta(days=1) >= self.date_start).filter(WeeklyReport.date_range_start < self.date_end).first()
            
            if self.session.query(~exists().where(WeeklyReport.date_range_start+timedelta(days=1) >= self.date_end).where(WeeklyReport.date_range_start < (self.date_end + timedelta(days = 7)))).scalar():
                self.newweeklyreport = WeeklyReport(self.date_end)
                self.session.add(self.newweeklyreport)
                self.session.commit()
                
            self.nextweeklyreport = self.session.query(WeeklyReport).filter(WeeklyReport.date_range_start+timedelta(days=1) >= self.date_end).filter(WeeklyReport.date_range_start < (self.date_end + timedelta(days = 7))).first()
            self.dateprev =  self.date_start - timedelta(days=7)
            self.datenext = self.date_end
        else:
            self.dateprev =  (datetime.today() - timedelta(days=datetime.today().weekday() % 7)) - timedelta(days=7)      
            self.datenext = self.dateprev + timedelta(days=14)     
        
        self.daterange = "" + self.weeklyreport.date_range_start.strftime("%B %d") + " - " + self.weeklyreport.date_range_end.strftime("%B %d")
        
        if userName == self.signeduser: 
            self.visitor = 0
        else:
            self.visitor = 1
            self.currentuser = self.user
            self.user = self.session.query(Account).filter(Account.username == userName).first()
            if self.session.query(~exists().where(SeenBy.user_id == self.user.user_id).where(SeenBy.weekly_report_id == self.weeklyreport.weekly_report_id).where(SeenBy.seen_by_user_id == self.currentuser.user_id)).scalar():
                self.newseenby = SeenBy(self.weeklyreport.weekly_report_id, self.user.user_id, datetime.now(), self.currentuser.user_id)
                self.session.add(self.newseenby)
                self.session.commit()
            # photo profile 
            self.params = {'Bucket': BUCKET_NAME, 'Key': 'members/' + userName  + '/avatar.png'}
            self.avatarURL = s3c.generate_presigned_url('get_object', self.params)
            self.projectgrouplist = self.session.query(ProjectGroup).order_by(ProjectGroup.project_group_name.asc()).all()
            self.user_projectlist = self.session.query(Project).outerjoin(ProjectMember).outerjoin(Account).filter(ProjectMember.user_id == self.user.user_id).all()
            self.user_level = self.session.query(func.max(XpEvents.level)).filter(self.user.exp - XpEvents.min_xp >= 0).scalar()
            self.maxexp = self.session.query(XpEvents.min_xp).filter(self.user_level + 1 == XpEvents.level).scalar()
        
        self.seen_by_report = self.session.query(SeenBy).filter(SeenBy.user_id == self.user.user_id).filter(SeenBy.weekly_report_id == self.weeklyreport.weekly_report_id).order_by(SeenBy.seen_by_user_id.desc()).all()
        seenbyAvatarURL={}
        
        for seenby in self.seen_by_report:
            self.seenbyuser = self.session.query(Account).filter(Account.user_id == seenby.seen_by_user_id).first()
            self.param = {'Bucket': BUCKET_NAME, 'Key': 'members/' + self.seenbyuser.username  + '/avatar.png'}
            seenbyAvatarURL[seenby.seen_by_id] = s3c.generate_presigned_url('get_object', self.param) 
        
        # reflection
        if self.session.query(exists().where(Reflection.weekly_report_id == self.weeklyreport.weekly_report_id).where(Reflection.user_id == self.user.user_id)).scalar():
            reflection_exists = 1
            reflection_content = self.session.query(Reflection).filter(Reflection.weekly_report_id == self.weeklyreport.weekly_report_id).filter(Reflection.user_id == self.user.user_id).first()
        self.allactivity = list()
        self.thisweekactivity = list()
        self.nextweekactivity = list() 
        
        self.thisweekprojectlist = self.session.query(Project).outerjoin(Activity).filter(Activity.user_id == self.user.user_id).filter(Activity.weekly_report_id == self.weeklyreport.weekly_report_id)
        
        self.nextweekprojectlist = self.session.query(Project).outerjoin(Activity).filter(Activity.user_id == self.user.user_id).filter(Activity.weekly_report_id == self.nextweeklyreport.weekly_report_id)
        
        for project in self.thisweekprojectlist:
            self.thisweekactivity.append([project,self.session.query(Activity, WeeklyReport).outerjoin(WeeklyReport).filter(Activity.user_id == self.user.user_id).filter(Activity.project_id == project.project_id).filter(WeeklyReport.weekly_report_id == self.weeklyreport.weekly_report_id).all()])
        
        for project in self.nextweekprojectlist:
            self.nextweekactivity.append([project,self.session.query(Activity, WeeklyReport).outerjoin(WeeklyReport).filter(Activity.user_id == self.user.user_id).filter(Activity.project_id == project.project_id).filter(WeeklyReport.weekly_report_id == self.nextweeklyreport.weekly_report_id).all()])
        
        self.allactivity.append(self.thisweekactivity)
        self.allactivity.append(self.nextweekactivity)
        
        self.render("newblog/report.html", title = self.title, userName = userName, user = self.user, avatarURL = self.avatarURL, projectgrouplist = self.projectgrouplist, reflection_exists = reflection_exists, reflection_content = reflection_content, projectlist = self.user_projectlist, menu = self.menu, allactivity = self.allactivity, dateprev= self.dateprev, datenext = self.datenext, daterange = self.daterange, userlevel = self.user_level, maxexp = self.maxexp, visitor = self.visitor, seenbydata = self.seen_by_report, seenbyAvatarURL = seenbyAvatarURL)
        self.session.close()
        
class ProfileEditHandler(BaseHandler):
    def get(self):
        homeBase.init(self)
        self.user=self.session.query(Account).filter(Account.username == self.signeduser).first()
        self.title = "New Blog"
        self.menu = 1
        self.render("newblog/main.html", title = self.title, userName = self.user.username, user = self.user, avatarURL = self.avatarURL, menu = self.menu, userlevel = self.user_level, maxexp = self.maxexp)
        self.session.close()
        
    def post(self):
        homeBase.init(self)
        userid = self.get_argument('userid',default='')
        newemail = self.get_argument('newemail', default= '')
        newphonenumber = self.get_argument('newphonenumber', default='')
        newwechatid = self.get_argument('newwechatid', default='')
        newlineid = self.get_argument('newlineid', default='')
        newskypeid = self.get_argument('newskypeid', default='')
        newphotoprofile = self.get_argument('newphotoprofile',default='')
        edituser = self.session.query(Account).filter(Account.username == self.signeduser).first()
        edituser.email = newemail
        edituser.phone_number = newphonenumber
        edituser.wechat_id = newwechatid
        edituser.line_id = newlineid
        edituser.skype_id = newskypeid
        if 'newphotoprofile' in self.request.files:
            file_dict_list = self.request.files['newphotoprofile']
            for file_dict in file_dict_list:
                # filename = nameRewrite(file_dict["filename"]).encode('utf8')
                filename = file_dict["filename"]
                data = file_dict["body"]
                image = Image.open(BytesIO (data))
                in_mem_file = BytesIO()
                image.save(in_mem_file, format=image.format)
                in_mem_file.seek(0)
                s3c.put_object(Bucket=BUCKET_NAME,Body=in_mem_file,Key='members/' + self.signeduser + '/avatar.png')
                # image.save(articles_path + filename, quality=150)
        self.session.commit()
        self.redirect("/newblog/" + edituser.username)
        self.session.close()
        
class AddProjectHandler(BaseHandler):
    def get(self):
        homeBase.init(self)
        self.user=self.session.query(Account).filter(Account.username == self.signeduser).first()
        self.title = "New Blog"
        self.render("newblog/main.html", title = self.title, userName = self.user.username, user = self.user, avatarURL = self.avatarURL, userlevel = self.user_level, maxexp = self.maxexp)
        self.session.close()
        
    def post(self):
        homeBase.init(self)
        newprojectgroupid = self.get_argument('newprojectgroupid', default=1)
        newprojectname = self.get_argument('newprojectname', default='')
        newprojectmembers = self.get_arguments('newprojectmembers')
        
        if self.session.query(exists().where(Project.project_name == newprojectname).where(Project.project_group_id == newprojectgroupid)).scalar():
            # data already exists
            editproject = self.session.query(Project).filter(Project.project_name==newprojectname).first()
            editproject.project_group_id = newprojectgroupid
            editproject.project_name = newprojectname
            self.session.commit()           
            for member in newprojectmembers:
                if self.session.query(~exists().where(ProjectMember.user_id == member).where(ProjectMember.project_id == editproject.project_id)).scalar():
                    newmember = ProjectMember(member, editproject.project_id)
                    self.session.add(newmember)
                    self.session.commit()
        else:
            newproject = Project(newprojectname, newprojectgroupid)
            self.session.add(newproject)
            querynewproject = self.session.query(Project).filter(Project.project_name == newprojectname).filter(Project.project_group_id == newprojectgroupid).first()
            for member in newprojectmembers:
                newmember = ProjectMember(member, querynewproject.project_id)
                self.session.add(newmember)
            self.session.commit()
        self.redirect("/newblog/" + self.signeduser)
        self.sesion.close()

class AddReflection(BaseHandler):
    def get(self):
        homeBase.init(self)
        self.user=self.session.query(Account).filter(Account.username == self.signeduser).first()
        self.title = "New Blog"
        self.render("newblog/main.html", title = self.title, userName = self.user.username, user = self.user, avatarURL = self.avatarURL, userlevel = self.user_level, maxexp = self.maxexp)
        self.session.close()
    
    def post(self):
        homeBase.init(self)
        self.user=self.session.query(Account).filter(Account.username == self.signeduser).first()
        newreflectionrate = self.get_argument('newreflectionrate', default=0)
        newreflectiontext = self.get_argument('newreflectiontext', default='')
        
        if self.session.query(exists().where(Reflection.weekly_report_id == self.weeklyreport.weekly_report_id).where(Reflection.user_id == self.user.user_id)).scalar():
            self.write('<script language="javascript">alert("You already wrote your reflection");self.location="/newblog/'+self.user.username+'";</script>')
        else:
            newreflection = Reflection(newreflectionrate, newreflectiontext, self.weeklyreport.weekly_report_id, self.user.user_id)
            self.session.add(newreflection)
            self.session.commit()
            self.redirect("/newblog/" + self.user.username)
            
        self.session.close()
        
class AddActivityHandler(BaseHandler):
    def get(self):
        homeBase.init(self)
        self.user=self.session.query(Account).filter(Account.username == self.signeduser).first()
        self.title = "New Blog"
        self.menu = 2
        self.render("newblog/main.html", title = self.title, userName = self.user.username, user = self.user, avatarURL = self.avatarURL, menu=self.menu, userlevel = self.user_level, maxexp = self.maxexp)
        self.session.close()
        
    def post(self):
        homeBase.init(self)
        self.user=self.session.query(Account).filter(Account.username == self.signeduser).first()
        newactivityname = self.get_argument('newactivityname', default='')
        newprojectid = self.get_argument('newprojectid', default=7)
        newdaterange = self.get_argument('newdaterange', default='')
        newpriority = self.get_argument('newpriority', default=0)
        newpercentage = self.get_argument('newpercentage', default=0)
        
        if(newdaterange=='' or newpercentage == '' or newactivityname == ''):
            if(newprojectid == 7):
                self.write('<script language="javascript">alert("Please input full data!");self.location="/newblog/projectadmin";</script>')
        else:
            daterange = newdaterange.split(" - ")
            datestart = datetime.strptime(daterange[0], "%Y.%m.%d")  - timedelta(days=datetime.strptime(daterange[0], "%Y.%m.%d").weekday() % 7)
            date_start_following_week = datestart + timedelta(days=7)
            
            if self.session.query(~exists().where(WeeklyReport.date_range_start>=datestart).where(WeeklyReport.date_range_start < date_start_following_week)).scalar():
                postweeklyreport = WeeklyReport(datestart)
                self.session.add(postweeklyreport)
                self.session.commit()
            addweeklyreport = self.session.query(WeeklyReport).filter(WeeklyReport.date_range_start>=datestart).filter(WeeklyReport.date_range_start < date_start_following_week).first()
            newactivity = Activity(newactivityname, newpriority, newpercentage, newprojectid, self.user.user_id, addweeklyreport.weekly_report_id)
            self.session.add(newactivity)
            self.session.commit()
            if(newprojectid == 7):
                self.redirect('/newblog/projectadmin')
            else:
                self.redirect('/newblog/'+self.signeduser)
            self.session.close()

class DeleteActivity(BaseHandler):
    @tornado.web.authenticated
    def get(self):
        homeBase.init(self)
        deleteactivityid = self.get_argument("deleteactivityid", default=None)
        self.session.query(Activity).filter(Activity.activity_id == deleteactivityid).delete()
        self.session.commit()
        self.redirect('/newblog/projectadmin')
        self.session.close()

class ProjectAdminHandler(BaseHandler):
    @tornado.web.authenticated
    def get(self, userName):
        homeBase.init(self)
        self.title = "Project Admin - New Blog"
        self.menu = 2
        self.user_projectlist = self.session.query(Project.project_name).outerjoin(ProjectMember).outerjoin(Account).filter(ProjectMember.user_id == self.user.user_id)
        self.activitylist = self.session.query(Activity, WeeklyReport).outerjoin(WeeklyReport).filter(Activity.user_id == self.user.user_id).filter(Activity.project_id == 7).filter(extract('month',WeeklyReport.date_range_start)==datetime.today().month).all()
        if userName == self.signeduser: 
            self.visitor = 0
        else:
            self.visitor = 1
            self.user = self.session.query(Account).filter(Account.username == userName).first()
            # photo profile 
            self.params = {'Bucket': BUCKET_NAME, 'Key': 'members/' + userName  + '/avatar.png'}
            self.avatarURL = s3c.generate_presigned_url('get_object', self.params)
            self.projectgrouplist = self.session.query(ProjectGroup).order_by(ProjectGroup.project_group_name.asc()).all()
            self.user_projectlist = self.session.query(Project).outerjoin(ProjectMember).outerjoin(Account).filter(ProjectMember.user_id == self.user.user_id).all()
            self.user_level = self.session.query(func.max(XpEvents.level)).filter(self.user.exp - XpEvents.min_xp >= 0).scalar()
            self.maxexp = self.session.query(XpEvents.min_xp).filter(self.user_level + 1 == XpEvents.level).scalar()
        self.render("newblog/project_admin.html", title = self.title, userName = userName, user = self.user, avatarURL = self.avatarURL, projectgrouplist = self.projectgrouplist, projectlist = self.user_projectlist, menu = self.menu, activitylist = self.activitylist, adminmonth = datetime.today(), userlevel = self.user_level, maxexp = self.maxexp, visitor = self.visitor)
        self.session.close()
        
    def post(self):
        homeBase.init(self)
        self.title = "Project Admin - New Blog"
        self.menu = 2
        newmonth = datetime.strptime(self.get_argument('newmonth', default=datetime.today().month), '%B %Y')
        self.user_projectlist = self.session.query(Project.project_name).outerjoin(ProjectMember).outerjoin(Account).filter(ProjectMember.user_id == self.user.user_id)
        self.activitylist = self.session.query(Activity, WeeklyReport).outerjoin(WeeklyReport).filter(Activity.user_id == self.user.user_id).filter(Activity.project_id == 7).filter(extract('month',WeeklyReport.date_range_start)==newmonth.month).all()
        self.render("newblog/project_admin.html", title = self.title, userName = userName, user = self.user, avatarURL = self.avatarURL, projectgrouplist = self.projectgrouplist, projectlist = self.user_projectlist, menu = self.menu, activitylist = self.activitylist, adminmonth = newmonth, userlevel = self.user_level, maxexp = self.maxexp)
        

class LeaderboardHandler(BaseHandler):
    @tornado.web.authenticated
    def get(self, userName):
        homeBase.init(self)
        self.title = "Leaderboard - New Blog"
        self.menu = 3
        
        if userName == self.signeduser: 
            self.visitor = 0
        else:
            self.visitor = 1
            self.user = self.session.query(Account).filter(Account.username == userName).first()
            # photo profile 
            self.params = {'Bucket': BUCKET_NAME, 'Key': 'members/' + userName  + '/avatar.png'}
            self.avatarURL = s3c.generate_presigned_url('get_object', self.params)
            self.projectgrouplist = self.session.query(ProjectGroup).order_by(ProjectGroup.project_group_name.asc()).all()
            self.user_projectlist = self.session.query(Project).outerjoin(ProjectMember).outerjoin(Account).filter(ProjectMember.user_id == self.user.user_id).all()
            self.user_level = self.session.query(func.max(XpEvents.level)).filter(self.user.exp - XpEvents.min_xp >= 0).scalar()
            self.maxexp = self.session.query(XpEvents.min_xp).filter(self.user_level + 1 == XpEvents.level).scalar()
        
        self.leaderboards = list()
        self.leaderboard = self.session.query(Account.user_id, Account.username, Account.exp).order_by(Account.exp.desc()).all()
        for idx,board in enumerate(self.leaderboard):
            self.level = self.session.query(func.max(XpEvents.level)).filter(board.exp - XpEvents.min_xp >= 0).scalar()
            self.params = {'Bucket': BUCKET_NAME, 'Key': 'members/' + board.username + '/avatar.png'}
            self.boardavatar = s3c.generate_presigned_url('get_object', self.params)
            self.leaderboards.append([self.level, board, self.boardavatar])
            if board.username == self.signeduser:
                self.userindex = idx
        
        self.render("newblog/leaderboard.html", title = self.title, menu = self.menu, userName = userName, avatarURL = self.avatarURL, user = self.user, projectgrouplist = self.projectgrouplist, projectlist = self.user_projectlist, leaderboard = self.leaderboards, userlevel = self.user_level, userrank = self.userindex, maxexp = self.maxexp, visitor = self.visitor)
        
class AddCommentHandler(BaseHandler):
    @tornado.web.authenticated
    def get(self):
        homeBase.init(self)
        self.user=self.session.query(Account).filter(Account.username == self.signeduser).first()
        self.title = "New Blog"
        self.menu = 1
        self.render("newblog/main.html", title = self.title, userName = self.user.username, user = self.user, avatarURL = self.avatarURL, menu=self.menu, userlevel = self.user_level, maxexp = self.maxexp)
        self.session.close()
    
    def post(self):
        homeBase.init(self)
        self.user=self.session.query(Account).filter(Account.username == self.signeduser).first()
        
        self.newcommentext = self.get_argument('newcommentext', default='')
        self.newuserid = self.get_argument('newuserid', default=0)
        self.newcommentedby = self.user.user_id
        self.newweeklyreportid = self.weeklyreport
        self.newstars = self.get_argument('newstars', default=0)
        
        newcomment = Comment(self.newcommentext,self.newuserid,self.newcommentedby,self.newweeklyreportid.weekly_report_id,0,self.newstars)
        self.session.add(newcomment)
        self.session.commit()
        self.redirect("/newblog/" + self.user.username)
        
        self.session.close()