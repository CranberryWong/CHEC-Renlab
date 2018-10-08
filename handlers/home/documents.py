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

# AWS S3 access bucket
myBucket = s3.Bucket(BUCKET_NAME)
config = s3c._client_config
config.signature_version = botocore.UNSIGNED

DocURL = os.path.join(os.path.dirname('./..'), "static/documents")
CurriculumURL = os.path.join(DocURL, "HCIcurriculum")
ProjectURL = os.path.join(DocURL, "projects")

dirDoc = os.path.dirname("documents/publication.md")
dirProjects = "documents/projects/"

class PubHandler(BaseHandler):
    def get(self):
        self.title = "Publications"

        print(dirDoc)
        if not os.path.exists(dirDoc):
            os.makedirs(dirDoc)
        s3.Bucket(BUCKET_NAME).download_file(dirDoc+"/publication.md", dirDoc+"/publication.md")

        with open(os.path.join(dirDoc, 'publication.md'), encoding='utf-8', mode="r") as f:
            content = markdown.markdown(f.read())
        self.render("home/publication.html", title = self.title, content = content)

class ResourceHandler(BaseHandler):
    @tornado.web.authenticated
    def get(self):
        self.title = 'Resource'
        userName = tornado.escape.xhtml_escape(self.current_user)

        memberList = [ x for x in os.listdir(BlogURL) if x not in ignore_list]
        
        allAvatarURL={}
        for file in myBucket.objects.filter(Prefix="members-180615/", Delimiter = '\\'):
            params = {'Bucket': BUCKET_NAME, 'Key': file.key}
            url = s3c.generate_presigned_url('get_object', params)
            # get avatar public url
            allAvatarURL[file.key] = url
        
        if not os.path.exists(dirDoc):
            os.makedirs(dirDoc)
        s3.Bucket(BUCKET_NAME).download_file(dirDoc+"/resource.md", dirDoc+"/resource.md")
        
        with open(os.path.join(dirDoc, 'resource.md'), encoding='utf-8', mode="r") as f:
            content = markdown.markdown(f.read())            
        self.render("home/resource.html", title = self.title, memberList = memberList, allAvatarURL=allAvatarURL, content = content)

class CurriculumHandler(BaseHandler):
    def get(self):
        self.title = 'HCI Curriculum'
        year = ['2014','2016','2017','2018']
        curriculumList = []
        for file in myBucket.objects.filter(Prefix="documents/HCIcurriculum/", Delimiter = '\\'):
            dir = os.path.dirname(file.key)
            if not os.path.exists(dir):
                os.makedirs(dir)
            if file.key[-1]=="/":
                continue
            if not os.path.isfile(file.key):
                s3.Bucket(BUCKET_NAME).download_file(file.key, file.key)
        for y in year:
            with open(os.path.join(dir, y + '.md'), encoding='utf-8', mode="r") as f:
                curriculumList.append(markdown.markdown(f.read(), extensions=['markdown.extensions.tables']))
        self.render("home/curriculum.html", title = self.title, curriculumList = curriculumList)

class IntroHandler(BaseHandler):
    def get(self):
        self.title = "Introduction for CHEC"

        if not os.path.exists(dirDoc):
            os.makedirs(dirDoc)
        s3.Bucket(BUCKET_NAME).download_file(dirDoc+"/chec.md", dirDoc+"/chec.md")

        with open(os.path.join(dirDoc, 'chec.md'), encoding='utf-8', mode="r") as f:
            content = markdown.markdown(f.read(), extensions=['markdown.extensions.tables'])
        self.render("home/page.html", title = self.title, content = content)

class FacilitesHandler(BaseHandler):
    def get(self):
        self.title = "Facilities"

        if not os.path.exists(dirDoc):
            os.makedirs(dirDoc)
        s3.Bucket(BUCKET_NAME).download_file(dirDoc+"/facilities.md", dirDoc+"/facilities.md")

        with open(os.path.join(dirDoc, 'facilities.md'), encoding='utf-8', mode="r") as f:
            content = markdown.markdown(f.read(), extensions=['markdown.extensions.tables'])
        self.render("home/facilities.html", title = self.title, content = content)

class ProjectsHandler(BaseHandler):
    def get(self):
        self.title = "Projects"
        for file in myBucket.objects.filter(Prefix="documents/projects/", Delimiter = '\\'):
            dir = os.path.dirname(file.key)
            if not os.path.exists(dir):
                os.makedirs(dir)
            if file.key[-1]=="/":
                continue
            if not os.path.isfile(file.key):
                s3.Bucket(BUCKET_NAME).download_file(file.key, file.key)   
        projectList = [ x for x in os.listdir(dir+'/') if x not in ignore_list ]    
        projectList.sort(key = lambda x: os.stat(dir+'/'+x).st_ctime)
        self.render("home/projects.html", title = self.title, projectList = projectList)

class ProjectShowHandler(BaseHandler):
    def get(self, project):
        print(project)
        self.title = project
        with open(dirProjects + '/' + project + '.md') as f:
            content = markdown.markdown(f.read())
        self.render("home/page.html", title = self.title, content = content)