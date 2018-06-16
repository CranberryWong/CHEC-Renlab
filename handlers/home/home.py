#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import tornado
import tornado.locale
import markdown
import os

from handlers.base import BaseHandler

class HomeHandler(BaseHandler):
    def get(self):
        BaseHandler.initialize(self)
        self.title = "CHEC"
        self.render("home/home.html", title = self.title)

class MembersHandler(BaseHandler):
    def get(self):
        self.title = "Members"
        MemberURL = os.path.join(os.path.dirname('./..'), "static/members/")
        memberList = {
            "Professor": ["Xiangshi Ren", "Kiyoshi Nakahara", "Kaechang Park"],
            "Associate Professor": ["Yukinobu Hoshino", "Kazunori Ueda", "Toru Kurihara"],
            "Visiting Professor": ["Silpasuwanchai Chaklam", "Kibum Kim"],
            "Assistant Professor": ["Zhenxin Wang", "Sayan Sarcar", "William Delamare", "Keita Mitani"],
            "Ph.D. Student": ["Kavous Salehzadeh Niksirat", "Xinhui Jiang", "Yang Li"],
            "Master Student": ["Chen Wang", "Zengyi Han", "Jingxin Liu", "Ayumu Ono", "Heyu Wang", "Shuang Wang", "Luxi Yang", "Xinyue Hu", "Mengyao Wu"],
            "Bachelor Student": ["Yumiko Kakuta", "Haruna Imada", "Kentarou Yoshida", "Arihiro Iwamoto", "Daichi Harada", "Ryutarou Mizuno", "Kouya Ono", "Kyoichirou Yonezawa", "Mikina Nambu", "Naoki Higashi", "Seira Itou"]
        }
        customLinkDict = {}
        for x in os.listdir(MemberURL):
            if os.path.isfile(MemberURL + x + '/custom.link'):
                with open(MemberURL + x + '/custom.link') as f:
                    customLinkDict[x] = f.read()
        print(customLinkDict)
        self.render("home/members.html", title = self.title, memberList = memberList, MemberURL = MemberURL, customLinkDict = customLinkDict)