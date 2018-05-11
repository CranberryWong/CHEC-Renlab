from handlers.base import BaseHandler

ignore_list = [
    '.DS_Store',
    'avatar.png',
    'profile.md',
    'password.salt',
]

class I18nHandler(BaseHandler):
    def get(self):
        language = self.get_argument("lang")
        if language == 'zh_CN':
            self.lang_encode = 'zh_CN'
        elif language == 'ja_JP':
            self.lang_encode = 'ja_JP'
        elif language == 'en_US':
            self.lang_encode = 'en_US'
        else:
            self.lang_encode = 'en_US'
        self.redirect('/')