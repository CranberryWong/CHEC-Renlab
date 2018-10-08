#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import tornado
import tornado.locale
import markdown
import os
import boto3 
import botocore

from handlers.base import BaseHandler
from handlers.util import *
from handlers.blog.blog import BlogURL
from boto3 import Session

# AWS S3 Configuration
BUCKET_NAME = 'chec-static'
session = Session()
credentials = session.get_credentials()
current_credentials = credentials.get_frozen_credentials()
s3 = boto3.resource('s3')
s3c = boto3.client('s3',aws_access_key_id=current_credentials.access_key,aws_secret_access_key=current_credentials.secret_key,aws_session_token=current_credentials.token)

DocURL = os.path.join(os.path.dirname('./..'), "static/documents")
CurriculumURL = os.path.join(DocURL, "HCIcurriculum")
ProjectURL = os.path.join(DocURL, "projects")

class PubHandler(BaseHandler):
    def get(self):
        self.title = "Publications"

        # AWS S3 access bucket
        myBucket = s3.Bucket(BUCKET_NAME)
        config = s3c._client_config
        config.signature_version = botocore.UNSIGNED
        dir = os.path.dirname("documents/publication.md")
        if not os.path.exists(dir):
            os.makedirs(dir)
        s3.Bucket(BUCKET_NAME).download_file(dir+"/publication.md", dir+"/publication.md")

        with open(os.path.join(dir, 'publication.md'), encoding='utf-8', mode="r") as f:
            content = markdown.markdown(f.read())
        self.render("home/publication.html", title = self.title, content = content)

class ResourceHandler(BaseHandler):
    @tornado.web.authenticated
    def get(self):
        self.title = 'Resource'
        userName = tornado.escape.xhtml_escape(self.current_user)
        memberList = [ x for x in os.listdir(BlogURL) if x not in ignore_list]
        with open(os.path.join(DocURL, 'resource.md'), "r") as f:
            content = markdown.markdown(f.read())            
        self.render("home/resource.html", title = self.title, memberList = memberList, content = content)

class CurriculumHandler(BaseHandler):
    def get(self):
        self.title = 'HCI Curriculum'
        year = ['2014']
        curriculumList = []
        for y in year:
            with open(os.path.join(CurriculumURL, y + '.md'), "r") as f:
                curriculumList.append(markdown.markdown(f.read(), extensions=['markdown.extensions.tables']))
        self.render("home/curriculum.html", title = self.title, curriculumList = curriculumList)

class IntroHandler(BaseHandler):
    def get(self):
        self.title = "Introduction for CHEC"
        with open(os.path.join(DocURL, 'chec.md'), "r") as f:
            content = markdown.markdown(f.read(), extensions=['markdown.extensions.tables'])
        self.render("home/page.html", title = self.title, content = content)

class FacilitesHandler(BaseHandler):
    def get(self):
        self.title = "Facilities"
        with open(os.path.join(DocURL, 'facilities.md'), "r") as f:
            content = markdown.markdown(f.read(), extensions=['markdown.extensions.tables'])
        self.render("home/facilities.html", title = self.title, content = content)

class ProjectsHandler(BaseHandler):
    def get(self):
        self.title = "Projects"
        projectList = [ x for x in os.listdir(ProjectURL) if x not in ignore_list ]
        self.render("home/projects.html", title = self.title, projectList = projectList)

class ProjectShowHandler(BaseHandler):
    def get(self, project):
        print(project)
        self.title = project
        with open(ProjectURL + '/' + project + '.md') as f:
            content = markdown.markdown(f.read())
        self.render("home/page.html", title = self.title, content = content)