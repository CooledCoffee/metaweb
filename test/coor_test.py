# -*- coding: utf-8 -*-
from metaweb import coor
from metaweb.resps import NotFoundResponse
from testutil import TestCase

class MatchViewTest(TestCase):
    def test_found(self):
        # set up
        v = object()
        self.patches.patch('metaweb.views._abs_pathes',
                {'/users/create': {'handler': v}})
        
        # test
        view, args = coor._match_view('/users/create')
        self.assertEquals(v, view)
        self.assertEquals({}, args)
        
    def test_not_found(self):
        with self.assertRaises(NotFoundResponse):
            coor._match_view('/users')
            