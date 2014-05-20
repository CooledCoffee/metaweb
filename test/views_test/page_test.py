# -*- coding: utf-8 -*-
from metaweb import views
from metaweb.resps import RedirectResponse
from metaweb.views import Page
from testutil import TestCase

def foo(key, name='default name'):
    return str(key) + '|' + name

class DecorateTest(TestCase):
    def test_default(self):
        # set up
        self.patches.patch('metaweb.views._pending_views', [])
        self.patches.patch('metaweb.views._views', {})
        
        # test
        Page(default=True)(foo)
        views.load(roots=['views_test.page_test'])
        
        # verify
        self.assertEquals(2, len(views._views))
        fields = {'key': '1', 'name': 'aaa'}
        self.assertEqual('1|aaa', views._views['/foo'].render(fields).body)
        resp = views._views['/'].render(fields)
        self.assertIsInstance(resp, RedirectResponse)
        self.assertEqual('/foo', resp.headers['Location'])
        