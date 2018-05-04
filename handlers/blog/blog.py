#! /usr/local/bin python3

import tornado
import tornado.locale
import markdown
import os
import uuid

from handlers.util import *
from handlers.base import BaseHandler

BlogURL = os.path.join(os.path.dirname('./..'), "static/members/")

class BlogHandler(BaseHandler):
    def get(self):
        self.title = "Blog"
        userName = tornado.escape.xhtml_escape(self.current_user)
        avatarURL = 'members/' + userName + '/avatar.png'
        blogList = [ (x, os.stat(BlogURL + userName + '/' + x)) for x in os.listdir(BlogURL + userName) if x not in ignore_list ]
        #blogList = list(set(list(lambda x: x[0] ,blogList)).difference(set(ignore_list)))
        self.render("blog/blog.html", title = self.title, avatarURL = avatarURL, userName = userName, blogList = blogList)

class BlogWritingHandler(BaseHandler):
    def post(self):
        self.title = "Writing"
        userName = tornado.escape.xhtml_escape(self.current_user)
        title = self.get_argument('title', default="Weekly Progress")
        content = self.get_argument('content', default="")
        print(title)
        print(content)
        with open(BlogURL + userName + '/' + title+'.md', "w") as f:
            f.write(content)
        print("ok")
        self.redirect("/blog")

class ProfileHandler(BaseHandler):
    def get(self):
        self.title = "Profile"
        userName = tornado.escape.xhtml_escape(self.current_user)
        avatarURL = 'members/' + userName + '/avatar.png'
        profileURL = BlogURL + userName + '/profile.md'
        with open(profileURL) as f:
            content = markdown.markdown(f.read())
        self.render("blog/profile.html", title = self.title, avatarURL = avatarURL, userName = userName, content = content)

class BlogContentHandler(BaseHandler):
    def get(self):
        title = self.get_argument('title', default="")[1:]
        userName = tornado.escape.xhtml_escape(self.current_user)
        for i in os.listdir(BlogURL + userName):
            if str(uuid.uuid3(uuid.NAMESPACE_DNS, i)) == title:
                title = i
        with open(BlogURL + userName + '/' + title + '.md') as f:
            content = markdown.markdown(f.read())
        self.write(content)

class ResourceHandler(BaseHandler):
    @tornado.web.authenticated
    def get(self):
        title = 'Resource'
        userName = tornado.escape.xhtml_escape(self.current_user)
        self.render("blog/resource.html", title = self.title)