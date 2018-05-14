#! /usr/local/bin python3

import tornado
import tornado.locale
import markdown
import os

from handlers.util import *
from handlers.base import BaseHandler

NewsURL = os.path.join(os.path.dirname('./..'), "static/news/")

class NewsHandler(BaseHandler):
    def get(self):
        self.title = "News"
        newsList = [ (x, os.stat(NewsURL + x)) for x in os.listdir(NewsURL) if x not in ignore_list ]
        self.render("home/news.html", title = self.title, newsList = newsList)

class NewsShowHandler(BaseHandler):
    def get(self, news):
        print(1)
        print(news)
        self.title = news
        with open(NewsURL + news + '.md') as f:
            content = markdown.markdown(f.read())
        self.render("home/page.html", title = self.title, content = content)
