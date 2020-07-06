#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import tornado
import tornado.locale
import markdown
import os
import uuid
import hashlib
import time
import boto3 
import botocore

from handlers.util import *
from handlers.base import BaseHandler

class MainHandler(BaseHandler):
    @tornado.web.authenticated
    def get(self, userName):
        BaseHandler.initialize(self)
        self.title = "New Blog"
        self.render("newblog/main.html", title = self.title, userName = userName)