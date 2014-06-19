# -*- coding: utf-8 -*-
from metaweb import views
from metaweb.resps import RedirectResponse
from metaweb.views import Page
from testutil import TestCase

def foo(a, b='0'):
    return str(int(a) + int(b))

class DecorateTest(TestCase):
    def test_default_root(self):
        # set up
        self.patches.patch('metaweb.views._pending_views', [])
        self.patches.patch('metaweb.views._views', {})
        
        # test
        page = Page(default=True)(foo)
        page.bind('/foo')
        
        # verify
        self.assertEquals(2, len(views._views))
        fields = {'a': '1', 'b': '2'}
        self.assertEqual('3', views._views['/foo'].render(fields).body)
        resp = views._views['/'].render(fields)
        self.assertIsInstance(resp, RedirectResponse)
        self.assertEqual('foo', resp.headers['Location'])
        
    def test_default_not_root(self):
        # set up
        self.patches.patch('metaweb.views._pending_views', [])
        self.patches.patch('metaweb.views._views', {})
        
        # test
        page = Page(default=True)(foo)
        page.bind('/users/foo')
        
        # verify
        self.assertEquals(2, len(views._views))
        fields = {'a': '1', 'b': '2'}
        self.assertEqual('3', views._views['/users/foo'].render(fields).body)
        resp = views._views['/users/'].render(fields)
        self.assertIsInstance(resp, RedirectResponse)
        self.assertEqual('foo', resp.headers['Location'])
        