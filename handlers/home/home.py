#! /usr/local/bin python3

import tornado
import tornado.locale
import markdown
import os

from handlers.base import BaseHandler

class HomeHandler(BaseHandler):
    def get(self):
        self.title = "CHEC"
        self.render("home/home.html", title = self.title)

class MembersHandler(BaseHandler):
    def get(self):
        self.title = "Members"
        md_path = os.path.join(os.path.dirname(__file__), "../../static/md/test.md")
        '''
        with open(md_path, "r") as f:
            mylist = [line.rstrip('\n') for line in f]
            print(mylist)
            content = markdown.markdown(mylist)
        '''
        self.render("home/members.html", title = self.title)