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
import re

from handlers.util import *
from handlers.base import BaseHandler
from models.entity import Account, XpEvents, ProjectGroup, Project, ProjectMember, WeeklyReport, Reflection, Activity, SeenBy, Comment, Like, Reply, ReplyLike, Notification
from models.entity import db_session
from datetime import datetime
from datetime import timedelta
from boto3 import Session
from PIL import Image
from io import BytesIO 
from sqlalchemy import exists, extract, func, literal

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
        
        self.notification_query = self.session.query(Notification).filter(Notification.recipient_id == self.user.user_id).order_by(Notification.created_on.desc()).all()
        
        self.notifications =  list()
        for notification in self.notification_query:
            self.sender = self.session.query(Account).filter(Account.user_id == notification.sender_id).first()
            self.param = {'Bucket': BUCKET_NAME, 'Key': 'members/' + self.sender.username  + '/avatar.png'}
            self.notificationavatarURL = s3c.generate_presigned_url('get_object', self.param)
            self.inside = {"notification_id": notification.notification_id, "avatar_url": self.notificationavatarURL, "sender_name": self.sender.username, "reference_text": notification.reference_text, "click_by_user": notification.click_by_user, "created_on":notification.created_on}
            self.notifications.append(self.inside)
        
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
            shareweeklyreport = self.weeklyreport
            
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
        
        self.currentuser = self.user
        self.currentuseravatarURL = self.avatarURL
        
        if userName == self.signeduser: 
            self.visitor = 0
        else:
            self.visitor = 1
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
        self.seenbydata = list()
        
        for seenby in self.seen_by_report:
            self.seenbyuser = self.session.query(Account).filter(Account.user_id == seenby.seen_by_user_id).first()
            self.param = {'Bucket': BUCKET_NAME, 'Key': 'members/' + self.seenbyuser.username  + '/avatar.png'}
            self.seenbydatainside = {'seen_by_id' : seenby.seen_by_id, 'seen_by_username' : self.seenbyuser.username, 'avatarURL' : s3c.generate_presigned_url('get_object', self.param), 'date_seen' : seenby.date_seen}
            self.seenbydata.append(self.seenbydatainside)
        
        # reflection
        if self.session.query(exists().where(Reflection.weekly_report_id == self.weeklyreport.weekly_report_id).where(Reflection.user_id == self.user.user_id)).scalar():
            reflection_exists = 1
            reflection_content = self.session.query(Reflection).filter(Reflection.weekly_report_id == self.weeklyreport.weekly_report_id).filter(Reflection.user_id == self.user.user_id).first()
            
        #comments
        self.comments = list()
        self.commentquery = self.session.query(Comment).filter(Comment.user_id == self.user.user_id).filter(Comment.weekly_report_id == self.weeklyreport.weekly_report_id).order_by(Comment.created_on.desc()).all()
        self.commentsname = {}
        self.commentsAvatarURL = {}
        self.repliesname = {}
        self.repliesAvatarURL = {}
        self.reply_liked_by = {}
        self.reply_likedata = {}
        for comment in self.commentquery:
            self.commentuser = self.session.query(Account).filter(Account.user_id == comment.commented_by).first()
            self.param = {'Bucket': BUCKET_NAME, 'Key': 'members/' + self.commentuser.username  + '/avatar.png'}
            self.commentsAvatarURL[comment.comment_id] = s3c.generate_presigned_url('get_object', self.param) 
            self.commentsname[comment.comment_id] = self.commentuser.username
            self.liked_by = 0
            if self.session.query(exists().where(Like.user_id == self.currentuser.user_id).where(Like.comment_id == comment.comment_id).where(Like.weekly_report_id == self.weeklyreport.weekly_report_id)).scalar():   
                self.liked_by = 1
            self.likedata = self.session.query(Like).filter(Like.user_id == self.currentuser.user_id).filter(Like.comment_id == comment.comment_id).filter(Like.weekly_report_id == self.weeklyreport.weekly_report_id).first()
            
            self.replies = self.session.query(Reply).filter(Reply.parent_comment_id == comment.comment_id).order_by(Reply.created_on.desc()).all()
            
            for reply in self.replies:
                self.replyuser = self.session.query(Account).filter(Account.user_id == reply.user_id).first()
                self.param = {'Bucket': BUCKET_NAME, 'Key': 'members/' + self.replyuser.username  + '/avatar.png'}
                self.repliesAvatarURL[reply.reply_id] = s3c.generate_presigned_url('get_object', self.param) 
                self.repliesname[reply.reply_id] = self.replyuser.username
                if self.session.query(exists().where(ReplyLike.user_id == self.currentuser.user_id).where(ReplyLike.reply_id == reply.reply_id).where(ReplyLike.weekly_report_id == self.weeklyreport.weekly_report_id)).scalar():   
                    self.reply_liked_by[reply.reply_id] = 1
                self.reply_likedata[reply.reply_id] = self.session.query(ReplyLike).filter(ReplyLike.user_id == self.currentuser.user_id).filter(ReplyLike.reply_id == reply.reply_id).filter(ReplyLike.weekly_report_id == self.weeklyreport.weekly_report_id).first()
            
            self.commentinside = {"comment_id": comment.comment_id, "comment_text": comment.comment_text, "user_id": comment.user_id, "commented_by": comment.commented_by, "weekly_report_id": comment.weekly_report_id, "like_count": comment.like_count, "stars": comment.stars, "created_on": comment.created_on, "liked_by_user": self.liked_by, "like_data": self.likedata, "replies": self.replies, "replies_avatar": self.repliesAvatarURL, "replies_name": self.repliesname, "reply_liked_by": self.reply_liked_by, "reply_like_data": self.reply_likedata}
            
            self.comments.append(self.commentinside)
        
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
        
        self.render("newblog/report.html", title = self.title, userName = userName, user = self.user, avatarURL = self.avatarURL, projectgrouplist = self.projectgrouplist, reflection_exists = reflection_exists, reflection_content = reflection_content, projectlist = self.user_projectlist, menu = self.menu, allactivity = self.allactivity, dateprev= self.dateprev, datenext = self.datenext, daterange = self.daterange, userlevel = self.user_level, maxexp = self.maxexp, visitor = self.visitor, comments = self.comments, commentsAvatarURL = self.commentsAvatarURL, commentsname = self.commentsname, currentuser= self.currentuser, weeklyreportid = self.weeklyreport.weekly_report_id, currentuseravatarURL = self.currentuseravatarURL, notifications = self.notifications, seenbydatafull = self.seenbydata )
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
        self.session.flush()
        if(edituser.email != '' and edituser.phone_number != '' and edituser.wechat_id != '' and edituser.line_id != '' and edituser.skype_id != ''):
            edituser.exp = edituser.exp + 5
        
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
            
            self.userexp = self.session.query(Account).filter(Account.user_id == self.user.user_id).first()
            self.userexp.exp = self.userexp.exp + 3 
            
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
        self.activitylocation = int(self.get_argument('activitylocation',default=7))
        
        if(newdaterange=='' or newpercentage == '' or newactivityname == ''):
            if(newprojectid == 7):
                self.write('<script language="javascript">alert("Please input full data!");self.location="/newblog/projectadmin";</script>')           
        else:
            if(int(newpercentage) > 100 or int(newpercentage) < 0):
                self.write('<script language="javascript">alert("Please input the right percentage (0 - 100)!");self.location="/newblog/projectadmin";</script>')     
            else: 
                daterange = newdaterange.split(" - ")
                datestart = datetime.strptime(daterange[0], "%Y.%m.%d")  - timedelta(days=datetime.strptime(daterange[0], "%Y.%m.%d").weekday() % 7)
                date_start_following_week = datestart + timedelta(days=7)
                
                if self.session.query(~exists().where(WeeklyReport.date_range_start>=datestart).where(WeeklyReport.date_range_start < date_start_following_week)).scalar():
                    postweeklyreport = WeeklyReport(datestart)
                    self.session.add(postweeklyreport)
                    self.session.commit()
                addweeklyreport = self.session.query(WeeklyReport).filter(WeeklyReport.date_range_start>=datestart).filter(WeeklyReport.date_range_start < date_start_following_week).first()
                newactivity = Activity(newactivityname, newpriority.strip("P"), newpercentage, newprojectid, self.user.user_id, addweeklyreport.weekly_report_id)
                self.session.add(newactivity)
                self.session.flush()
                                    
                self.userexp = self.session.query(Account).filter(Account.user_id == self.user.user_id).first()
            
                if (newpercentage == 100):
                    self.userexp.exp = self.userexp.exp + 4
                else:
                    self.userexp.exp = self.userexp.exp + 2                
                
                #processing comment text for the mention
                self.mentioneduser = re.findall(r'@(\w+)', newactivityname)
                self.modifiedcommenttext = newactivityname
                if len(self.mentioneduser)>0:
                    for idx, mention in enumerate(self.mentioneduser):
                        #get mentioned userid
                        self.mentionuser = self.session.query(Account).filter(Account.username.contains(mention)).all()
                        
                        while(len(self.mentionuser)>1):
                            self.newmention = re.findall(r'{mention}(\w+)', newactivityname)
                            self.mentionuser = self.session.query(Account).filter(Account.username.contains(self.newmention)).all()
                                                                    
                        #use the full name to change the text to the link
                        self.modifiedcommenttext = self.modifiedcommenttext.replace("@" + self.mentionuser[0].username, "<a href='/newblog/" + self.mentionuser[0].username+"'>" + "@" + self.mentionuser[0].username + "</a>")
                        print(self.modifiedcommenttext)
                        
                        #notify mentioned user
                        self.mentionnotification = Notification(self.mentionuser[0].user_id, self.user.user_id, addweeklyreport.weekly_report_id, self.user.username, 5, "mentioned you: " + newactivityname, 1, newactivity.activity_id)
                        self.session.add(self.mentionnotification)
                
                newactivity.activity_name = self.modifiedcommenttext
                
                self.session.commit()
                #redirecting the page
                if(self.activitylocation == 7):
                    self.redirect('/newblog/'+self.signeduser+'/projectadmin?date=' + datestart.strftime("%Y-%m-%d %H:%M:%S.%f"))
                else:
                    self.redirect('/newblog/'+self.signeduser + "?date=" + datestart.strftime("%Y-%m-%d %H:%M:%S.%f"))
                self.session.close()

class EditActivityHandler(BaseHandler):
    @tornado.web.authenticated
    def get(self):
        homeBase.init(self)
        
    def post(self):
        homeBase.init(self)
        self.newactivityid = self.get_argument('newactivityid', default=0)
        self.newactivityname = self.get_argument('newactivityname', default='')
        self.newdaterange = self.get_argument('newdaterange', default='')
        self.newpriority = self.get_argument('newpriority',default=3)
        self.newpercentage = int(self.get_argument('newpercentage', default=0))
        self.activitylocation = int(self.get_argument('activitylocation',default=7))
        
        #check the data is empty or not
        if(self.newdaterange=='' or self.newpercentage == '' or self.newactivityname == ''):
            self.write('<script language="javascript">alert("Please input full data!");self.location="/newblog/projectadmin";</script>')
        else:
            if(self.newpercentage > 100 or self.newpercentage < 0):
                self.write('<script language="javascript">alert("Please input the right percentage (0 - 100)!");self.location="/newblog/projectadmin";</script>')       
            #check whether the activity is exist
            if self.session.query(exists().where(Activity.activity_id == self.newactivityid)).scalar():
                self.newactivity = self.session.query(Activity).filter(Activity.activity_id == self.newactivityid).first()
                
                #parse the newdaterange into daterange start and daterange end
                self.daterange = self.newdaterange.split(" - ")
                self.datestart = datetime.strptime(self.daterange[0], "%Y.%m.%d")  - timedelta(days=datetime.strptime(self.daterange[0], "%Y.%m.%d").weekday() % 7)
                self.date_start_following_week = self.datestart + timedelta(days=7)
                
                #if the new date range is not exist, create a new weeklyreport data
                if self.session.query(~exists().where(WeeklyReport.date_range_start>= self.datestart).where(WeeklyReport.date_range_start < self.date_start_following_week)).scalar():
                    self.postweeklyreport = WeeklyReport(self.datestart)
                    self.session.add(self.postweeklyreport)
                    self.session.flush()
                
                #get new weeklyreport id
                self.newweeklyreport = self.session.query(WeeklyReport).filter(WeeklyReport.date_range_start>=self.datestart).filter(WeeklyReport.date_range_start < self.date_start_following_week).first()
                
                #take the user's database
                self.newuser = self.session.query(Account).filter(Account.user_id == self.newactivity.user_id).first()
                
                #add user exp point +1 every editing
                self.newuser.exp = self.newuser.exp + 1
                
                #check whether the new percentage is decreasing from 100% or not 
                if (self.newactivity.progress_percentage == 100 and self.newpercentage < 100):
                    self.newuser.exp = self.newuser.exp - 2
                else: 
                    if (self.newactivity.progress_percentage < 100 and self.newpercentage == 100):
                        self.newuser.exp = self.newuser.exp + 2
                
                #edit the database
                self.newactivity.activity_name = self.newactivityname
                self.newactivity.priority = self.newpriority
                self.newactivity.progress_percentage = self.newpercentage
                self.newactivity.weekly_report_id = self.newweeklyreport.weekly_report_id
                
                #processing comment text for the mention
                self.mentioneduser = re.findall(r'@(\w+)', self.newactivityname)
                self.exludeduser = re.findall(r">@(\w+)", self.newactivityname)
                self.mentioneduser = list(set(self.mentioneduser)^set(self.exludeduser))
                self.modifiedcommenttext = self.newactivityname
                if len(self.mentioneduser)>0:
                    for idx, mention in enumerate(self.mentioneduser):
                        #get mentioned userid
                        self.mentionuser = self.session.query(Account).filter(Account.username.contains(mention)).all()
                        
                        while(len(self.mentionuser)>1):
                            self.newmention = re.findall(r'{mention}(\w+)', self.newactivityname)
                            self.mentionuser = self.session.query(Account).filter(Account.username.contains(self.newmention)).all()
                                                                    
                        #use the full name to change the text to the link
                        self.modifiedcommenttext = self.modifiedcommenttext.replace("@" + self.mentionuser[0].username, "<a href='/newblog/" + self.mentionuser[0].username+"'>" + "@" + self.mentionuser[0].username + "</a>")
                        print(self.modifiedcommenttext)
                        
                        #notify mentioned user
                        self.mentionnotification = Notification(self.mentionuser[0].user_id, self.newuser.user_id, self.newweeklyreport.weekly_report_id, self.newuser.username, 5, "mentioned you: " + self.newactivityname, 1, self.newactivity.activity_id)
                        self.session.add(self.mentionnotification)
                
                self.newactivity.activity_name = self.modifiedcommenttext
                
                #commit all the data to database
                self.session.commit()
                
                #redirecting the page
                if(self.activitylocation == 7):
                    self.redirect('/newblog/'+self.signeduser+'/projectadmin?date=' + self.datestart.strftime("%Y-%m-%d %H:%M:%S.%f"))
                elif(self.activitylocation == 3):
                    self.projectname = self.session.query(Project).filter(Project.project_id == self.newactivity.project_id).first()
                    self.redirect('/newblog/'+self.signeduser+'/project?name=' + self.projectname.project_name)
                else:
                    self.redirect('/newblog/'+self.signeduser + "?date=" + self.datestart.strftime("%Y-%m-%d %H:%M:%S.%f"))
        
        self.session.close()
            
        

class DeleteActivity(BaseHandler):
    @tornado.web.authenticated
    def get(self):
        homeBase.init(self)
        deleteactivityid = self.get_argument("deleteactivityid", default=None)
        self.activitylocation = int(self.get_argument('activitylocation',default=7))
        self.activity = self.session.query(Activity).filter(Activity.activity_id == deleteactivityid).first()
        self.projectname = self.session.query(Project).filter(Project.project_id == self.activity.project_id).first()
        self.weeklyreport =  self.session.query(WeeklyReport).filter(WeeklyReport.weekly_report_id == Activity.weekly_report_id).first()
        
        self.userexp = self.session.query(Account).filter(Account.user_id == self.activity.user_id).first()
        self.userexp.exp = self.userexp.exp - 1 
        
        self.session.query(Activity).filter(Activity.activity_id == deleteactivityid).delete()
                
        self.session.commit()
        
        #redirecting the page
        if(self.activitylocation == 7):
            self.redirect('/newblog/'+self.signeduser+'/projectadmin?date=' + self.weeklyreport.date_range_start.strftime("%Y-%m-%d %H:%M:%S.%f"))
        elif(self.activitylocation == 3):
            self.redirect('/newblog/'+self.signeduser+'/project?name=' + self.projectname.project_name)
        else:
            self.redirect('/newblog/'+self.signeduser + "?date=" + self.weeklyreport.date_range_start.strftime("%Y-%m-%d %H:%M:%S.%f"))
        
        self.session.close()

class ProjectAdminHandler(BaseHandler):
    @tornado.web.authenticated
    def get(self, userName):
        homeBase.init(self)
        self.title = "Project Admin - New Blog"
        self.menu = 2
        self.date = self.get_argument('date', None)
        self.user_projectlist = self.session.query(Project.project_name).outerjoin(ProjectMember).outerjoin(Account).filter(ProjectMember.user_id == self.user.user_id)
        self.adminmonth = datetime.today()
        if self.date is None:
            self.activitylist = self.session.query(Activity, WeeklyReport).outerjoin(WeeklyReport).filter(Activity.user_id == self.user.user_id).filter(Activity.project_id == 7).filter(extract('month',WeeklyReport.date_range_start)==datetime.today().month).order_by(WeeklyReport.date_range_start.desc()).all()
        else:
            self.activitylist = self.session.query(Activity, WeeklyReport).outerjoin(WeeklyReport).filter(Activity.user_id == self.user.user_id).filter(Activity.project_id == 7).filter(extract('month',WeeklyReport.date_range_start)==datetime.strptime(self.date, "%Y-%m-%d %H:%M:%S.%f").month).order_by(WeeklyReport.date_range_start.desc()).all()
            self.adminmonth = datetime.strptime(self.date, "%Y-%m-%d %H:%M:%S.%f")
        if userName == self.signeduser: 
            self.visitor = 0
            self.user_projectlist = self.session.query(Project).outerjoin(ProjectMember).outerjoin(Account).filter(ProjectMember.user_id == self.user.user_id).all()
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
        self.render("newblog/project_admin.html", title = self.title, userName = userName, user = self.user, avatarURL = self.avatarURL, projectgrouplist = self.projectgrouplist, projectlist = self.user_projectlist, menu = self.menu, activitylist = self.activitylist, adminmonth = self.adminmonth, userlevel = self.user_level, maxexp = self.maxexp, visitor = self.visitor, notifications = self.notifications)
        self.session.close()
        
    def post(self, userName):
        homeBase.init(self)
        self.title = "Project Admin - New Blog"
        self.menu = 2
        newmonth = datetime.strptime(self.get_argument('newmonth', default=datetime.today().month), '%B %Y')
        
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
        
        self.user_projectlist = self.session.query(Project.project_name).outerjoin(ProjectMember).outerjoin(Account).filter(ProjectMember.user_id == self.user.user_id)
        self.activitylist = self.session.query(Activity, WeeklyReport).outerjoin(WeeklyReport).filter(Activity.user_id == self.user.user_id).filter(Activity.project_id == 7).filter(extract('month',WeeklyReport.date_range_start)==newmonth.month).all()
        self.render("newblog/project_admin.html", title = self.title, userName = userName, user = self.user, avatarURL = self.avatarURL, projectgrouplist = self.projectgrouplist, projectlist = self.user_projectlist, menu = self.menu, activitylist = self.activitylist, adminmonth = newmonth, userlevel = self.user_level, maxexp = self.maxexp, visitor = self.visitor, notifications = self.notifications)
        self.session.close()
        

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
        
        self.render("newblog/leaderboard.html", title = self.title, menu = self.menu, userName = userName, avatarURL = self.avatarURL, user = self.user, projectgrouplist = self.projectgrouplist, projectlist = self.user_projectlist, leaderboard = self.leaderboards, userlevel = self.user_level, userrank = self.userindex, maxexp = self.maxexp, visitor = self.visitor, notifications = self.notifications)
        
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
        self.newweeklyreportid = self.get_argument('newweeklyreportid', default=0)
        self.newstars = self.get_argument('newstars', default=0)
        
        self.newuser = self.session.query(Account).filter(Account.user_id == self.newuserid).first()
        self.weeklyreport = self.session.query(WeeklyReport).filter(WeeklyReport.weekly_report_id == self.newweeklyreportid).first()
        
        newcomment = Comment(self.newcommentext,self.newuserid,self.newcommentedby,self.weeklyreport.weekly_report_id,0,self.newstars)
        self.session.add(newcomment)
        self.session.flush()
        
        if(self.newuserid != self.newcommentedby):
            self.newnotification = Notification(self.newuserid, self.newcommentedby, self.newweeklyreportid, self.newuser.username, 0, "commented: " + self.newcommentext, 1, newcomment.comment_id)
            self.session.add(self.newnotification)
        
        #processing comment text for the mention
        self.mentioneduser = re.findall(r'@(\w+)', self.newcommentext)
        self.modifiedcommenttext = self.newcommentext
        if len(self.mentioneduser)>0:
            for idx, mention in enumerate(self.mentioneduser):
                #get mentioned userid
                self.mentionuser = self.session.query(Account).filter(Account.username.contains(mention)).all()
                
                while(len(self.mentionuser)>1):
                    self.newmention = re.findall(r'{mention}(\w+)', self.self.newcommentext)
                    self.mentionuser = self.session.query(Account).filter(Account.username.contains(self.newmention)).all()
                                                              
                #use the full name to change the text to the link
                self.modifiedcommenttext = self.modifiedcommenttext.replace("@" + self.mentionuser[0].username, "<a href='/newblog/" + self.mentionuser[0].username+"'>" + "@" + self.mentionuser[0].username + "</a>")
                print(self.modifiedcommenttext)
                
                #notify mentioned user
                self.mentionnotification = Notification(self.mentionuser[0].user_id, self.newcommentedby, self.newweeklyreportid, self.newuser.username, 5, "mentioned you: " + self.newcommentext, 1, newcomment.comment_id)
                self.session.add(self.mentionnotification)
        
        newcomment.comment_text = self.modifiedcommenttext
        
        self.userexp = self.session.query(Account).filter(Account.user_id == self.newuserid).first()
        self.userexp.exp = self.userexp.exp + 1
        
        self.session.commit()
        
        self.redirect("/newblog/" + self.newuser.username + "?date=" + self.weeklyreport.date_range_start.strftime("%Y-%m-%d %H:%M:%S.%f"))
        
        self.session.close()
        
class EditCommentHandler(BaseHandler):
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
        
        self.newcommentid = self.get_argument('newcommentid', default=0)
        self.newcommenttext = self.get_argument('newcommenttext', default='')
        self.newstars = self.get_argument('newstars', default=0)
        
        if self.session.query(exists().where(Comment.comment_id == self.newcommentid)).scalar():
            self.comment = self.session.query(Comment).filter(Comment.comment_id == self.newcommentid).first()
            self.comment.comment_text = self.newcommenttext
            self.comment.stars = self.newstars
            self.comment.created_on = datetime.now()
            self.newuser = self.session.query(Account).filter(Account.user_id == self.comment.user_id).first()
            
            if(self.comment.user_id != self.comment.commented_by):
                self.newnotification = Notification(self.comment.user_id, self.comment.commented_by, self.comment.weekly_report_id, self.newuser.username, 0, "edited comment: " + self.newcommenttext, 1, self.comment.comment_id)
                self.session.add(self.newnotification)
        
            #processing comment text for the mention
            self.mentioneduser = re.findall(r'@(\w+)', self.newcommenttext)
            self.exludeduser = re.findall(r">@(\w+)", self.newcommenttext)
            self.mentioneduser = list(set(self.mentioneduser)^set(self.exludeduser))
            self.modifiedcommenttext = self.newcommenttext
            if len(self.mentioneduser)>0:
                for idx, mention in enumerate(self.mentioneduser):
                    #get mentioned userid
                    self.mentionuser = self.session.query(Account).filter(Account.username.contains(mention)).all()
                    
                    while(len(self.mentionuser)>1):
                        self.newmention = re.findall(r'{mention}(\w+)', self.self.newcommenttext)
                        self.mentionuser = self.session.query(Account).filter(Account.username.contains(self.newmention)).all()
                                                                
                    #use the full name to change the text to the link
                    self.modifiedcommenttext = self.modifiedcommenttext.replace("@" + self.mentionuser[0].username, "<a href='/newblog/" + self.mentionuser[0].username+"'>" + "@" + self.mentionuser[0].username + "</a>")
                    print(self.modifiedcommenttext)
                    
                    #notify mentioned user
                    self.mentionnotification = Notification(self.mentionuser[0].user_id, self.comment.commented_by, self.comment.weekly_report_id, self.newuser.username, 5, "mentioned you: " + self.newcommenttext, 1, self.comment.comment_id)
                    self.session.add(self.mentionnotification)
            
            self.comment.comment_text = self.modifiedcommenttext
            
            self.weeklyreport = self.session.query(WeeklyReport).filter(WeeklyReport.weekly_report_id == self.comment.weekly_report_id).first()
            
            self.session.commit()
            self.redirect("/newblog/" + self.newuser.username + "?date=" + self.weeklyreport.date_range_start.strftime("%Y-%m-%d %H:%M:%S.%f"))
        
        self.session.close()
        
class DeleteCommentHandler(BaseHandler):
    @tornado.web.authenticated
    def get(self):
        homeBase.init(self)
        deletecommentid = self.get_argument("deletecommentid", default=None)
        
        self.comment = self.session.query(Comment).filter(Comment.comment_id == deletecommentid).first()
        self.newuser = self.session.query(Account).filter(Account.user_id == self.comment.user_id).first()
        self.notification = self.session.query(Notification).filter(Notification.reference_type == 1).filter(Notification.reference_id == self.comment.comment_id).filter(Notification.sender_id == self.comment.commented_by).first()
        self.weeklyreport = self.session.query(WeeklyReport).filter(WeeklyReport.weekly_report_id == self.comment.weekly_report_id).first()
        
        self.session.query(Notification).filter(Notification.reference_type == 1).filter(Notification.reference_id == self.comment.comment_id).filter(Notification.sender_id == self.comment.commented_by).delete()
        self.userexp = self.session.query(Account).filter(Account.user_id == self.comment.commented_by).first()
        self.userexp.exp = self.userexp.exp - 1
        
        self.replies = self.session.query(Reply).filter(Reply.parent_comment_id == deletecommentid).all()
        
        if self.session.query(exists().where(Reply.parent_comment_id == deletecommentid)).scalar():
            for reply in self.replies:
                self.session.query(ReplyLike).filter(ReplyLike.reply_id == reply.reply_id).delete()
        
        self.session.query(Reply).filter(Reply.parent_comment_id == deletecommentid).delete()
        self.session.query(Like).filter(Like.comment_id == deletecommentid).delete()        
        self.session.query(Comment).filter(Comment.comment_id == deletecommentid).delete()
        
        self.session.commit()
        self.redirect("/newblog/" + self.newuser.username + "?date=" + self.weeklyreport.date_range_start.strftime("%Y-%m-%d %H:%M:%S.%f"))
        self.session.close()

class AddLikeHandler(BaseHandler):
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
        
        self.newuserid = self.get_argument('newuserid', default=0)
        self.newcommentid = self.get_argument('newcommentid', default=0)
        self.newweeklyreportid = self.get_argument('newweeklyreportid', default=0)
        
        self.newlike = Like(self.newuserid, self.newweeklyreportid, self.newcommentid)
        self.session.add(self.newlike)
        self.session.flush()
        
        self.comment = self.session.query(Comment).filter(Comment.comment_id == self.newcommentid).first()
        self.comment.like_count = self.comment.like_count + 1
        
        self.user = self.session.query(Account).filter(Account.user_id == self.comment.user_id).first()
        self.weeklyreporturl = self.session.query(WeeklyReport).filter(WeeklyReport.weekly_report_id == self.newweeklyreportid).first()
        
        if(self.comment.user_id != self.comment.commented_by):
            self.newnotification = Notification(self.comment.user_id, self.comment.commented_by, self.newweeklyreportid, self.user.username, 0, "like this comment: " + self.comment.comment_text, 2, self.newlike.like_id)
            self.session.add(self.newnotification)
        
        self.userexp = self.session.query(Account).filter(Account.user_id == self.newuserid).first()
        self.userexp.exp = self.userexp.exp + 1
        
        self.session.commit()
        
        
        self.redirect("/newblog/" + self.user.username  + "?date=" + self.weeklyreporturl.date_range_start.strftime("%Y-%m-%d %H:%M:%S.%f"))
        self.session.close()

class DeleteLikeHandler(BaseHandler):
    @tornado.web.authenticated
    def get(self):
        homeBase.init(self)
        deletelikeid = self.get_argument("deletelikeid", default=None)
        
        self.like = self.session.query(Like).filter(Like.like_id == deletelikeid).first()
        self.comment = self.session.query(Comment).filter(Comment.comment_id == self.like.comment_id).first()
        self.comment.like_count = self.comment.like_count - 1
        self.userdata = self.session.query(Account).filter(Account.user_id == self.comment.user_id).first()
        self.weeklyreportdata = self.session.query(WeeklyReport).filter(WeeklyReport.weekly_report_id == self.like.weekly_report_id).first()
        self.notification = self.session.query(Notification).filter(Notification.reference_type == 2).filter(Notification.reference_id == self.like.like_id).filter(Notification.sender_id == self.comment.commented_by).first()
        
        self.session.query(Notification).filter(Notification.reference_type == 2).filter(Notification.reference_id == self.like.like_id).filter(Notification.sender_id == self.comment.commented_by).delete()
        
        self.userexp = self.session.query(Account).filter(Account.user_id == self.like.user_id).first()
        self.userexp.exp = self.userexp.exp - 1
        
        self.session.query(Like).filter(Like.like_id == deletelikeid).delete()
        
        self.session.commit()
        self.redirect("/newblog/" + self.userdata.username + "?date=" + self.weeklyreportdata.date_range_start.strftime("%Y-%m-%d %H:%M:%S.%f"))
        self.session.close()

class AddReplyHandler(BaseHandler):
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
        
        self.newreplytext = self.get_argument("newreplytext", default="")
        self.newparentcommentid = self.get_argument("newparentcommentid", default=0)
        self.newuserid = self.user.user_id
        
        self.reply = Reply(self.newreplytext, self.newparentcommentid, self.newuserid, 0)
        self.session.add(self.reply)
        self.session.flush()
        
        self.comment = self.session.query(Comment).filter(Comment.comment_id == self.newparentcommentid).first()
        self.newuser = self.session.query(Account).filter(Account.user_id == self.comment.user_id).first()
        self.newweeklyreportid = self.session.query(WeeklyReport).filter(WeeklyReport.weekly_report_id == self.comment.weekly_report_id).first()

        if (self.comment.user_id != self.newuserid):
            self.notification = Notification(self.comment.user_id, self.newuserid, self.newweeklyreportid.weekly_report_id, self.newuser.username, 0, "commented: " + self.newreplytext, 3, self.reply.reply_id)
            self.session.add(self.notification)
        
        if (self.comment.commented_by != self.newuserid):
            self.notification_comment = Notification(self.comment.commented_by, self.newuserid, self.newweeklyreportid.weekly_report_id, self.newuser.username, 0, "replied: " + self.newreplytext, 3, self.reply.reply_id)
            self.session.add(self.notification_comment)   
        
        self.userexp = self.session.query(Account).filter(Account.user_id == self.newuserid).first()
        self.userexp.exp = self.userexp.exp + 1
        
        #processing comment text for the mention
        self.mentioneduser = re.findall(r'@(\w+)', self.newreplytext)
        self.modifiedcommenttext = self.newreplytext
        if len(self.mentioneduser)>0:
            for idx, mention in enumerate(self.mentioneduser):
                #get mentioned userid
                self.mentionuser = self.session.query(Account).filter(Account.username.contains(mention)).all()
                
                while(len(self.mentionuser)>1):
                    self.newmention = re.findall(r'{mention}(\w+)', self.self.newreplytext)
                    self.mentionuser = self.session.query(Account).filter(Account.username.contains(self.newmention)).all()
                                                            
                #use the full name to change the text to the link
                self.modifiedcommenttext = self.modifiedcommenttext.replace("@" + self.mentionuser[0].username, "<a href='/newblog/" + self.mentionuser[0].username+"'>" + "@" + self.mentionuser[0].username + "</a>")
                print(self.modifiedcommenttext)
                
                #notify mentioned user
                self.mentionnotification = Notification(self.mentionuser[0].user_id, self.newuserid, self.comment.weekly_report_id, self.newuser.username, 5, "mentioned you: " + self.newreplytext, 1, self.reply.reply_id)
                self.session.add(self.mentionnotification)
        
        self.reply.reply_text = self.modifiedcommenttext
        
        self.session.commit()
        
        self.redirect("/newblog/" + self.newuser.username + "?date=" + self.newweeklyreportid.date_range_start.strftime("%Y-%m-%d %H:%M:%S.%f"))
        
        self.session.close()

    
class EditReplyHandler(BaseHandler):
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
        
        self.newreplyid = self.get_argument("newreplyid", default=0)
        self.newreplytext = self.get_argument("newreplytext", default="")
        
        if self.session.query(exists().where(Reply.reply_id == self.newreplyid)).scalar():
            self.reply = self.session.query(Reply).filter(Reply.reply_id == self.newreplyid).first()
            self.reply.reply_text = self.newreplytext
            self.reply.created_on = datetime.now()
            
            self.comment = self.session.query(Comment).filter(Comment.comment_id == self.reply.parent_comment_id).first()
            self.newuser = self.session.query(Account).filter(Account.user_id == self.comment.user_id).first()
        
            if(self.comment.user_id !=  self.reply.user_id):
                self.notification = Notification(self.comment.user_id, self.reply.user_id, self.comment.weekly_report_id, self.newuser.username, 0, "edited comment: " + self.newreplytext, 3, self.reply.reply_id)
                self.session.add(self.notification)
            
            if(self.comment.commented_by != self.reply.user_id):
                self.notification_comment = Notification(self.comment.commented_by, self.reply.user_id, self.comment.weekly_report_id, self.newuser.username, 0, "edited reply: " + self.newreplytext, 3, self.reply.reply_id)
                self.session.add(self.notification_comment)
            
            #processing comment text for the mention
            self.mentioneduser = re.findall(r'@(\w+)', self.newreplytext)
            self.exludeduser = re.findall(r">@(\w+)", self.newreplytext)
            self.mentioneduser = list(set(self.mentioneduser)^set(self.exludeduser))
            self.modifiedcommenttext = self.newreplytext
            if len(self.mentioneduser)>0:
                for idx, mention in enumerate(self.mentioneduser):
                    #get mentioned userid
                    self.mentionuser = self.session.query(Account).filter(Account.username.contains(mention)).all()
                    
                    while(len(self.mentionuser)>1):
                        self.newmention = re.findall(r'{mention}(\w+)', self.self.newreplytext)
                        self.mentionuser = self.session.query(Account).filter(Account.username.contains(self.newmention)).all()
                                                                
                    #use the full name to change the text to the link
                    self.modifiedcommenttext = self.modifiedcommenttext.replace("@" + self.mentionuser[0].username, "<a href='/newblog/" + self.mentionuser[0].username+"'>" + "@" + self.mentionuser[0].username + "</a>")
                    print(self.modifiedcommenttext)
                    
                    #notify mentioned user
                    self.mentionnotification = Notification(self.mentionuser[0].user_id, self.reply.user_id, self.comment.weekly_report_id, self.newuser.username, 5, "mentioned you: " + self.newreplytext, 1, self.reply.reply_id)
                    self.session.add(self.mentionnotification)
            
            self.reply.reply_text = self.modifiedcommenttext

            self.session.commit()
            self.weeklyreport = self.session.query(WeeklyReport).filter(WeeklyReport.weekly_report_id == self.comment.weekly_report_id).first()
            self.redirect("/newblog/" + self.newuser.username + "?date=" + self.weeklyreport.date_range_start.strftime("%Y-%m-%d %H:%M:%S.%f"))
        
        self.session.close()
        
class DeleteReplyHandler(BaseHandler):
    @tornado.web.authenticated
    def get(self):
        homeBase.init(self)
        deletereplyid = self.get_argument("deletereplyid", default=None)
        
        self.reply = self.session.query(Reply).filter(Reply.reply_id == deletereplyid).first()
        self.comment = self.session.query(Comment).filter(Comment.comment_id == self.reply.parent_comment_id).first()
        self.weeklyreport = self.session.query(WeeklyReport).filter(WeeklyReport.weekly_report_id == self.comment.weekly_report_id).first()
        self.user = self.session.query(Account).filter(Account.user_id == self.comment.user_id).first()
        
        self.notification_comment = self.session.query(Notification).filter(Notification.reference_type == 3).filter(Notification.reference_id == self.reply.reply_id).filter(Notification.recipient_id == self.comment.user_id).first()
        
        self.notification = self.session.query(Notification).filter(Notification.reference_type == 3).filter(Notification.reference_id == self.reply.reply_id).filter(Notification.recipient_id == self.comment.commented_by).first()
        
        self.session.query(Notification).filter(Notification.reference_type == 3).filter(Notification.reference_id == self.reply.reply_id).filter(Notification.recipient_id == self.comment.user_id).delete()
        self.session.query(Notification).filter(Notification.reference_type == 3).filter(Notification.reference_id == self.reply.reply_id).filter(Notification.recipient_id == self.comment.commented_by).delete()
        
        self.userexp = self.session.query(Account).filter(Account.user_id == self.reply.user_id).first()
        self.userexp.exp = self.userexp.exp - 1
        
        self.session.query(ReplyLike).filter(ReplyLike.reply_id == deletereplyid).delete()
        self.session.query(Reply).filter(Reply.reply_id == deletereplyid).delete()
        
        self.session.commit()
        
        self.redirect("/newblog/" + self.user.username + "?date=" + self.weeklyreport.date_range_start.strftime("%Y-%m-%d %H:%M:%S.%f"))
        
        self.session.close()
        
class AddReplyLikeHandler(BaseHandler):
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
        
        self.newuserid = self.get_argument("newuserid", default=0)
        self.newreplyid = self.get_argument("newreplyid", default=0)
        self.newweeklyreportid = self.get_argument("newweeklyreportid", default=0)
        
        self.likereply = ReplyLike(self.newreplyid, self.newweeklyreportid, self.newuserid)
        self.session.add(self.likereply)
        self.session.flush()
        
        self.reply = self.session.query(Reply).filter(Reply.reply_id == self.newreplyid).first()
        self.reply.like_count = self.reply.like_count + 1
        
        self.comment = self.session.query(Comment).filter(Comment.comment_id == self.reply.parent_comment_id).first()
        self.weeklyreport = self.session.query(WeeklyReport).filter(WeeklyReport.weekly_report_id == self.comment.weekly_report_id).first()
        self.user = self.session.query(Account).filter(Account.user_id == self.comment.user_id).first()
        
        if str(self.reply.user_id) != self.likereply.user_id:     
            self.notification = Notification(self.reply.user_id, self.newuserid, self.weeklyreport.weekly_report_id, self.user.username, 0, "liked your reply: " + self.reply.reply_text, 4, self.likereply.like_reply_id)
            self.session.add(self.notification)
            self.session.flush()
        
        self.userexp = self.session.query(Account).filter(Account.user_id == self.newuserid).first()
        self.userexp.exp = self.userexp.exp + 1
        self.session.commit()
        
        self.redirect("/newblog/" + self.user.username + "?date=" + self.weeklyreport.date_range_start.strftime("%Y-%m-%d %H:%M:%S.%f"))
        
        self.session.close()
        
        
class DeleteReplyLikeHandler(BaseHandler):
    @tornado.web.authenticated
    def get(self):
        homeBase.init(self)
        deletereplylikeid = self.get_argument("deletereplylikeid", default=None)
        
        self.replylike = self.session.query(ReplyLike).filter(ReplyLike.like_reply_id == deletereplylikeid).first()
        self.reply = self.session.query(Reply).filter(Reply.reply_id == self.replylike.reply_id).first()
        self.comment = self.session.query(Comment).filter(Comment.comment_id == self.reply.parent_comment_id).first()
        self.weeklyreport = self.session.query(WeeklyReport).filter(WeeklyReport.weekly_report_id == self.comment.weekly_report_id).first()
        self.user = self.session.query(Account).filter(Account.user_id == self.comment.user_id).first()
        
        self.notification = self.session.query(Notification).filter(Notification.reference_type == 4).filter(Notification.reference_id == self.replylike.like_reply_id).filter(Notification.sender_id == self.replylike.user_id).first()
        
        self.session.query(Notification).filter(Notification.reference_type == 4).filter(Notification.reference_id == self.replylike.like_reply_id).filter(Notification.sender_id == self.replylike.user_id).delete()
        self.session.query(ReplyLike).filter(ReplyLike.like_reply_id == deletereplylikeid).delete()
        self.reply.like_count = self.reply.like_count - 1
        
        self.userexp = self.session.query(Account).filter(Account.user_id == self.replylike.user_id).first()
        self.userexp.exp = self.userexp.exp - 1
        
        self.session.commit()
        
        self.redirect("/newblog/" + self.user.username + "?date=" + self.weeklyreport.date_range_start.strftime("%Y-%m-%d %H:%M:%S.%f"))
        
        self.session.close()
    
class ReadNofiticationHandler(BaseHandler):
    @tornado.web.authenticated
    def get(self):
        homeBase.init(self)
        
        self.newnotificationid = self.get_argument("newnotificationid", default=0)
        
        self.notification = self.session.query(Notification).filter(Notification.notification_id == self.newnotificationid).first()
        self.notification.click_by_user = 1
        self.session.commit() 
        self.weeklyreport = self.session.query(WeeklyReport).filter(WeeklyReport.weekly_report_id == self.notification.link_weekly_report_id).first()
        
        self.redirect("/newblog/"+self.notification.link_username+"?date="+self.weeklyreport.date_range_start.strftime("%Y-%m-%d %H:%M:%S.%f"))
        
        self.session.close()
    
class ViewProjectHandler(BaseHandler):
    @tornado.web.authenticated
    def get(self, userName):
        homeBase.init(self)
        self.name = self.get_argument('name', '')
        self.title = self.name + " Project - New Blog"
        self.menu = 5
        self.projectdata = None
        self.projectmembers = None
        self.projectmembersdata = list()
        self.activitydata = None

        if self.name:
            self.projectdata = self.session.query(Project).filter(Project.project_name.contains(self.name)).first()
            self.projectmembers = self.session.query(Account).outerjoin(ProjectMember).outerjoin(Project).filter(ProjectMember.project_id == self.projectdata.project_id).all()
            self.menu = 4 + self.projectdata.project_id
            for member in self.projectmembers:
                self.param = {'Bucket': BUCKET_NAME, 'Key': 'members/' + member.username  + '/avatar.png'}
                self.memberphoto = s3c.generate_presigned_url('get_object', self.param)
                self.activitydata = self.session.query(Activity, WeeklyReport).outerjoin(WeeklyReport).filter(Activity.user_id == member.user_id).filter(Activity.project_id == self.projectdata.project_id).order_by(Activity.weekly_report_id.desc()).all()
                self.members = {"user_id": member.user_id, "username": member.username, "photoURL": self.memberphoto, "activitydata": self.activitydata} 
                self.projectmembersdata.append(self.members)

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
        
        # reflection
        reflection_exists = 0
        reflection_content = None
        if self.session.query(exists().where(Reflection.weekly_report_id == self.weeklyreport.weekly_report_id).where(Reflection.user_id == self.user.user_id)).scalar():
            reflection_exists = 1
            reflection_content = self.session.query(Reflection).filter(Reflection.weekly_report_id == self.weeklyreport.weekly_report_id).filter(Reflection.user_id == self.user.user_id).first()
        
        self.render("newblog/projects.html", title = self.title, userName = self.signeduser, user = self.user, avatarURL = self.avatarURL, projectgrouplist = self.projectgrouplist,reflection_exists = reflection_exists, reflection_content = reflection_content, projectlist = self.user_projectlist, menu = self.menu, userlevel = self.user_level, maxexp = self.maxexp, visitor = self.visitor, notifications = self.notifications, projectdata = self.projectdata, projectmembers = self.projectmembersdata)
        self.session.close()
        
class LatestBlogHandler(BaseHandler):
    @tornado.web.authenticated
    def get(self, userName):
        homeBase.init(self)
        self.title = "Latest CHEC Blog"
        self.menu = 4
        self.projectdata = None
        self.projectmembers = None
        self.projectmembersdata = list()
        self.activitydata = None
        self.visitor = 0
        
        if userName == self.signeduser: 
            self.visitor = 0
        else:
            self.visitor = 1
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

        self.latestusers = self.session.query(Account).filter(Account.degree > 0).all() 

        self.latestusersdata = list()
        # get activity and project for every user
        for latestuser in self.latestusers:
            self.allactivity = []
            self.thisweekactivity = []
            self.nextweekactivity = []
            #get activities for each projects
            if self.session.query(exists().where(Activity.weekly_report_id == self.weeklyreport.weekly_report_id).where(Activity.user_id == latestuser.user_id)).scalar():   
                self.thisweekprojectlist = self.session.query(Project).outerjoin(Activity).filter(Activity.user_id == latestuser.user_id).filter(Activity.weekly_report_id == self.weeklyreport.weekly_report_id)
                
                self.nextweekprojectlist = self.session.query(Project).outerjoin(Activity).filter(Activity.user_id == latestuser.user_id).filter(Activity.weekly_report_id == self.nextweeklyreport.weekly_report_id)
                
                for project in self.thisweekprojectlist:
                    self.thisweekactivity.append([project,self.session.query(Activity, WeeklyReport).outerjoin(WeeklyReport).filter(Activity.user_id == latestuser.user_id).filter(Activity.project_id == project.project_id).filter(WeeklyReport.weekly_report_id == self.weeklyreport.weekly_report_id).all()])
                
                for project in self.nextweekprojectlist:
                    self.nextweekactivity.append([project,self.session.query(Activity, WeeklyReport).outerjoin(WeeklyReport).filter(Activity.user_id == latestuser.user_id).filter(Activity.project_id == project.project_id).filter(WeeklyReport.weekly_report_id == self.nextweeklyreport.weekly_report_id).all()])
                
                self.allactivity.append(self.thisweekactivity)
                self.allactivity.append(self.nextweekactivity)

                # get user name and photo
                self.param = {'Bucket': BUCKET_NAME, 'Key': 'members/' + latestuser.username  + '/avatar.png'}
                self.photoURL = s3c.generate_presigned_url('get_object', self.param) 
                self.daterange = "" + self.weeklyreport.date_range_start.strftime("%B %d") + " - " + self.weeklyreport.date_range_end.strftime("%B %d")
                self.datainside = {"user_id": latestuser.user_id, "username": latestuser.username, "photoURL": self.photoURL, "daterange": self.daterange, "allactivity": self.allactivity}
                self.latestusersdata.append(self.datainside)
                print(self.latestusersdata)
                print("1")
                
            else:

                # date_range_start < this.weeklyreport
                self.latestweeklyreports = self.session.query(WeeklyReport).outerjoin(Activity).filter(Activity.user_id == latestuser.user_id).filter(WeeklyReport.date_range_start < self.weeklyreport.date_range_start).distinct().order_by(WeeklyReport.date_range_start.desc()).limit(3).all()


                # get the prev. weeklyreport id, if the prev has activity, show the prev as next week projectlist and nextweekactivity
                if self.latestweeklyreports:
                    if (self.latestweeklyreports[0].date_range_start - self.latestweeklyreports[1].date_range_start) <= timedelta(days=7):
                        self.thisweekprojectlist = self.session.query(Project).outerjoin(Activity).filter(Activity.user_id == latestuser.user_id).filter(Activity.weekly_report_id == self.latestweeklyreports[1].weekly_report_id)
                        
                        self.nextweekprojectlist = self.session.query(Project).outerjoin(Activity).filter(Activity.user_id == latestuser.user_id).filter(Activity.weekly_report_id == self.latestweeklyreports[0].weekly_report_id)
                        
                        for project in self.thisweekprojectlist:
                            self.thisweekactivity.append([project,self.session.query(Activity, WeeklyReport).outerjoin(WeeklyReport).filter(Activity.user_id == latestuser.user_id).filter(Activity.project_id == project.project_id).filter(WeeklyReport.weekly_report_id == self.latestweeklyreports[1].weekly_report_id).all()])
                        
                        for project in self.nextweekprojectlist:
                            self.nextweekactivity.append([project,self.session.query(Activity, WeeklyReport).outerjoin(WeeklyReport).filter(Activity.user_id == latestuser.user_id).filter(Activity.project_id == project.project_id).filter(WeeklyReport.weekly_report_id == self.latestweeklyreports[0].weekly_report_id).all()])

                        self.allactivity.append(self.thisweekactivity)
                        self.allactivity.append(self.nextweekactivity)

                        # get user name and photo
                        self.param = {'Bucket': BUCKET_NAME, 'Key': 'members/' + latestuser.username  + '/avatar.png'}
                        self.photoURL = s3c.generate_presigned_url('get_object', self.param) 
                        self.daterange = "" + self.latestweeklyreports[1].date_range_start.strftime("%B %d") + " - " + self.latestweeklyreports[1].date_range_end.strftime("%B %d")
                        self.datainside = {"user_id": latestuser.user_id, "username": latestuser.username, "photoURL": self.photoURL, "daterange": self.daterange, "allactivity": self.allactivity}
                        self.latestusersdata.append(self.datainside)
                        print(self.latestusersdata)
                        print("2")

                    else:
                        # if the prev does not has activity, show the current as this week and next week will be empty 

                        # get next weeklyreport data
                        self.nextweek = self.latestweeklyreports[0].date_range_start + timedelta(days=7)
                        self.endnextweek = self.latestweeklyreports[0].date_range_start + timedelta(days=14)
                        if self.session.query(~exists().where(WeeklyReport.date_range_start+timedelta(days=1) >= self.nextweek).where(WeeklyReport.date_range_start < self.endnextweek)).scalar():
                            self.newweeklyreport = WeeklyReport(self.nextweek)
                            self.session.add(self.newweeklyreport)
                            self.session.flush()
                        self.nextweeklyreport = self.session.query(WeeklyReport).filter(WeeklyReport.date_range_start+timedelta(days=1) >= self.nextweek).filter(WeeklyReport.date_range_start < self.endnextweek).first()

                        # get project and activities
                        self.thisweekprojectlist = self.session.query(Project).outerjoin(Activity).filter(Activity.user_id == latestuser.user_id).filter(Activity.weekly_report_id == self.latestweeklyreports[0].weekly_report_id)
                        
                        self.nextweekprojectlist = self.session.query(Project).outerjoin(Activity).filter(Activity.user_id == latestuser.user_id).filter(Activity.weekly_report_id == self.nextweeklyreport.weekly_report_id)
                        
                        for project in self.thisweekprojectlist:
                            self.thisweekactivity.append([project,self.session.query(Activity, WeeklyReport).outerjoin(WeeklyReport).filter(Activity.user_id == latestuser.user_id).filter(Activity.project_id == project.project_id).filter(WeeklyReport.weekly_report_id == self.latestweeklyreports[0].weekly_report_id).all()])
                        
                        for project in self.nextweekprojectlist:
                            self.nextweekactivity.append([project,self.session.query(Activity, WeeklyReport).outerjoin(WeeklyReport).filter(Activity.user_id == latestuser.user_id).filter(Activity.project_id == project.project_id).filter(WeeklyReport.weekly_report_id == self.nextweeklyreport.weekly_report_id).all()])

                        self.allactivity.append(self.thisweekactivity)
                        self.allactivity.append(self.nextweekactivity)

                        # get user name and photo
                        self.param = {'Bucket': BUCKET_NAME, 'Key': 'members/' + latestuser.username  + '/avatar.png'}
                        self.photoURL = s3c.generate_presigned_url('get_object', self.param) 
                        self.daterange = "" + self.latestweeklyreports[0].date_range_start.strftime("%B %d") + " - " + self.latestweeklyreports[0].date_range_end.strftime("%B %d")
                        self.datainside = {"user_id": latestuser.user_id, "username": latestuser.username, "photoURL": self.photoURL, "daterange": self.daterange, "allactivity": self.allactivity}
                        self.latestusersdata.append(self.datainside)
                        print(self.latestusersdata)
                        print("3")
                else:
                    # empty blog
                    # get user name and photo
                    self.param = {'Bucket': BUCKET_NAME, 'Key': 'members/' + latestuser.username  + '/avatar.png'}
                    self.photoURL = s3c.generate_presigned_url('get_object', self.param) 
                    self.daterange = "" + self.weeklyreport.date_range_start.strftime("%B %d") + " - " + self.weeklyreport.date_range_end.strftime("%B %d")
                    self.datainside = {"user_id": latestuser.user_id, "username": latestuser.username, "photoURL": self.photoURL, "daterange": self.daterange, "allactivity": self.allactivity}
                    self.latestusersdata.append(self.datainside)
                    print(self.latestusersdata)
                    print("4")

        print(self.latestusersdata)
        print("total")

        self.render("newblog/latestblog.html", title = self.title, userName = self.signeduser, user = self.user, avatarURL = self.avatarURL, projectgrouplist = self.projectgrouplist, menu = self.menu, userlevel = self.user_level, maxexp = self.maxexp, visitor = self.visitor, notifications = self.notifications, projectlist = self.user_projectlist, latestuserdatas = self.latestusersdata)
        self.session.close()
