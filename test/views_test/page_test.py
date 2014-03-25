# -*- coding: utf-8 -*-
from metaweb import views
from metaweb.resps import RedirectResponse
from metaweb.views import Page
from testutil import TestCase

def foo(key, name='default name'):
    return str(key) + '|' + name
foo.__module__ = 'views.users'

class DecorateTest(TestCase):
    def test_default(self):
        Page(default=True)(foo)
        self.assertEquals(2, len(views._views))
        fields = {'key': '1', 'name': 'aaa'}
        self.assertEqual('1|aaa', views._views['/users/foo'].render(fields).body)
        resp = views._views['/users/'].render(fields)
        self.assertIsInstance(resp, RedirectResponse)
        self.assertEqual('/users/foo', resp.headers['Location'])
        