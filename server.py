
import os

import tornado.web
import tornado.httpserver
import tornado.ioloop
import tornado.options
import tornado.locale
# import asyncio
# from mongoengine import connect

from tornado.options import define, options
from tornado.log import enable_pretty_logging

from urls import handlers

enable_pretty_logging()

define('port', default=8000, help='run on the given port', type=int)
# define('db', default='zeus', help='Database Name')

class Application(tornado.web.Application):
    def __init__(self, handlers):    
        settings = dict(
            template_path = os.path.join(os.path.dirname(__file__), 'templates'),
            static_path = os.path.join(os.path.dirname(__file__), 'static'),
            cookie_secret = "dEr2Viz6TrqsoQVbQCRdxUmzKB5q40U0jYtp+fnsAOY=",
            debug = True,            
        )
        tornado.web.Application.__init__(self, handlers, **settings)
        # connect(options.db)
        
def main():
    # asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    tornado.locale.load_translations(os.path.join(os.path.dirname(__file__), "csv_translations"))
    #tornado.options.define("log_file_prefix", default=os.path.join(os.path.dirname(__file__), "tornado_main.log"))
    tornado.options.parse_command_line()
    http_server = tornado.httpserver.HTTPServer(Application(handlers))
    #http_server.listen(options.port)
    http_server.bind(int(options.port), "0.0.0.0")
    #http_server.bind(int(options.port), "localhost")
    http_server.start(1)
    print('Development server is running at http://0.0.0.0:%s/' % options.port) 
    print('Quit the server with Ctrl-C')
    tornado.ioloop.IOLoop.instance().start()
    
if __name__ == '__main__':
    main()
