#! /usr/local/bin python3

import tornado.web
import tornado.locale
import random
import time
import os
# import pandas as pd
import csv
from handlers.base import BaseHandler
from handlers.util import WebpageLists
from models.user import User
from models.webpage import Webpage

WebpageList = WebpageLists
random.shuffle(WebpageList)

class MainHandler(BaseHandler):
    def get(self):
        BaseHandler.initialize(self)
        self.title = 'Home'
        user = 'Wang Chen'
        self.render("main/main.html", user = user)

class FormHandler(BaseHandler):
    def get(self):
        BaseHandler.initialize(self)
        self.title = "Questionaire"
        self.render("experiment/form.html")
        
    def post(self):
        BaseHandler.initialize(self)
        self.title = "Questionaire"
        ever = self.get_argument('ever', default='')  
        email = self.get_argument('email', default='') 
        name = self.get_argument('name', default='')
        gender = self.get_argument('gender', default='')
        age = self.get_argument('age', default='')
        country = self.get_argument('country', default='')
        edu = self.get_argument('edu', default='')
        design = self.get_argument('design', default='')
        
        newUser = User(ever, email, name, gender, age, country, edu, design)
        newUser.write2CSV()
        BaseHandler.uid = newUser.id
        BaseHandler.login_user = name
        global Name
        self.login_user = name
        Name = name
        print(self.login_user)
        print("/")
        self.set_secure_cookie('username', name)
        self.redirect('/aesthetic/note')
  
class StatementHandler(BaseHandler):
    def get(self):
        BaseHandler.initialize(self)
        self.title = "Statement"
        self.render("experiment/first.html")
        
class NoteHandler(BaseHandler):
    def get(self):
        BaseHandler.initialize(self)
        self.title = "Note"
        global WebpageList
        wid, title = WebpageList[0].split('*')
        self.render("experiment/second.html", wid=int(wid))    
        
class WebpageHandler(BaseHandler):
    def get(self, wid):
        BaseHandler.initialize(self)
        self.title = "Start"
        global WebpageList
        fixation_path = "images/fixation.png"
        noise_path = "images/noise.png"
        for i in WebpageList:
            wid2, title = WebpageList[0].split('*')
            if wid == wid2:
                webpage_path = "images/webpages/" + title + ".png"
                WebpageList.remove(i)
        self.render("experiment/webpage.html", fixation_path = fixation_path, webpage_path = webpage_path, noise_path = noise_path, title = title, wid = wid)

class RatingHandler(BaseHandler):  
    def post(self):
        BaseHandler.initialize(self)
        self.title = "Rating"
        global WebpageList
        appealRating = self.get_argument('appeal', default=4)
        complexityRating = self.get_argument('complexity', default=4)
        wid = self.get_argument('wid', default='')
        print(wid)
        title = self.get_argument('title', default='anonymous')
        
        uid = BaseHandler.uid
        print(uid)    
        newWebpage = Webpage(wid, title, uid)
        newWebpage.appeal = int(appealRating)
        newWebpage.complexity = int(complexityRating)
        newWebpage.write2CSV()
        if WebpageList == []:
            self.redirect("/finish")
        else:
            try: 
                wid, title = WebpageList[0].split('*')
            except Exception as e:
                print(e)
        self.redirect("/aesthetic/start/"+ str(wid))

class FinishHandler(BaseHandler):
    def get(self):
        BaseHandler.initialize(self)
        self.title = "Thank you so much ~"
        global Name
        global csvName
        # slogan = self.login_user
        print(self.login_user)    
        print("/")
        self.clear_cookie('username')
        global WebpageList
        WebpageList = WebpageLists 
        self.render("main/finish.html", slogan = Name)