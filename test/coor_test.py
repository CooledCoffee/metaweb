# -*- coding: utf-8 -*-
from metaweb import views, coor
from metaweb.resps import Response, NotFoundResponse
from testutil import TestCase

class GetViewTest(TestCase):
    def test_found(self):
        # set up
        view = object()
        self.patches.patch('metaweb.views._abs_pathes', {'/users/create': view})
        
        # test
        result = coor._get_view('/users/create')
        self.assertEquals(view, result)
        
    def test_found_with_slash(self):
        # set up
        self.patches.patch('metaweb.views._abs_pathes', {'/users/': object()})
            
        # test
        with self.assertRaises(Response) as ctx:
            coor._get_view('/users')
        resp = ctx.exception
        self.assertEquals(301, resp.code)
        self.assertEquals('/users/', resp.headers['Location'])
        
    def test_not_found(self):
        with self.assertRaises(NotFoundResponse):
            coor._get_view('/users')
            