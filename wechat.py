#!/usr/bin/env python2.7
# -*- coding: utf-8 -*-

import tornado.ioloop
import tornado.web
import hashlib
import xml.etree.ElementTree as ET
import time
import urllib2, json
import os

import access_token_server
import menus
access_token_manager = access_token_server.AccessTokenManager()
menus_to_set = {
     "button":[
     {    
          "type":"click",
          "name":"今日歌曲",
          "key":"V1001_TODAY_MUSIC"
      },
      {
           "name":"菜单",
           "sub_button":[
           {    
               "type":"view",
               "name":"搜索",
               "url":"http://www.soso.com/"
            },
            {
               "type":"view",
               "name":"视频",
               "url":"http://v.qq.com/"
            },
            {
               "type":"click",
               "name":"赞一下我们",
               "key":"V1001_GOOD"
            }]
       }]
}

# 微信公众平台里输入的token
token = "linden"
AppID = 'wx3c6944e7541cf4e0'
AppSecret = 'ebf3493166f6c164f7cfd0f63647f90c'
access_token_url = 'https://api.weixin.qq.com/cgi-bin/token?grant_type=client_credential&appid=' + AppID + '&secret=' + AppSecret
     
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
    if not signature or not timestamp or not nonce:
            return False
    #字典序排序
    tmp_list = [token,timestamp,nonce]
    tmp_list.sort()
    tmp_str = ''.join(tmp_list)
    if signature != hashlib.sha1(tmp_str.encode('utf-8')).hexdigest():
        return False
    return True

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
        # msgId= data.find("MsgId").text

        if 'text' == msgType:
            content = translate(content)
        if type(content).__name__ == "unicode":
            content = content.encode('UTF-8')
            
        # from与to在返回的时候要交换
        params = {
            'toUser': fromUser,
            'fromUser': toUser,
            'createTime': createTime,
            'msgType': msgType,
            'reply': {
                'content': content
            }
        }
        self.render('message_reply.html',**params)

application = tornado.web.Application(
    handlers=[(r'/', MainHandler)],
    (r'/menus', menus.MenuSetupHandler, dict(access_token_manager=access_token_manager, menus=menus_to_set)),
    template_path=os.path.join(os.path.dirname(__file__), "templates"),
    static_path=os.path.join(os.path.dirname(__file__), "static"),
    debug=True
)

if __name__ == "__main__":
    application.listen(80)
    tornado.ioloop.IOLoop.instance().start()