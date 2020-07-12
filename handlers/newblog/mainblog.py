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
from models.entity import Account, XpEvents, ProjectGroup, Project, ProjectMember, WeeklyReport, Reflection, Activity
from models.entity import db_session
from datetime import datetime
from datetime import timedelta
from boto3 import Session
from PIL import Image
from io import BytesIO 
from sqlalchemy import exists, extract

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
        params = {'Bucket': BUCKET_NAME, 'Key': 'members/' + self.signeduser  + '/avatar.png'}
        self.avatarURL = s3c.generate_presigned_url('get_object', params)
        day_of_the_week = datetime.today()  - timedelta(days=datetime.today().weekday() % 7)
        start_following_week = day_of_the_week + timedelta(days=7)
        if self.session.query(~exists().where(WeeklyReport.date_range_start >= day_of_the_week).where(WeeklyReport.date_range_start < start_following_week)).scalar():
            newweeklyreport = WeeklyReport(day_of_the_week)
            self.session.add(newweeklyreport)
            self.session.commit()
        self.weeklyreport = self.session.query(WeeklyReport).filter(WeeklyReport.date_range_start > day_of_the_week).filter(WeeklyReport.date_range_start < start_following_week).first()
        self.user = self.session.query(Account).filter(Account.username == self.signeduser).first()
        self.projectgrouplist = self.session.query(ProjectGroup).order_by(ProjectGroup.project_group_name.asc()).all()
        self.user_projectlist = self.session.query(Project.project_name).outerjoin(ProjectMember).outerjoin(Account).filter(ProjectMember.user_id == self.user.user_id).all()
        self.session.close()

class MainHandler(BaseHandler):
    @tornado.web.authenticated
    def get(self, userName):
        homeBase.init(self)
        self.title = "New Blog"
        self.menu = 1
        reflection_exists = 0 
        reflection_content = ''
        if self.session.query(exists().where(Reflection.weekly_report_id == self.weeklyreport.weekly_report_id).where(Reflection.user_id == self.user.user_id)).scalar():
            reflection_exists = 1
            reflection_content = self.session.query(Reflection).filter(Reflection.weekly_report_id == self.weeklyreport.weekly_report_id).filter(Reflection.user_id == self.user.user_id).first()
        self.render("newblog/report.html", title = self.title, userName = userName, user = self.user, avatarURL = self.avatarURL, projectgrouplist = self.projectgrouplist, reflection_exists = reflection_exists, reflection_content = reflection_content, projectlist = self.user_projectlist, menu = self.menu)
        self.session.close()
        
class ProfileEditHandler(BaseHandler):
    def get(self):
        homeBase.init(self)
        self.user=self.session.query(Account).filter(Account.username == self.signeduser).first()
        self.title = "New Blog"
        self.menu = 1
        self.render("newblog/main.html", title = self.title, userName = self.user.username, user = self.user, avatarURL = self.avatarURL, menu = self.menu)
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
        self.render("newblog/main.html", title = self.title, userName = self.user.username, user = self.user, avatarURL = self.avatarURL)
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
            for member in newprojectmembers:
                newmember = ProjectMember(member, newproject.project_id)
                self.session.add(newmember)
            self.session.commit()
        self.redirect("/newblog/" + self.signeduser)
        self.sesion.close()

class AddReflection(BaseHandler):
    def get(self):
        homeBase.init(self)
        self.user=self.session.query(Account).filter(Account.username == self.signeduser).first()
        self.title = "New Blog"
        self.render("newblog/main.html", title = self.title, userName = self.user.username, user = self.user, avatarURL = self.avatarURL)
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
        self.render("newblog/main.html", title = self.title, userName = self.user.username, user = self.user, avatarURL = self.avatarURL, menu=self.menu)
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
    def get(self):
        homeBase.init(self)
        self.title = "Project Admin - New Blog"
        self.menu = 2
        self.user_projectlist = self.session.query(Project.project_name).outerjoin(ProjectMember).outerjoin(Account).filter(ProjectMember.user_id == self.user.user_id)
        activitylist = self.session.query(Activity, WeeklyReport).outerjoin(WeeklyReport).filter(Activity.user_id == self.user.user_id).filter(Activity.project_id == 7).filter(extract('month',WeeklyReport.date_range_start)==datetime.today().month).all()
        self.render("newblog/project_admin.html", title = self.title, userName = self.signeduser, user = self.user, avatarURL = self.avatarURL, projectgrouplist = self.projectgrouplist, projectlist = self.user_projectlist, menu = self.menu, activitylist = activitylist, adminmonth = datetime.today())
        
    def post(self):
        homeBase.init(self)
        self.title = "Project Admin - New Blog"
        self.menu = 2
        newmonth = datetime.strptime(self.get_argument('newmonth', default=datetime.today().month), '%B %Y')
        self.user_projectlist = self.session.query(Project.project_name).outerjoin(ProjectMember).outerjoin(Account).filter(ProjectMember.user_id == self.user.user_id)
        activitylist = self.session.query(Activity, WeeklyReport).outerjoin(WeeklyReport).filter(Activity.user_id == self.user.user_id).filter(Activity.project_id == 7).filter(extract('month',WeeklyReport.date_range_start)==newmonth.month).all()
        self.render("newblog/project_admin.html", title = self.title, userName = self.signeduser, user = self.user, avatarURL = self.avatarURL, projectgrouplist = self.projectgrouplist, projectlist = self.user_projectlist, menu = self.menu, activitylist = activitylist, adminmonth = newmonth)