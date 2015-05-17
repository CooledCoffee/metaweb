# -*- coding: utf-8 -*-
from metaweb import views
from metaweb.resps import Response, RedirectResponse
from metaweb.views import View
from testutil import TestCase
import re

def foo(a, b='2'):
    return int(a) + int(b)
foo = View(foo)

class DecorateTest(TestCase):
    def test(self):
        # set up
        self.patches.patch('metaweb.views._pending_views', [])
        
        # test
        View(foo)
        self.assertEquals(1, len(views._pending_views))
        self.assertEqual(foo, views._pending_views[0]._func)
        
class BindTest(TestCase):
    def test_absolute_path(self):
        view = View()
        view.bind('/users')
        self.assertEqual(view, views._abs_pathes['/users'])
        
    def test_regex_path(self):
        view = View()
        view.bind('/users/<id>')
        expected_path = re.compile('^/users/(?P<id>.*?)$')
        self.assertEqual(view, views._regex_pathes[expected_path])
        
class DecodeFieldsTest(TestCase):
    def test_normal(self):
        fields = foo._decode_fields({'a': '1', 'b': '2'})
        self.assertEqual({'a': '1', 'b': '2'}, fields)
        
    def test_chinese(self):
        fields = foo._decode_fields({'a': u'中文'.encode('utf-8')})
        self.assertEqual({'a': u'中文'}, fields)

    def test_extra_fields(self):
        fields = foo._decode_fields({'a': '1', 'b': '2', 'timestamp': '111'})
        self.assertEqual({'a': '1', 'b': '2'}, fields)
        
class RenderTest(TestCase):
    def test_basic(self):
        resp = foo.render({}, {'a': '1', 'b': '3'})
        self.assertEquals(200, resp.code)
        self.assertEquals('4', resp.body)
        
    def test_response(self):
        def foo():
            raise RedirectResponse('/redirect')
        foo.__module__ = 'views.user'
        foo = View(foo)
        resp = foo.render({}, {})
        self.assertIsInstance(resp, RedirectResponse)
        
    def test_path_args(self):
        resp = foo.render({'a': '1'}, {'b': '3'})
        self.assertEquals(200, resp.code)
        self.assertEquals('4', resp.body)
        
        resp = foo.render({'a': '0'}, {'a': '1', 'b': '3'})
        self.assertEquals(200, resp.code)
        self.assertEquals('4', resp.body)
        
    def test_missing_field(self):
        resp = foo.render({}, {})
        self.assertEqual(400, resp.code)
        
    def test_error(self):
        # set up
        def _view(key):
            raise NotImplementedError()
        _view.__module__ = 'views.user'
        v = View(_view)
        
        # test
        resp = v.render({}, {'key': '111'})
        self.assertEqual(500, resp.code)
        self.assertIn('NOT_IMPLEMENTED_ERROR', resp.body)
        
class AddDefaultViewTest(TestCase):
    def test(self):
        views.add_default_view('/users/home')
        view = views._abs_pathes['/']
        resp = view.render({}, {})
        self.assertIsInstance(resp, RedirectResponse)
        self.assertEqual('/users/home', resp.headers['Location'])
        
class LoadTest(TestCase):
    def test_basic(self):
        view = View(foo)
        views.load(roots=['views_test.view_test'])
        self.assertEquals(1, len(views._abs_pathes))
        self.assertEqual(view, views._abs_pathes['/foo'])
    
    def test_prefix(self):
        view = View(foo)
        views.load(roots={'views_test.view_test': '/prefix'})
        self.assertEquals(1, len(views._abs_pathes))
        self.assertEqual(view, views._abs_pathes['/prefix/foo'])
        
    def test_out_of_roots(self):
        View(foo)
        views.load(roots=['metaweb.views'])
        self.assertEquals(0, len(views._abs_pathes))
        
class MatchTest(TestCase):
    def test_absolute_path(self):
        # set up
        v = object()
        self.patches.patch('metaweb.views._abs_pathes', {'/users/': v})
        
        # test
        view, args = views.match('/users/')
        self.assertEquals(v, view)
        self.assertEqual({}, args)
        
    def test_regex_path(self):
        # set up
        v = object()
        self.patches.patch('metaweb.views._regex_pathes', {re.compile('^/users/(?P<id>.*?)$'): v})
        
        # test
        view, args = views.match('/users/111')
        self.assertEquals(v, view)
        self.assertEqual(1, len(args))
        self.assertEqual('111', args['id'])
        
    def test_not_found(self):
        view, args = views.match('/users/create')
        self.assertIsNone(view)
        self.assertIsNone(args)
        