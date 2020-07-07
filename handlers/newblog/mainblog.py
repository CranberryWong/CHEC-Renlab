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

from handlers.util import *
from handlers.base import BaseHandler
from models.entity import Account
from models.entity import db_session
from datetime import datetime
from boto3 import Session

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

class MainHandler(BaseHandler):
    @tornado.web.authenticated
    def get(self, userName):
        BaseHandler.initialize(self)
        params = {'Bucket': BUCKET_NAME, 'Key': 'members/' + userName + '/avatar.png'}
        avatarURL = s3c.generate_presigned_url('get_object', params)
        self.session = db_session.getSession
        self.user = self.session.query(Account).filter(Account.username == userName).first()
        self.title = "New Blog"
        self.render("newblog/main.html", title = self.title, userName = userName, user = self.user, avatarURL = avatarURL)