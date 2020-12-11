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
from handlers.aesthetics import settingslay
from models.user import User
from models.webpagelay import Webpage
from functools import reduce
from handlers.exception import ErrorHandler

n_cookie = re.compile(r'(\d{1,3})-(.*)')


class FormHandler(BaseHandler):
    def get(self):
        BaseHandler.initialize(self)
        self.title = "Questionaire"
        self.render("experiment/layout/form.html")
        
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
        ext = self.get_cookie('ext')
        with open(os.path.join(os.path.dirname('./..'), "data/"+str(ext)+"/%s.csv") % name, "a+", newline='') as f:
            writer = csv.writer(f)
            writer.writerow(["id", "wid", "timestamp", "title", "appeal"])
        self.set_cookie('uid', uid)
        self.set_secure_cookie('username', name)
        self.redirect('/layout/note?trial=1')
  
class StatementHandler(BaseHandler):
    def get(self):
        BaseHandler.initialize(self)
        ext = self.get_argument("ext")
        m = list(range(len(settingslay.WebpageList)))
        random.shuffle(m)
        m = str(reduce(lambda x, y: x+y, list(map(lambda x: str(x) + "-", m))))
        print(m)
        self.set_cookie('m', m)
        self.set_cookie('ext', ext)
        self.title = "Statement"
        self.render("experiment/layout/first.html")
        
class NoteHandler(BaseHandler):
    def get(self):
        BaseHandler.initialize(self)
        trial = self.get_argument("trial", default=0)
        self.title = "Note"
        m = self.get_cookie('m')
        g = n_cookie.match(m)
        if trial == '1':
            self.render("experiment/layout/second.html", wid=999)   
        if trial == '0': 
            wid, title = settingslay.WebpageList[int(g.group(1))].split('*')
            self.render("experiment/layout/second.html", wid=wid)    
        
class WebpageHandler(BaseHandler):
    def get(self, wid):
        BaseHandler.initialize(self)
        self.title = "Start"
        fixation_path = "images/fixation.png"
        noise_path = "images/noise.png"
        ext = self.get_cookie('ext')
        if wid == '999':
            webpage_path = "images/webpages/ted.com.png"
            self.render("experiment/layout/webpage.html", fixation_path = fixation_path, webpage_path = webpage_path, noise_path = noise_path, title = 'ted.com', wid = wid, ext=ext)
        wid2, title = settingslay.WebpageList[int(wid)].split('*')
        webpage_path = "images/webpages/" + title + ".png"
        m = self.get_cookie('m')
        print(m)
        g = n_cookie.match(m)
        print(g.group(2))        
        self.set_cookie('m', g.group(2))
        self.render("experiment/layout/webpage.html", fixation_path = fixation_path, webpage_path = webpage_path, noise_path = noise_path, title = title, wid = wid2, ext=ext)

class RatingHandler(BaseHandler):  
    def post(self):
        BaseHandler.initialize(self)
        self.title = "Rating"
        ext = self.get_cookie('ext')
        appealRating = self.get_argument('appeal', default=4)
        #complexityRating = self.get_argument('complexity', default=4)
        wid = self.get_argument('wid', default='')
        print(wid)
        if wid == '999':
            self.redirect('/layout/note?trial=0')
        else:
            title = self.get_argument('title', default='anonymous')
            uid = self.get_cookie('uid')
            name = self.get_secure_cookie('username').decode("utf-8")
            print(uid)    
            newWebpage = Webpage(wid, ext, title, name)
            newWebpage.appeal = int(appealRating)
            #newWebpage.complexity = int(complexityRating)
            newWebpage.write2CSV()
            m = self.get_cookie('m')
            if m == '':
                self.redirect("/layout/finish")
            else:
                try: 
                    g = n_cookie.match(m)
                    wid, title = settingslay.WebpageList[int(g.group(1))].split('*')
                except Exception as e:
                    print(e)
                    ErrorHandler.write_error(500)
            self.redirect("/layout/start/"+ str(wid))

class FinishHandler(BaseHandler):
    def get(self):
        BaseHandler.initialize(self)
        self.title = "Thank you so much ~"
        Name = self.get_secure_cookie('username')
        self.clear_cookie('username')
        self.clear_cookie('uid')
        self.clear_cookie('ext')
        self.clear_cookie('m')
        self.clear_cookie('n')
        self.render("main/finish.html", slogan = Name)