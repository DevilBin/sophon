#!/usr/bin/env python2
# -*- coding: utf-8 -*-

import urllib
import json

import mock
import tornado.web
from tornado.testing import AsyncHTTPTestCase

from sophon.config import TORNADO_SETTINGS
from sophon.handlers.user import GetUserInfoHandler, LoginHandler, LogoutHandler


class TestLoginHandler(AsyncHTTPTestCase):

    def get_app(self):
        return tornado.web.Application(
            [(r"/api/user/login", LoginHandler)],
            **TORNADO_SETTINGS
        )

    @mock.patch("sophon.handlers.user.UserMeta")
    def test_login_success(self, _UserMeta):
        _query, _filter_by, _first, _check_password = (
            mock.Mock(), mock.Mock(), mock.Mock(), mock.Mock()
        )
        _query_data = mock.Mock()
        _query_data.id, _query_data.user_type = 42, 1
        _first.return_value = _query_data
        _filter_data = mock.Mock()
        _filter_data.first = _first
        _filter_by.return_value = _filter_data
        _query.filter_by = _filter_by
        _UserMeta.query = _query

        _check_password.return_value = True
        _UserMeta.check_password = _check_password

        post_data = {
            "username": "Alice",
            "password": "notgoodpasswd"
        }
        post_body = urllib.urlencode(post_data)
        response = self.fetch(r"/api/user/login",
                              method="POST",
                              body=post_body)
        response_body = json.loads(response.body)

        _check_password.assert_called_once_with(username="Alice",
                                                password="notgoodpasswd")
        _filter_by.assert_called_once_with(username="Alice")
        _first.assert_called_once_with()
        self.assertEqual(response.code, 200)
        self.assertEqual(
            response_body,
            {
                "id": 42,
                "username": "Alice",
                "type": 1
            }
        )

    @mock.patch("sophon.handlers.user.UserMeta")
    def test_login_failed(self, _UserMeta):
        _check_password = mock.Mock()
        _check_password.return_value = False
        _UserMeta.check_password = _check_password
        post_data = {
            "username": "Alice",
            "password": "notgoodpasswd"
        }
        post_body = urllib.urlencode(post_data)
        response = self.fetch(r"/api/user/login",
                              method="POST",
                              body=post_body)
        response_body = json.loads(response.body)

        self.assertEqual(response.code, 200)
        self.assertIn("msg", response_body)


class TestLogoutHandler(AsyncHTTPTestCase):

    def get_app(self):
        return tornado.web.Application(
            [(r"/api/user/logout", LogoutHandler)],
            **TORNADO_SETTINGS
        )

    def test_logout(self):
        with mock.patch.object(LogoutHandler, "clear_cookie") as _clear_cookie:
            response = self.fetch(r"/api/user/logout")
            response_body = json.loads(response.body)

            self.assertEqual(response.code, 200)
            self.assertEqual(response_body, {})
            _clear_cookie.assert_called_once_with("username")

class TestGetUserInfoHandler(AsyncHTTPTestCase):

    def get_app(self):
        return tornado.web.Application(
            [(r"/api/user/info", GetUserInfoHandler)],
            **TORNADO_SETTINGS
        )

    def test_get_info_without_login(self):
        response = self.fetch(r"/api/user/info")
        response_body = json.loads(response.body)

        self.assertEqual(response.code, 200)
        self.assertEqual(response_body, {})

    @mock.patch("sophon.handlers.user.UserMeta")
    def test_get_info_with_login(self, _UserMeta):
        _query, _filter_by, _first = (
            mock.Mock(), mock.Mock(), mock.Mock()
        )
        _query_data = mock.Mock()
        _query_data.id, _query_data.user_type = 42, 1
        _first.return_value = _query_data
        _filter_data = mock.Mock()
        _filter_data.first = _first
        _filter_by.return_value = _filter_data
        _query.filter_by = _filter_by
        _UserMeta.query = _query

        with mock.patch.object(
            GetUserInfoHandler, "get_secure_cookie"
        ) as _get_secure_cookie:
            _get_secure_cookie.return_value = "Alice"

            response = self.fetch(r"/api/user/info")
            response_body = json.loads(response.body)

            _get_secure_cookie.assert_called_once_with("username")
            _filter_by.assert_called_once_with(username="Alice")
            _first.assert_called_once_with()
            self.assertEqual(response.code, 200)
            self.assertEqual(
                response_body,
                {
                    "id": 42,
                    "username": "Alice",
                    "type": 1
                }
            )


