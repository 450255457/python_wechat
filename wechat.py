#!/usr/bin/env python2.7
# -*- coding: utf-8 -*-

import tornado.ioloop
import tornado.web
import hashlib
import xml.etree.ElementTree as ET
import time

def check_signature(signature, timestamp, nonce):
    # 微信公众平台里输入的token
    token="linden"
    #字典序排序
    list = [token,timestamp,nonce]
    list.sort()
    sha1=hashlib.sha1()
    map(sha1.update,list)
    hashcode=sha1.hexdigest()
    return hashcode == signature

class MainHandler(tornado.web.RequestHandler):
    def get(self):
        signature = self.get_argument('signature')
        timestamp = self.get_argument('timestamp')
        nonce = self.get_argument('nonce')
        echostr = self.get_argument('echostr')
        if check_signature(signature, timestamp, nonce):
            self.write(echostr)
        else:
            self.write('fail')
    def post(self): 
        body = self.request.body
        data = ET.fromstring(body)
        toUser = data.find('ToUserName').text
        fromUser = data.find('FromUserName').text
        createTime = int(time.time())
        msgType = data.find('MsgType').text
        content = data.find('Content').text
        msgId= data.find("MsgId").text
        textTpl = """<xml>
            <ToUserName><![CDATA[%s]]></ToUserName>
            <FromUserName><![CDATA[%s]]></FromUserName>
            <CreateTime>%s</CreateTime>
            <MsgType><![CDATA[%s]]></MsgType>
            <Content><![CDATA[%s]]></Content>
            <MsgId>%s</MsgId>
            </xml>"""
        out = textTpl % (fromUser, toUser, createTime, msgType, content, msgId)
        self.write(out)
        # self.render('reply_text.html', toUser=toUser, fromUser=fromUser, createTime=createTime, content=content)
application = tornado.web.Application([
    (r"/", MainHandler),
])

if __name__ == "__main__":
    application.listen(80)
    tornado.ioloop.IOLoop.instance().start()