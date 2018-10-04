#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import tornado
import tornado.locale
import markdown
import os
import boto3 
import botocore

from handlers.util import *
from handlers.base import BaseHandler
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

# NewsURL = os.path.join(os.path.dirname('./..'), "static/news/")
dir="news/"
class NewsHandler(BaseHandler):
    def get(self):
        self.title = "News"

        for file in myBucket.objects.filter(Prefix="news/", Delimiter = '\\'):
            dir = os.path.dirname(file.key)
            if not os.path.exists(dir):
                os.makedirs(dir)
            if file.key[-1]=="/":
                continue
            s3.Bucket(BUCKET_NAME).download_file(file.key, file.key)
        dir = dir + '/'
        newsList = [ (x, os.stat(dir + x)) for x in os.listdir(dir) if x not in ignore_list ]
        newsList = sorted(newsList, key=lambda x: x[0].rstrip('.md').split(']')[0][1:], reverse=True)
        self.render("home/news.html", title = self.title, newsList = newsList)

class NewsShowHandler(BaseHandler):
    def get(self, news):
        self.title = news
        with open(dir + "/" + news + '.md', encoding='utf-8-sig') as f:
            content = markdown.markdown(f.read())
        self.render("home/page.html", title = self.title, content = content)
