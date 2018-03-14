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

class FormHandler(tornado.web.RequestHandler):
    def get(self):
        self.title = "Questionaire"
        self.render("experiment/form.html")
        
    def post(self):
        self.title = "Questionaire"
    
        ever = self.get_argument('ever', default='')   
        name = self.get_argument('name', default='')
        gender = self.get_argument('gender', default='')
        age = self.get_argument('age', default='')
        country = self.get_argument('country', default='')
        edu = self.get_argument('edu', default='')
        design = self.get_argument('design', default='')
        
        newUser = User(ever, name, gender, age, country, edu, design)
        newUser.write2CSV()
        self.set_secure_cookie('name', name)
        self.redirect('/aesthetic/note')
  
class StatementHandler(tornado.web.RequestHandler):
    def get(self):
        self.title = "Statement"
        self.render("experiment/first.html")
        
class NoteHandler(tornado.web.RequestHandler):
    def get(self):
        self.title = "Note"
        self.render("experiment/second.html")    
        
class WebpageHandler(tornado.web.RequestHandler):
    def get(self, wid):
        self.title = "Start"
        fixation_path = "images/fixation.png"
        noise_path = "images/noise.png"
        self.render("experiment/webpage.html", path = fixation_path, webpage_path = "images/webpages/_apple.com.png", anotherpath = noise_path)

class RatingHandler(tornado.web.RequestHandler):  
    def post(self):
        self.title = "Rating"
        n = 1
        appealRating = self.get_argument('appeal', default=4)
        complexityRating = self.get_argument('complexity', default=4)
        wid, title = WebpageList[n].split('-')
        newWebpage = Webpage(title)
        newWebpage.appeal.append(appealRating)
        newWebpage.complexity.append(complexityRating)
        n += 1
        self.redirect("/aesthetic/start/"+ wid)
                
class EditPost(tornado.web.RequestHandler):
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

