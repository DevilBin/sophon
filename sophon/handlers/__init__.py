#!/usr/bin/env python2
# -*- coding: utf-8 -*-

from tornado.web import RequestHandler


class BaseHandler(RequestHandler):

    def get_current_user(self):
        return self.get_secure_cookie("username")
