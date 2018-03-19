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

WebpageLists = [
    # More and more use interactive webpage

    # Trial
    #'1_http://apple.com',

    # Webby
    #'1*http://projects.two-n.com/world-gender/',
    '1*two-n.com',
    '2*makeitok.org',

    #Brand
    '3*mozilla.org',
    '4*segmentfault.com',
    '5*kameisyouten.ocnk.net',
    #'6*https://docs.opencv.org/3.0-beta/doc/py_tutorials/py_setup/py_intro/py_intro.html#intro',
    '6*docs.opencv.org',
    #'7*http://blog.sciencenet.cn/blog.php',
    '7*blog.sciencenet.cn',
    '8*yinwang.org',
    #'9*http://www.richyli.com/tool/loremipsum/',
    '9*richyli.com',
    '10*pxtoem.com',
    '11*nounplus.net'

]