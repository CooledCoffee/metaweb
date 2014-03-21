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
        with self.assertRaises(Response) as ctx:
            coor._load_view('/users')
        resp = ctx.exception
        self.assertEquals(301, resp.code)
        self.assertEquals('/users/', resp.headers['Location'])
        
    def test_not_found(self):
        with self.assertRaises(NotFoundResponse):
            coor._load_view('/users')
            