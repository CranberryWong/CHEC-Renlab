#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import tornado
import tornado.locale
import markdown
import os
import boto3 
import botocore

from handlers.base import BaseHandler
from boto3 import Session

# AWS S3 Configuration
BUCKET_NAME = 'chec-static'
session = Session()
credentials = session.get_credentials()
current_credentials = credentials.get_frozen_credentials()
s3 = boto3.resource('s3')
s3c = boto3.client('s3',aws_access_key_id=current_credentials.access_key,aws_secret_access_key=current_credentials.secret_key,aws_session_token=current_credentials.token)

class HomeHandler(BaseHandler):
    def get(self):
        BaseHandler.initialize(self)
        self.title = "CHEC"
        self.render("home/home.html", title = self.title)

class MembersHandler(BaseHandler):
    def get(self):
        self.title = "Members"

        # AWS S3 access bucket
        myBucket = s3.Bucket(BUCKET_NAME)
        config = s3c._client_config
        config.signature_version = botocore.UNSIGNED
        allAvatarURL={}

        # OLD CODE
        # MemberURL = os.path.join(os.path.dirname('./..'), "static/members/")

        memberList = {
            "Professor": ["Xiangshi Ren", "Kiyoshi Nakahara", "Kaechang Park"],
            "Associate Professor": ["Yukinobu Hoshino", "Kazunori Ueda", "Toru Kurihara"],
            "Visiting Professor": ["Silpasuwanchai Chaklam", "Kibum Kim"],
            "Assistant Professor": ["Zhenxin Wang", "Sayan Sarcar", "William Delamare", "Keita Mitani"],
            "Secretary": ["Kyoko Hatakenaka"],
            "Ph.D. Student": ["Kavous Salehzadeh Niksirat", "Xinhui Jiang", "Yang Li", "Chen Wang"],
            "Master Student": ["Zengyi Han", "Jingxin Liu", "Ayumu Ono", "Heyu Wang", "Shuang Wang", "Luxi Yang", "Xinyue Hu", "Mengyao Wu", "Fitra Rahmamuliani"],
            "Bachelor Student": ["Yumiko Kakuta", "Haruna Imada", "Kentarou Yoshida", "Arihiro Iwamoto", "Daichi Harada", "Ryutarou Mizuno", "Kouya Ono", "Kyoichirou Yonezawa", "Mikina Nambu", "Naoki Higashi", "Seira Itou", "Yugandhara Suren Hiray", "Junlin Sun", "Anran Wu"]
        }
        customLinkDict = {}
        for file in myBucket.objects.all():
            params = {'Bucket': BUCKET_NAME, 'Key': file.key}
            url = s3c.generate_presigned_url('get_object', params)
            # get avatar public url
            allAvatarURL[file.key] = url
            file_key = file.key
            # get custom link content
            if 'custom.link' in file_key:
                dir = os.path.dirname(file_key)
                # create directory if it does not exist
                if not os.path.exists(dir):
                    os.makedirs(dir)
                s3.Bucket(BUCKET_NAME).download_file(file_key, file_key)
                with open(file_key) as f:
                    customLinkDict[file_key.split('/')[1]] = f.read()

        # OLD CODE
        # for x in os.listdir(MemberURL):
        #     if os.path.isfile(MemberURL + x + '/custom.link'):
        #         with open(MemberURL + x + '/custom.link') as f:
        #             customLinkDict[x] = f.read()
        # print(customLinkDict)
        # self.render("home/members.html", title = self.title, memberList = memberList, MemberURL = MemberURL, customLinkDict = customLinkDict)

        self.render("home/members.html", title = self.title, memberList = memberList, allAvatarURL=allAvatarURL, customLinkDict = customLinkDict)