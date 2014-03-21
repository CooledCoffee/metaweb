# -*- coding: utf-8 -*-
from fixtures._fixtures.monkeypatch import MonkeyPatch
from metaweb import views, coor
from metaweb.resps import Response, NotFoundResponse
from testutil import TestCase

class LoadViewTest(TestCase):
    def setUp(self):
        super(LoadViewTest, self).setUp()
        self.useFixture(MonkeyPatch('metaweb.views._views', {}))
        
    def test_found(self):
        # set up
        view = object()
        views._views['/users/create'] = view
        
        # test
        result = coor._load_view('/users/create')
        self.assertEquals(view, result)
        
    def test_found_with_slash(self):
        # set up
        views._views['/users/'] = object()
            
        # test
        try:
            coor._load_view('/users')
            self.fail()
        except Response, r:
            self.assertEquals('301 Moved Permanently', r.code)
            self.assertEquals('/users/', r.headers['Location'])
        
    def test_not_found(self):
        with self.assertRaises(NotFoundResponse):
            coor._load_view('/users')
            