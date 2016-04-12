#!/usr/bin/env python2.7
# -*- coding: utf-8 -*-

import tornado.ioloop
import tornado.web
import hashlib
import xml.etree.ElementTree as ET
import time
import urllib2, json
import os
 
def translate(data):
    qword = urllib2.quote(data)
    baseurl = r'http://fanyi.youdao.com/openapi.do?keyfrom=linden&key=1102672932&type=data&doctype=json&version=1.1&q='
    url = baseurl+qword
    resp = urllib2.urlopen(url)
    fanyi = json.loads(resp.read())
    if fanyi['errorCode'] == 0:
        if 'basic' in fanyi.keys():
            trans = u'%s:\n%s\n%s\n网络释义：\n%s'%(fanyi['query'], ''.join(fanyi['translation']), ' '.join(fanyi['basic']['explains']), ''.join(fanyi['web'][0]['value']))
            return trans
        else:
            trans =u'%s:\n基本翻译:%s\n'%(fanyi['query'], ''.join(fanyi['translation']))
            return trans
    elif fanyi['errorCode'] == 20:
        return u'对不起，要翻译的文本过长'
    elif fanyi['errorCode'] == 30:
        return u'对不起，无法进行有效的翻译'
    elif fanyi['errorCode'] == 40:
        return u'对不起，不支持的语言类型'
    else:
        return u'对不起，您输入的单词%s无法翻译,请检查拼写'% data
            
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
        # print ("ToUserName:%s,FromUserName:%sCreateTime:%s,MsgId:%s" % (toUser,fromUser,createTime,msgId))
        response_text = """<xml>
            <ToUserName><![CDATA[%s]]></ToUserName>
            <FromUserName><![CDATA[%s]]></FromUserName>
            <CreateTime>%s</CreateTime>
            <MsgType><![CDATA[%s]]></MsgType>
            <Content><![CDATA[%s]]></Content>
            <MsgId>%s</MsgId>
            </xml>"""
        params = {
            'toUser': toUser,
            'fromUser': fromUser,
            'createTime': int(time.time()),
            'msgType': msgType,
            'reply': {
                'content': 'HELLO!'
            }
        }
        out = self.render_string('reply_text.xml', autoescape=None, **params)
        self.write(out)
        # self.render("reply_text.xml", fromUser=fromUser,toUser=toUser,createTime=createTime,content=content)
        
        # out = response_text % (fromUser, toUser, createTime, msgType, content, msgId)
        # self.write(out)
        
        #if 'text' == msgType:
        #    if 'help' == content.lower():
        #        content = u'''
        #        1.输入"translate"为中英翻译工具
        #        '''
        #    elif type(content).__name__ == "unicode":
        #        content = content.encode('UTF-8')
        #    content = translate(content)
        #    out = response_text % (fromUser, toUser, createTime, msgType, content, msgId)
        # self.write(out)
application = tornado.web.Application([
    (r"/", MainHandler),
])

if __name__ == "__main__":
    template_path=os.path.join(os.path.dirname(__file__), "templates")
    application.listen(80)
    tornado.ioloop.IOLoop.instance().start()