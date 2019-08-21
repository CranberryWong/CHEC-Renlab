#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import tornado.web
import tornado.locale
import random
import time
import os
import re
import csv
from handlers.base import BaseHandler
from handlers.aesthetics.settings import WebpageList
from models.user import User
from models.webpage import Webpage
from functools import reduce
from handlers.exception import ErrorHandler

n_cookie = re.compile(r'(\d{1,3})-(.*)')

class MainHandler(BaseHandler):
    def get(self):
        BaseHandler.initialize(self)
        n = list(range(len(WebpageList)))
        random.shuffle(n)
        n = str(reduce(lambda x, y: x+y, list(map(lambda x: str(x) + "-", n))))
        print(n)
        self.set_cookie('n', n)
        self.title = 'Home'
        self.render("experiment/main.html")

class FormHandler(BaseHandler):
    def get(self):
        BaseHandler.initialize(self)
        self.title = "Questionaire"
        self.render("experiment/aesthetics/form.html")
        
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
        uid = newUser.id
        with open(os.path.join(os.path.dirname('./..'), "data/%s.csv") % name, "a+", newline='') as f:
            writer = csv.writer(f)
            writer.writerow(["id", "wid", "timestamp", "title", "appeal"])
        self.set_cookie('uid', uid)
        self.set_secure_cookie('username', name)
        self.redirect('/aesthetic/note?trial=1')
  
class StatementHandler(BaseHandler):
    def get(self):
        BaseHandler.initialize(self)
        self.title = "Statement"
        self.render("experiment/aesthetics/first.html")
        
class NoteHandler(BaseHandler):
    def get(self):
        BaseHandler.initialize(self)
        trial = self.get_argument("trial", default=0)
        self.title = "Note"
        n = self.get_cookie('n')
        g = n_cookie.match(n)
        if trial == '1':
            self.render("experiment/aesthetics/second.html", wid=999)   
        if trial == '0': 
            wid, title = WebpageList[int(g.group(1))].split('*')
            self.render("experiment/aesthetics/second.html", wid=wid)    
        
class WebpageHandler(BaseHandler):
    def get(self, wid):
        BaseHandler.initialize(self)
        self.title = "Start"
        fixation_path = "images/fixation.png"
        noise_path = "images/noise.png"
        if wid == '999':
            webpage_path = "images/webpages/ted.com.png"
            self.render("experiment/aesthetics/webpage.html", fixation_path = fixation_path, webpage_path = webpage_path, noise_path = noise_path, title = 'ted.com', wid = wid)
        wid2, title = WebpageList[int(wid)].split('*')
        webpage_path = "images/webpages/" + title + ".png"
        n = self.get_cookie('n')
        print(n)
        g = n_cookie.match(n)
        print(g.group(2))        
        self.set_cookie('n', g.group(2))
        self.render("experiment/aesthetics/webpage.html", fixation_path = fixation_path, webpage_path = webpage_path, noise_path = noise_path, title = title, wid = wid2)

class RatingHandler(BaseHandler):  
    def post(self):
        BaseHandler.initialize(self)
        self.title = "Rating"
        appealRating = self.get_argument('appeal', default=4)
        #complexityRating = self.get_argument('complexity', default=4)
        wid = self.get_argument('wid', default='')
        print(wid)
        if wid == '999':
            self.redirect('/aesthetic/note?trial=0')
        else:
            title = self.get_argument('title', default='anonymous')
            uid = self.get_cookie('uid')
            name = self.get_secure_cookie('username').decode("utf-8")
            print(uid)    
            newWebpage = Webpage(wid, title, name)
            newWebpage.appeal = int(appealRating)
            #newWebpage.complexity = int(complexityRating)
            newWebpage.write2CSV()
            n = self.get_cookie('n')
            if n == '':
                self.redirect("/aesthetic/finish")
            else:
                try: 
                    g = n_cookie.match(n)
                    wid, title = WebpageList[int(g.group(1))].split('*')
                except Exception as e:
                    print(e)
                    ErrorHandler.write_error(500)
            self.redirect("/aesthetic/start/"+ str(wid))

class FinishHandler(BaseHandler):
    def get(self):
        BaseHandler.initialize(self)
        self.title = "Thank you so much ~"
        Name = self.get_secure_cookie('username')
        self.clear_cookie('username')
        self.clear_cookie('uid')
        self.clear_cookie('n')
        self.render("main/finish.html", slogan = Name)