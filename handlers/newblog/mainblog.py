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
from models.entity import Account, XpEvents, ProjectGroup, Project 
from models.entity import db_session
from datetime import datetime
from boto3 import Session
from PIL import Image
from io import BytesIO 

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

class MainHandler(BaseHandler):
    @tornado.web.authenticated
    def get(self, userName):
        homeBase.init(self)
        self.user = self.session.query(Account).filter(Account.username == userName).first()
        self.title = "New Blog"
        projectgrouplist = self.session.query(ProjectGroup).order_by(ProjectGroup.project_group_name.asc()).all()
        self.render("newblog/main.html", title = self.title, userName = userName, user = self.user, avatarURL = self.avatarURL, projectgrouplist = projectgrouplist)
        
class ProfileEditHandler(BaseHandler):
    def get(self):
        homeBase.init(self)
        self.user=self.session.query(Account).filter(Account.username == self.signeduser).first()
        self.title = "New Blog"
        self.render("newblog/main.html", title = self.title, userName = self.user.username, user = self.user, avatarURL = self.avatarURL)
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
        newproject = Project(newprojectname, newprojectgroupid)
        self.session.add(newproject)
        self.session.commit()
        self.redirect("/newblog/" + self.signeduser)
        self.sesion.close()
        
        