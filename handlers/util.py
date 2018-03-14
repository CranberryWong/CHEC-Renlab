from handlers.base import BaseHandler

class I18nHandler(BaseHandler):
    def get(self):
        language = self.get_argument("lang_encode")
        if language == 'zh_CN':
            self.lang_encode = 'zh_CN'
        elif language == 'ja_JP':
            self.lang_encode = 'ja_JP'
        elif language == 'en_US':
            self.lang_encode = 'en_US'
        else:
            self.lang_encode = 'en_US'
        self.redirect('/')

WebpageList = [
    '1-apple.com.png',
]