#! /usr/local/bin python3

import tornado
import tornado.locale
import markdown
import os

from handlers.base import BaseHandler
from handlers.util import *
from handlers.blog.blog import BlogURL

DocURL = os.path.join(os.path.dirname('./..'), "static/documents")
CurriculumURL = os.path.join(DocURL, "HCIcurriculum")

class PubHandler(BaseHandler):
    def get(self):
        self.title = "Publication"
        with open(os.path.join(DocURL, 'publication.md'), "r") as f:
            content = markdown.markdown(f.read())
        self.render("home/publication.html", title = self.title, content = content)

class ResourceHandler(BaseHandler):
    @tornado.web.authenticated
    def get(self):
        self.title = 'Resource'
        userName = tornado.escape.xhtml_escape(self.current_user)
        memberList = [ x for x in os.listdir(BlogURL) if x not in ignore_list]
        with open(os.path.join(DocURL, 'resource.md'), "r") as f:
            content = markdown.markdown(f.read())            
        self.render("home/resource.html", title = self.title, memberList = memberList, content = content)


# Program your code here
class CurriculumHandler(BaseHandler):
    def get(self):
        pass


'''
class CurriculumHandler(BaseHandler):
    def get(self):
        self.title = 'HCI Curriculum'
        year = ['2018', '2017', '2016']
        curriculumList = []
        for y in year:
            with open(os.path.join(CurriculumURL, y + '.md'), "r") as f:
                curriculumList.append(markdown.markdown(f.read(), extensions=['markdown.extensions.tables']))
        self.render("home/curriculum.html", title = self.title, curriculumList = curriculumList)
'''