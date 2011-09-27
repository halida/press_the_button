#!/usr/bin/env python
#-*- coding:utf-8 -*-
"""
module: poll
"""

import logging
import tornado.auth
import tornado.escape
import tornado.ioloop
import tornado.options
import tornado.web
import os.path
import uuid

import redis

r = redis.Redis()

from tornado.options import define, options

define("port", default=8110, help="long pull", type=int)

class Application(tornado.web.Application):
    def __init__(self):
        handlers = [
            (r"/", MainHandler),
            (r"/press", PressHandler),
            (r"/number", NumberHandler),
        ]
        settings = dict(
            # cookie_secret="43oETzKXQAGaYdkL5gEmGeJJFuYh7EQnp2XdTP1o/Vo=",
            xsrf_cookies=False,
        )
        tornado.web.Application.__init__(self, handlers, **settings)

class BaseHandler(tornado.web.RequestHandler):
    def check_xsrf_cookie():
        pass

class MessageMixin(object):
    waiters = []

    def wait_for_number(self, callback):
        cls = MessageMixin
        cls.waiters.append(callback)

    def press(self):
        cls = MessageMixin
        n = r.incr('press_button_number')
        n = str(n)
        logging.info("Sending new number to %r listeners", len(cls.waiters))
        for callback in cls.waiters:
            try:
                callback(n)
            except:
                logging.error("Error in waiter callback", exc_info=True)
        cls.waiters = []

class PressHandler(BaseHandler, MessageMixin):
    def get(self):
        self.press()
        
    def post(self):
        self.press()

class NumberHandler(BaseHandler, MessageMixin):
    @tornado.web.asynchronous
    def get(self):
        self.wait_for_number(self.async_callback(self.on_new_press))
        
    @tornado.web.asynchronous
    def post(self):
        self.wait_for_number(self.async_callback(self.on_new_press))

    def on_new_press(self, n):
        # Closed client connection
        if self.request.connection.stream.closed():
            return
        self.finish(n)


def main():
    tornado.options.parse_command_line()
    app = Application()
    app.listen(options.port)
    tornado.ioloop.IOLoop.instance().start()


if __name__ == "__main__":
    main()
