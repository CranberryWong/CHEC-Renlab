#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import tornado
import tornado.locale
import markdown
import os
import uuid
import hashlib
import time

from handlers.util import *
from handlers.base import BaseHandler

BlogURL = os.path.join(os.path.dirname('./..'), "static/members/")

class BlogHandler(BaseHandler):
    def get(self, userName):
        self.title = "Blog"
        avatarURL = 'members/' + userName + '/avatar.png'
        blogList = [ (x, os.stat(BlogURL + userName + '/' + x)) for x in os.listdir(BlogURL + userName) if x not in ignore_list ]
        blogList = [(x[0], time.ctime(x[1].st_ctime)) for x in sorted(blogList, key = lambda x: x[1].st_ctime,reverse=True)]
        #blogList = list(set(list(lambda x: x[0] ,blogList)).difference(set(ignore_list)))
        self.render("blog/blog.html", title = self.title, avatarURL = avatarURL, userName = userName, blogList = blogList)

class BlogWritingHandler(BaseHandler):
    @tornado.web.authenticated
    def post(self):
        self.title = "Writing"
        userName = tornado.escape.xhtml_escape(self.current_user)
        title = self.get_argument('title', default="Weekly Progress")
        content = self.get_argument('content', default="")
        with open(BlogURL + userName + '/' + title+'.md', "w") as f:
            f.write(content)
        print("ok")
        self.redirect("/blog/" + userName)

class BlogContentHandler(BaseHandler):
    @tornado.web.authenticated
    def get(self):
        title = self.get_argument('title', default="")[1:]
        userName = self.get_argument('name', default="")
        for i in os.listdir(BlogURL + userName):
            if str(uuid.uuid3(uuid.NAMESPACE_DNS, i)) == title:
                title = i
        with open(BlogURL + userName + '/' + title) as f:
            content = markdown.markdown(f.read())
        self.write(content)

class BlogDeletingHandler(BaseHandler):
    @tornado.web.authenticated
    def get(self):
        title = self.get_argument("title")
        userName = tornado.escape.xhtml_escape(self.current_user)
        os.remove(BlogURL + userName + '/' + title)
        self.write("<script>console.log('Delete!')</script>")
        self.redirect("/blog/" + userName)

class BlogRevisingHandler(BaseHandler):
    def get(self):
        title = self.get_argument('title')
        userName = tornado.escape.xhtml_escape(self.current_user)
        with open(BlogURL + userName + '/' + title+'.md', "r") as f:
            content = f.read()
        self.write(content)


class ProfileHandler(BaseHandler):
    def get(self, userName):
        self.title = "Profile"
        #userName = tornado.escape.xhtml_escape(self.current_user)
        avatarURL = 'members/' + userName + '/avatar.png'
        profileURL = BlogURL + userName + '/profile.md'
        with open(profileURL, "r") as f:
            content = markdown.markdown(f.read())
        self.render("blog/profile.html", title = self.title, avatarURL = avatarURL, userName = userName, content = content)

class ProfileEditingHandler(BaseHandler):
    @tornado.web.authenticated
    def post(self):
        content = self.get_argument('content', default="")
        userName = tornado.escape.xhtml_escape(self.current_user)
        profileURL = BlogURL + userName + '/profile.md'
        with open(profileURL, "w") as f:
            f.write(content)
        self.redirect("/profile/" + userName)

class ProfileRequestHandler(BaseHandler):
    @tornado.web.authenticated
    def get(self):
        userName = tornado.escape.xhtml_escape(self.current_user)
        profileURL = BlogURL + userName + '/profile.md'
        with open(profileURL, "r") as f:
            content = f.read()
        self.write(content)

class PasswordChangeHandler(BaseHandler):
    @tornado.web.authenticated
    def post(self):
        password = self.get_argument('password', default="1234")
        userName = tornado.escape.xhtml_escape(self.current_user)
        passwordURL = BlogURL + userName + '/password.salt'
        md5_password = hashlib.md5(password.encode("utf-8")).hexdigest()
        with open(passwordURL, "w") as f:
            f.write(md5_password)
        self.redirect("/blog/" + userName)

class CustomLinkHandler(BaseHandler):
    @tornado.web.authenticated
    def post(self):
        link = self.get_argument('link', default="1234")
        userName = tornado.escape.xhtml_escape(self.current_user)
        linkURL = BlogURL + userName + '/custom.link'
        with open(linkURL, "w") as f:
            f.write(link)
        self.redirect("/blog/" + userName)