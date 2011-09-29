#!/usr/bin/env python
#-*- coding:utf-8 -*-
"""
module: websocket_server
"""
import sys, os, time, logging, json

import tornado
import tornado.web, tornado.websocket

import redis
r = redis.Redis()


class ChatRoomWebSocket(tornado.websocket.WebSocketHandler):
    connects = []
    def open(self):
        self.name = '???'
        self.room = -1
        # 显示现在已经在的人
        self.write_message('current in: ' + ', '.join([u"%s in room %d" % (c.name, c.room)
                                                       for c in self.connects]))
        self.connects.append(self)
        
    def on_message(self, message):
        data = json.loads(message)
        if data.has_key('name'):
            self.name = data['name']
            self.room = data['room']
            self.broadcast(self.room, self.name + ' enters.')
            return
        else:
            self.broadcast(self.room, self.name + ' says: ' + data['msg'])

    def broadcast(self, room, msg):
        for c in self.connects:
            if c.room == room:
                try:
                    c.write_message(msg)
                except:
                    # 防止出现错误
                    self.connects.remove(c)
            
    def on_close(self):
        self.connects.remove(self)
        self.broadcast(self.room, self.name + ' leaves.')

class ButtonSocket(tornado.websocket.WebSocketHandler):
    connects = []
    
    def open(self):
        self.write_message(r.get('press_button_number'))
        self.connects.append(self)
        
    def on_message(self, message):
        # print "on press:", message
        pressed = r.incr('press_button_number')
        self.broadcast(str(pressed))

    def broadcast(self, pressed):
        for c in self.connects:
            try:
                # print "write to c"
                c.write_message(pressed)
            except:
                # 防止出现错误
                self.connects.remove(c)
            
    def on_close(self):
        self.connects.remove(self)


settings = {
    "static_path": os.path.join(os.path.dirname(__file__), "static"),
    "cookie_secret": "61oETzKXQAGaYdkL5gEmGeJJFuYh7EQnp2XdTP1o/Vo=",
    # "login_url": "/login",
    # "xsrf_cookies": True,
    'debug' : True,
}

application = tornado.web.Application([
    (r"/button", ButtonSocket),
    (r"/chatroom", ChatRoomWebSocket),
    ], **settings)

def main():
    application.listen(9999)
    try:
        io_loop = tornado.ioloop.IOLoop.instance()
        io_loop.start()
    except KeyboardInterrupt:
        print "bye!"

if __name__ == "__main__":
    main()

