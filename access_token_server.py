#!/usr/bin/env python2.7
# -*- coding: utf-8 -*-

import time
import ConfigParser
import urllib2
import json


class AccessTokenManager():

    def __init__(self):
        self.access_token = None
        self.expires_in = 0
        # 上次获取时间
        self.gettime = 0

        self.cf = ConfigParser.ConfigParser()
        self.cf.read("conf/weixin.conf")

    def get(self):
        if self.gettime + self.expires_in <= time.time():
            self.gettime = time.time()
            response = urllib2.urlopen(self.cf.get("access", "access_token_url")).read()
            response = json.loads(response)
            self.access_token = response["access_token"]
            self.expires_in = response["expires_in"]
            print "%s: Get Access Token [%s] for %ss " % (time.ctime(self.gettime), self.access_token, self.expires_in)
        return self.access_token