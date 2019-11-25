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
            "Visiting Researcher": ["Kavous Salehzadeh Niksirat", "Silpasuwanchai Chaklam", "Kibum Kim"],
            "Assistant Professor": ["Zhenxin Wang", "Sayan Sarcar", "William Delamare", "Keita Mitani"],
            "Secretary": ["Kyoko Hatakenaka"],
            "Ph.D. Student": ["Xinhui Jiang", "Yang Li", "Chen Wang"],
            "Master Student": ["Jingxin Liu", "Ayumu Ono", "Fitra Rahmamuliani", "Xiaoxuan Li", "Yilin Zheng", "Chunyuan Lan", "Xinpeng Li", "Xi Chen", "Sai Jiang", "Hongyun Lyu", "Jian Zhang", "Zhihang Guo"],
            "Bachelor Student": ["Kouya Ono", "Kyoichirou Yonezawa", "Mikina Nambu", "Naoki Higashi", "Seira Itou", "Akinori Kondo", "Hijiri Kaneko", "Ryota Torii", "Takaaki Kubo", "Yusuke Tokito", "Jiayuan Geng"]
        }
        alumniList = {
            "Nem Khan Dim": "",
            "Huawei Tu": "",
            "Minghui Sun": "",
            "Feng Wang": "",
            "Yizhong Xin": "",
            "Chuanyi Liu": "",
            "Xiaolei Zhou ": "",
            "Xinyong Zhang": "",
            "Jibin Yin": "",
            "Jing Kong": "",
            "Mahmoud Mohamed Hussein Ahmed": "",
            "Handityo Aulia Putra": "Assistant Professor at Keimyung University, Daegu, Korea",
            "Qinglong Wang": "Ph.D student at Jilin University",
            "Naoteru Jinjo":"",
            "Kousuke Kume": "",
            "Ryo Mizobata": "",
            "Masashi Okamoto": "",
            "Taiga Machida": "",
            "Ohara Yoshitaka": "",
            "Masatoshi Kusuba": "",
            "Yusuke Hayashi": "",
            "Tomoki Ooya": "",
            "Fumiya Fukutoku": "",
            "Tomoaki Tsuchida": "",
            "Taishi Kato": "",
            "Masafumi Ogasawara": "",
            "Kinya Tamura": "",
            "Ryusuke Ueta": "",
            "Fang Qi" : "",
            "Masaki Obata" : "",
            "Toshiaki Shiraki": "",
            "Jiaxin Yu ": "",
            "Jiabing Wang ": "",
            "Ping Ju ": "",
            "Kuo Pang ": "",
            "Yingda Lu ": "",
            "Yang Gao ": "",
            "Yuan Fu ": "",
            "Xin Li ": "",
            "Dongxing Bao ": "",
            "Xue Wang ": "",
            "Jing Fan": "Requirements-analyst at ChinaUnicom Software Institute in Beijing, China",
            "Dongcai Wen ": "",
            "Guanghui Chen": "Game programmer at HUANBAO Net Tech Co.,Ltd, China",
            "Zijing Yang": "Software Engineer at ChinaUnicom Beijing, China",
            "Song Donglei" : "Ph.D student at Jilin University, Changchun, China",
            "Zhong Qiuheqi": "",
            "Tao Yu": "",
            "Chunyuan Lan": "",
            "Li Zhuang": "",
            "Sun Chongliang": "",
            "Wang Yiqun": "",
            "Wang Xueying": "",
            "Wang Xiaoxu": "",
            "Xu Qihong": "",
            "Zhang Chi": "",
            "Dong Lei": "",
            "Moriyama": "",
            "Tanigawa": "",
            "Ming Wei": "",
            "Junlin Sun" : "",
            "Zengyi Han": "",
            "Yumiko Kakuta":"", 
            "Haruna Imada":"", 
            "Kentarou Yoshida":"", 
            "Arihiro Iwamoto":"", 
            "Daichi Harada":"", 
            "Ryutarou Mizuno":"",
            "Yugandhara Suren Hiray":"", 
            "Anran Wu":""
             
        }
        allAvatarURL["members/Handityo Aulia Putra/avatar.png"] = "https://media.licdn.com/dms/image/C5103AQEYVvXfbkE6Mw/profile-displayphoto-shrink_800_800/0?e=1545868800&v=beta&t=nP2BNCn54128cMsdb7p0W3KP4V7Po8f50k6-6w8qpCw"
        allAvatarURL["members/Mahmoud Mohamed Hussein Ahmed/avatar.png"]= "https://i1.rgstatic.net/ii/profile.image/283545642782721-1444613957285_Q128/Mahmoud_Hussien7.jpg"
        customLinkDict = {}
        MemberURL=""
        for file in myBucket.objects.filter(Prefix="members/", Delimiter = '\\'):
            params = {'Bucket': BUCKET_NAME, 'Key': file.key}
            url = s3c.generate_presigned_url('get_object', params)
            # get avatar public url
            allAvatarURL[file.key] = url
            file_key = file.key
            # print(allAvatarURL[file.key])
            if 'member' in file_key.split('/')[0]:
                MemberURL=file_key.split('/')[0]
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

        self.render("home/members.html", title = self.title, memberList = memberList, alumniList = alumniList, MemberURL = MemberURL, allAvatarURL=allAvatarURL, customLinkDict = customLinkDict)