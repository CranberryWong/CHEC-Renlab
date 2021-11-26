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
from datetime import datetime

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
pastCurriculumURL = os.path.join(DocURL, "HCIcurriculum")
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

        memberIgnoreList = ["Yukinobu Hoshino", "Kaechang Park", "Hamed Aliyari","Kibum Kim", "Sayan Sarcar", "Huawei Tu","Zhenxin Wang", "Yugandhara Suren Hiray", "Anran Wu", "Yumiko Kakuta", "Haruna Imada", "Kentarou Yoshida", "Arihiro Iwamoto", "Daichi Harada", "Ryutarou Mizuno", "Zengyi Han","Jingxin Liu", "Ayumu Ono","Heyu Wang","Shuang Wang","Luxi Yang", "Xinyue Hu", "Mengyao Wu","Kouya Ono", "Kyoichirou Yonezawa", "Mikina Nambu", "Naoki Higashi", "Seira Itou","Ryota Torii","Yanyin Zhou"]
        memberList2 = {
            "Professor": ["Xiangshi Ren",  "Kaechang Park"],
            "Associate Professor": ["Yukinobu Hoshino"],
            "Visiting Researcher": ["Kavous Salehzadeh Niksirat", "Huawei Tu", "Kibum Kim", "Sayan Sarcar", "William Delamare"],
            "Assistant Professor": ["Zhenxin Wang"],
            "Ph.D. Student": ["Xinhui Jiang", "Yang Li", "Chen Wang"],
            "Master Student": ["Yilin Zheng","Xinpeng Li","Xi Chen","Sai Jiang","Hongyun Lyu","Jian Zhang","Zhihang Guo","Xiaofei Zhu","Junlin Sun"],
            "Bachelor Student": [ "Akinori Kondo", "Hijiri Kaneko", "Takaaki Kubo", "Yusuke Tokito", "Saki Hiramatsu", "Adachi Kenshi", "Miyamoto Daisuke"]
        }
        memberList = [ (x, os.stat(BlogURL + '/' + x)) for x in os.listdir(BlogURL) if x not in ignore_list and x not in memberIgnoreList]
        memberList.sort(key = lambda x: x[1].st_ctime, reverse = True)

        blogList = {}
        blogContent = {}
        blogTitle = {}
        for member in memberList:
            blogList[member[0]] = os.path.basename(max([os.path.join(BlogURL+ member[0], basename) for basename in os.listdir(BlogURL + member[0])], key=os.path.getctime))
            if ".md" in blogList[member[0]]:
                with open(BlogURL + member[0] + '/' + blogList[member[0]], encoding='utf-8', mode="r") as f:
                    blogContent[member[0]] = markdown.markdown(f.read())
            else:
                blogList[member[0]] = " "
                blogContent[member[0]] = " "

        allAvatarURL={}
        for file in myBucket.objects.filter(Prefix="members/", Delimiter = '\\'):
            params = {'Bucket': BUCKET_NAME, 'Key': file.key}
            url = s3c.generate_presigned_url('get_object', params)
            # get avatar public url
            allAvatarURL[file.key] = url
        s3_resource = s3c.get_object(Bucket=BUCKET_NAME, Key=dirDoc+'/resource.md')
        content = markdown.markdown(s3_resource['Body'].read().decode('utf-8-sig'))

        s3_response_object = s3c.get_object(Bucket=BUCKET_NAME, Key=dirDoc+'/agenda.md')
        agenda = markdown.markdown(s3_response_object['Body'].read().decode('utf-8-sig'))

        self.render("home/resource.html", title = self.title, memberList = memberList, allAvatarURL = allAvatarURL, content = content, agenda = agenda, blogList = blogList, blogContent = blogContent, memberList2 = memberList2)

class CurriculumHandler(BaseHandler):
    def get(self):
        self.title = 'HCI Curriculum'
        year = ['2021u']
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
            s3_response_object = s3c.get_object(Bucket=BUCKET_NAME, Key='documents/HCIcurriculum/'+y+'.md')
            curriculumList.append(markdown.markdown(s3_response_object['Body'].read().decode('utf-8-sig'), extensions=['markdown.extensions.tables']))
            # with open(os.path.join(dir, y + '.md'), encoding='utf-8', mode="r") as f:
            #     curriculumList.append(markdown.markdown(f.read(), extensions=['markdown.extensions.tables']))
        self.render("home/curriculum.html", title = self.title, curriculumList = curriculumList)


class pastcurriculumHandler(BaseHandler):
  def get(self):
    self.title = 'HCI Curriculum'
    year = ['2018','2017', '2016', '2014']
    curriculumList = []
    for file in myBucket.objects.filter(Prefix="documents/HCIcurriculum/", Delimiter='\\'):
      dir = os.path.dirname(file.key)
      if not os.path.exists(dir):
        os.makedirs(dir)
      if file.key[-1] == "/":
        continue
      if not os.path.isfile(file.key):
        s3.Bucket(BUCKET_NAME).download_file(file.key, file.key)
    for y in year:
      s3_response_object = s3c.get_object(Bucket=BUCKET_NAME, Key='documents/HCIcurriculum/' + y + '.md')
      curriculumList.append(markdown.markdown(s3_response_object['Body'].read().decode('utf-8-sig'),
                                              extensions=['markdown.extensions.tables']))
      # with open(os.path.join(dir, y + '.md'), encoding='utf-8', mode="r") as f:
      #     curriculumList.append(markdown.markdown(f.read(), extensions=['markdown.extensions.tables']))
    self.render("home/curriculum.html", title=self.title, curriculumList=curriculumList)

class IntroHandler(BaseHandler):
    def get(self):
        self.title = "Introduction for CHEC"

        if not os.path.exists(dirDoc):
            os.makedirs(dirDoc)

        if self.get_cookie('lang') == 'ja_JP':
            filename = "chec_jp.md"
        else:
            filename = "chec.md"

        s3.Bucket(BUCKET_NAME).download_file(dirDoc+"/"+filename, dirDoc+"/"+filename)

        with open(os.path.join(dirDoc, filename), encoding='utf-8', mode="r") as f:
            content = markdown.markdown(f.read(), extensions=['markdown.extensions.tables'])
        self.render("home/page.html", title = self.title, content = content)

class FacilitesHandler(BaseHandler):
    def get(self):
        self.title = "Facilities"
        filename = ''

        if not os.path.exists(dirDoc):
            os.makedirs(dirDoc)

        if self.get_cookie('lang') == 'ja_JP':
            filename = "facilities_jp.md"
        else:
            filename = "facilities.md"

        s3.Bucket(BUCKET_NAME).download_file(dirDoc+"/"+filename, dirDoc+"/"+filename)

        with open(os.path.join(dirDoc, filename), encoding='utf-8', mode="r") as f:
            content = markdown.markdown(f.read(), extensions=['markdown.extensions.tables'])
        self.render("home/facilities.html", title = self.title, content = content)

class ProjectsHandler(BaseHandler):
    def get(self):
        self.title = "Projects"
        foldername = ""

        if self.get_cookie('lang') == 'ja_JP':
            foldername = "projects_jp"
        else:
            foldername = "projects"
        for file in myBucket.objects.filter(Prefix="documents/"+foldername+"/", Delimiter = '\\'):
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
        # with open(dirProjects + '/' + project + '.md') as f:
        #     content = markdown.markdown(f.read())
        # open the markdown directly from s3
        if self.get_cookie('lang') == 'ja_JP':
            foldername = "projects_jp"
        else:
            foldername = "projects"

        s3_response_object = s3c.get_object(Bucket=BUCKET_NAME, Key='documents/'+foldername+'/'+project+'.md')
        content = markdown.markdown(s3_response_object['Body'].read().decode('utf-8-sig'))

        self.render("home/page.html", title = self.title, content = content)
