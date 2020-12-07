#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import tornado
import tornado.locale
import hashlib
import os
import boto3 
import botocore
import urllib.request

from handlers.base import BaseHandler
from boto3 import Session
from datetime import datetime
from models.entity import Account
from models.entity import db_session

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

# AuthURL = os.path.join(os.path.dirname('./..'), "static/members/")

#Sign In
class SignInHandler(BaseHandler):
    def get(self):
        self.title = "Sign In"
        self.render("auth/signin.html")

    def post(self):
        username = self.get_argument("username", default="")
        password = self.get_argument("password", default="")
        #Query
        md5_password = hashlib.md5(password.encode("utf-8")).hexdigest()
        isUser = False
        AuthURL = ""

        for file in myBucket.objects.filter(Prefix="members/"+username, Delimiter = '\\'):
            if 'password.salt' in file.key:
                dir = os.path.dirname(file.key)
                if not os.path.exists(dir):
                    os.makedirs(dir)
                s3.Bucket(BUCKET_NAME).download_file(file.key, file.key)
                isUser = True
                AuthURL = file.key

        if isUser == True:
            with open(AuthURL) as f:
                pwd = f.read()
            if md5_password == pwd:
                self.message = ""
                self.set_secure_cookie('user', username)
                self.session = db_session.getSession
                self.user = self.session.query(Account).filter(Account.username == username).first()
                self.user.last_login = datetime.now()
                self.user.last_login_ip = urllib.request.urlopen('https://ident.me').read().decode('utf8')
                self.session.commit()
                self.redirect('/')
                self.session.close()
            
        self.message = "Username hasn't been signed up!"
        self.redirect('/signin')

        # memberList = [ x for x in os.listdir(AuthURL)]
        # if username in memberList:
        #     with open(AuthURL + username + '/password.salt') as f:
        #         pwd = f.read()
        #     if md5_password == pwd:
        #         self.message = ""
        #         self.set_secure_cookie('user', username)
        #         self.redirect('/')
        #     else:
        #         self.message = "Wrong Password!"
        #         self.redirect('/signin')
        # else:
        #     self.message = "Username hasn't been signed up!"
        #     self.redirect('/signin')

#Sign Out
class SignOutHandler(BaseHandler):
    def get(self):
      self.clear_cookie('user')
      self.redirect('/')