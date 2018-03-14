import tornado.web
import tornado.locale
from models.user import User

class BaseHandler(tornado.web.RequestHandler):
    
    def initialize(self, title="Untitled", lang_encode="en_US"):
        tornado.locale.set_default_locale(lang_encode)
        self.title = title
        self.lang_encode = lang_encode
        self.message = None

    def get_user_locale(self):
        return tornado.locale.get("en_US")

    def get_current_user(self):
        return self.get_secure_cookie('username')    
        


    