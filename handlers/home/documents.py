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
ProjectURL = os.path.join(DocURL, "projects")

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

class CurriculumHandler(BaseHandler):
    def get(self):
        self.title = 'HCI Curriculum'
        year = ['2014']
        curriculumList = []
        for y in year:
            with open(os.path.join(CurriculumURL, y + '.md'), "r") as f:
                curriculumList.append(markdown.markdown(f.read(), extensions=['markdown.extensions.tables']))
        self.render("home/curriculum.html", title = self.title, curriculumList = curriculumList)

class FacilitesHandler(BaseHandler):
    def get(self):
        self.title = "Facilities"
        with open(os.path.join(DocURL, 'facilities.md'), "r") as f:
            content = markdown.markdown(f.read(), extensions=['markdown.extensions.tables'])
        self.render("home/facilities.html", title = self.title, content = content)

class ProjectsHandler(BaseHandler):
    def get(self):
        self.title = "Projects"
        projectList = [ x for x in os.listdir(ProjectURL) if x not in ignore_list ]
        self.render("home/projects.html", title = self.title, projectList = projectList)

class ProjectShowHandler(BaseHandler):
    def get(self, project):
        print(project)
        self.title = project
        with open(ProjectURL + '/' + project + '.md') as f:
            content = markdown.markdown(f.read())
        self.render("home/page.html", title = self.title, content = content)