#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import tornado
import tornado.locale
import markdown
import os

from handlers.base import BaseHandler

class IndexHandler(BaseHandler):
    def get(self):
        BaseHandler.initialize(self)
        self.render("iss2018workshop/index.html")