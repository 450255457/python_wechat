#!/usr/bin/env python2.7
# -*- coding: utf-8 -*-

import tornado.web
import urllib2
import ConfigParser
import json


class MenuSetupHandler(tornado.web.RequestHandler):

    def initialize(self, access_token_manager, menus):
        self.access_token_manager = access_token_manager
        self.menus = menus
        self.cf = ConfigParser.ConfigParser()
        self.cf.read("conf/weixin.conf")

    def get(self):
        url = self.cf.get("access", "menu_setup_url") % (self.access_token_manager.get(), )
        print url
        req = urllib2.Request(url=url, data=json.dumps(self.menus, ensure_ascii=False))
        response = urllib2.urlopen(req).read()
        print response