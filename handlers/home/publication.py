#! /usr/local/bin python3

import tornado
import tornado.locale
import markdown
import os

from handlers.base import BaseHandler

PubURL = os.path.join(os.path.dirname('./..'), "static/publication/publication.md")

class PubHandler(BaseHandler):
    def get(self):
        print(PubURL)
        self.title = "Publication"
        with open(PubURL, "r") as f:
            content = markdown.markdown(f.read())
        self.render("home/publication.html", title = self.title, content = content)