#!/usr/bin/env python
# -*- coding:utf-8 -*-

from handlers import main, exception

handlers = [
            (r"/", main.MainHandler),
            (r"/aesthetic/statement", main.StatementHandler),
            (r"/aesthetic/form", main.FormHandler),
            (r"/aesthetic/note", main.NoteHandler),
            (r"/aesthetic/start/([0-9]+)", main.WebpageHandler),
            (r"/aesthetic/ratings", main.RatingHandler),
            (r"/finish", main.FinishHandler),

            (r".*", exception.ErrorHandler)
    ]