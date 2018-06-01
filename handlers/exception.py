#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import tornado.web
from handlers.base import BaseHandler

class ErrorHandler(BaseHandler):
    def get(self):
        BaseHandler.initialize(self)
        self.write_error(404)

    def write_error(self, status_code, **kwargs):
        self.title = str(status_code)
        if status_code == 404:
            self.render('main/404.html')
        elif status_code == 500:
            self.render('main/500.html')
        elif status_code == 403:
            self.render('main/403.html')
        else:
            self.write('error:' + str(status_code))
