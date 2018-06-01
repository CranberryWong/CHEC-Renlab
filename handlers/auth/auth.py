#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import tornado
import tornado.locale
import hashlib
import os

from handlers.base import BaseHandler

AuthURL = os.path.join(os.path.dirname('./..'), "static/members/")

#Sign In
class SignInHandler(BaseHandler):
    def get(self):
        self.title = "Sign In"
        self.render("auth/signin.html")

    def post(self):
        username = self.get_argument("username", default="")
        password = self.get_argument("password", default="")
        #Query
        md5_password = hashlib.md5(password.encode("utf-8")).hexdigest()
        memberList = [ x for x in os.listdir(AuthURL)]
        if username in memberList:
            with open(AuthURL + username + '/password.salt') as f:
                pwd = f.read()
            if md5_password == pwd:
                self.message = ""
                self.set_secure_cookie('user', username)
                self.redirect('/')
            else:
                self.message = "Wrong Password!"
                self.redirect('/signin')
        else:
            self.message = "Username hasn't been signed up!"
            self.redirect('/signin')

#Sign Out
class SignOutHandler(BaseHandler):
    def get(self):
      self.clear_cookie('user')
      self.redirect('/')