#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import tornado.web
import tornado.locale
import random
import time
import os
import re
import csv
from selenium import webdriver
from handlers.base import BaseHandler
from handlers.aesthetics.settings import WebpageList
from models.user import User
from models.webpage import Webpage
from functools import reduce
from handlers.exception import ErrorHandler

prefix = '/Pictures/buffer/'

class HomeHandler(BaseHandler):
    def get(self):
        BaseHandler.initialize(self)
        self.title = 'Optimizing Your Design'
        self.render("visualization/vhome.html")

class MainHandler(BaseHandler):
    def get(self):
        BaseHandler.initialize(self)
        
        self.title = 'Optimizing'
        self.render("visualization/vmain.html")

    def post(self):
        BaseHandler.initialize(self)
        windowWidth = 1900
        windowHeight = 900 + 123
        self.title = "Optimizing"
        url = self.get_argument('url', default='')
        
        driver = webdriver.Chrome()
        driver.set_window_size(windowWidth, windowHeight)
        driver.get(url)
        driver.save_screenshot(os.getenv("HOME") + prefix + 'webpages/' + domainNAME + '.png')
        driver.close()