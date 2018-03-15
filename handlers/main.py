#! /usr/local/bin python3

import tornado.web
import tornado.locale
import random
import time
import os
from handlers.base import BaseHandler
from handlers.util import WebpageList
from models.user import User
from models.webpage import Webpage


class MainHandler(BaseHandler):
    def get(self):
        BaseHandler.initialize(self)
        self.title = 'Home'
        user = 'Wang Chen'
        self.render("main/main.html", user = user)

class FormHandler(BaseHandler):
    def get(self):
        self.title = "Questionaire"
        self.render("experiment/form.html")
        
    def post(self):
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
        self.set_secure_cookie('username', name)
        self.redirect('/aesthetic/note')
  
class StatementHandler(BaseHandler):
    def get(self):
        self.title = "Statement"
        self.render("experiment/first.html")
        
class NoteHandler(BaseHandler):
    def get(self):
        self.title = "Note"
        self.render("experiment/second.html")    
        
class WebpageHandler(BaseHandler):
    def get(self, wid):
        self.title = "Start"
        fixation_path = "images/fixation.png"
        noise_path = "images/noise.png"
        self.render("experiment/webpage.html", path = fixation_path, webpage_path = "images/webpages/_apple.com.png", anotherpath = noise_path)

class RatingHandler(BaseHandler):  
    def post(self):
        self.title = "Rating"
        n = 0
        appealRating = self.get_argument('appeal', default=4)
        complexityRating = self.get_argument('complexity', default=4)
        wid, title = WebpageList[n].split('-')
        newWebpage = Webpage(title)
        newWebpage.appeal.append(int(appealRating))
        newWebpage.complexity.append(int(complexityRating))
        newWebpage.write2CSV()
        n += 1
        wid = 1
        self.redirect("/aesthetic/start/"+ str(wid))

class FinishHandler(BaseHandler):
    def get(self):
        self.title = "Thank you so much ~"
        print(self.get_secure_cookie('name'))
        slogan = self.get_secure_cookie(self)
        self.clear_cookie('username')  
        self.render("main/finish.html", slogan = slogan)

'''                
class EditPost(BaseHandler):
    def get(self):
        users = self.application.db['user']
        user = users.find_one()
        if user:
            del user["_id"]
            self.set_status(200)
            self.write(user)            
        else:
            self.set_status(404)
            self.write({"error": "word not found"})            

'''