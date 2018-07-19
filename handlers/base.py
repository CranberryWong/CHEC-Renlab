#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import tornado.web
import tornado.locale
import random
from models.user import User
# from mongoengine import *

class BaseHandler(tornado.web.RequestHandler):
    
    def initialize(self, title="Untitled"):
        self.title = title
        self.message = None
        if not self.get_cookie('lang'):
            self.set_cookie('lang', 'en_US')
            self.lang = self.get_cookie('lang')
        else:
            self.lang = self.get_cookie('lang')
        tornado.locale.set_default_locale("en_US")

    def get_user_locale(self):
        return tornado.locale.get(self.get_cookie('lang'))

    def get_current_user(self):
        return self.get_secure_cookie('user')  

    def get_current_id(self):
        return self.get_cookie('uid')  
        
class I18nHandler(BaseHandler):
    def get(self):
        language = self.get_argument("lang")
        if language == 'zh_CN':
            self.set_cookie('lang', 'zh_CN')
        elif language == 'ja_JP':
            self.set_cookie('lang', 'ja_JP')
        elif language == 'en_US':
            self.set_cookie('lang', 'en_US')
        else:
            self.set_cookie('lang', 'en_US')
        tornado.locale.get(self.get_cookie('lang'))
        self.redirect('/')

    