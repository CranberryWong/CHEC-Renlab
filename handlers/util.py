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
    # More and more use interactive webpage

    # Trial
    '1_http://apple.com',

    # Webby
    '3_http://projects.two-n.com/world-gender/',
    '4_https://makeitok.org/',

    #Brand
    'https://www.pantone.com/',
    '2_http://mozilla.org',
    'https://segmentfault.com/',
    'http://kameisyouten.ocnk.net',
    'https://docs.opencv.org/3.0-beta/doc/py_tutorials/py_setup/py_intro/py_intro.html#intro',
    'http://blog.sciencenet.cn/blog.php',
    'http://www.yinwang.org'
    'http://www.richyli.com/tool/loremipsum/'

]