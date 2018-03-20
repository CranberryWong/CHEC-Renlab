import tornado.web
import tornado.locale
import random
from models.user import User
from handlers.settings import WebpageList
# from mongoengine import *

class BaseHandler(tornado.web.RequestHandler):
    
    def initialize(self, title="Untitled", lang_encode="en_US"):
        tornado.locale.set_default_locale(lang_encode)
        self.title = title
        self.lang_encode = lang_encode
        self.message = None

    def get_user_locale(self):
        return tornado.locale.get("en_US")

    def get_current_user(self):
        return self.get_cookie('username')  

    def get_current_id(self):
        return self.get_cookie('uid')  
        


    