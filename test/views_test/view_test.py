# -*- coding: utf-8 -*-
from decorated.base.context import Context
from metaweb import views
from metaweb.path import Path
from metaweb.resps import RedirectResponse
from metaweb.views import View
from testutil import TestCase
import re

def foo(a, b='2'):
    return str(int(a) + int(b))
foo = View(foo)

class DecorateTest(TestCase):
    def test(self):
        # set up
        self.patches.patch('metaweb.views._pending_views', [])
        
        # test
        View(foo)
        self.assertEqual(1, len(views._pending_views))
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
        self.assertEqual(1, len(views._regex_pathes[expected_path]._path_params))
        self.assertEqual(unicode, views._regex_pathes[expected_path]._path_params['id'])
        
    def test_regex_path_with_type(self):
        view = View()
        view.bind('/users/<id:int>')
        expected_path = re.compile('^/users/(?P<id>.*?)$')
        self.assertEqual(view, views._regex_pathes[expected_path])
        self.assertEqual(1, len(views._regex_pathes[expected_path]._path_params))
        self.assertEqual(int, views._regex_pathes[expected_path]._path_params['id'])
        
class ParseArgsTest(TestCase):
    def test_from_fields(self):
        fields = foo._parse_args({'a': '1', 'b': '2'}, {})
        self.assertEqual({'a': '1', 'b': '2'}, fields)
        
    def test_from_path_args(self):
        # set up
        def foo(a, b):
            return str(int(a) + int(b))
        foo = View(foo)
        foo._path_params = {'a': int}
        
        # basic test
        fields = foo._parse_args({'b': '2'}, {'a': '1'})
        self.assertEqual({'a': 1, 'b': '2'}, fields)
        
    def test_chinese(self):
        fields = foo._parse_args({'a': u'中文'.encode('utf-8')}, {})
        self.assertEqual({'a': u'中文', 'b': '2'}, fields)

    def test_extra_fields(self):
        fields = foo._parse_args({'a': '1', 'b': '2', 'timestamp': '111'}, {})
        self.assertEqual({'a': '1', 'b': '2'}, fields)
        
class RenderTest(TestCase):
    def test_basic(self):
        request = {
            'cookies': {},
            'fields': {'a': '1', 'b': '3'},
            'headers': {},
            'path': Path('/test'),
        }
        resp = foo.render(request, Context)
        self.assertEqual(200, resp.status)
        self.assertEqual('4', resp.body)
        
    def test_response(self):
        def foo():
            raise RedirectResponse('/redirect')
        foo.__module__ = 'views.user'
        foo = View(foo)
        request = {
            'cookies': {},
            'fields': {},
            'headers': {},
            'path': Path('/test'),
        }
        resp = foo.render(request, Context)
        self.assertIsInstance(resp, RedirectResponse)
        
    def test_400(self):
        request = {
            'cookies': {},
            'fields': {},
            'headers': {},
            'path': Path('/test'),
        }
        resp = foo.render(request, Context)
        self.assertEqual(400, resp.status)
        
    def test_500(self):
        # set up
        def _view():
            raise NotImplementedError()
        _view.__module__ = 'views.user'
        v = View(_view)
        
        # test
        request = {
            'cookies': {},
            'fields': {},
            'headers': {},
            'path': Path('/test'),
        }
        resp = v.render(request, Context)
        self.assertEqual(500, resp.status)
        
class AddDefaultViewTest(TestCase):
    def test(self):
        views.add_default_view('/users/home')
        request = {
            'cookies': {},
            'fields': {},
            'headers': {},
            'path': Path('/'),
        }
        view = views._abs_pathes['/']
        resp = view.render(request, Context)
        self.assertIsInstance(resp, RedirectResponse)
        self.assertEqual('/users/home', resp.headers['Location'])
        
class LoadTest(TestCase):
    def test_basic(self):
        view = View(foo)
        views.load(roots=['views_test.view_test'])
        self.assertEqual(1, len(views._abs_pathes))
        self.assertEqual(view, views._abs_pathes['/foo'])
    
    def test_prefix(self):
        view = View(foo)
        views.load(roots={'views_test.view_test': '/prefix'})
        self.assertEqual(1, len(views._abs_pathes))
        self.assertEqual(view, views._abs_pathes['/prefix/foo'])
        
    def test_out_of_roots(self):
        View(foo)
        views.load(roots=['metaweb.views'])
        self.assertEqual(0, len(views._abs_pathes))
        
class MatchTest(TestCase):
    def test_absolute_path(self):
        # set up
        v = lambda: None
        self.patches.patch('metaweb.views._abs_pathes', {'/users/': v})
        
        # test
        path = views.match('/users/')
        self.assertEqual('/users/', path)
        self.assertEqual(v, path.view)
        self.assertEqual({}, path.args)
        
    def test_regex_path(self):
        # set up
        v = lambda: None
        self.patches.patch('metaweb.views._regex_pathes', {re.compile('^/users/(?P<id>.*?)$'): v})
        
        # test
        path = views.match('/users/111')
        self.assertEqual('/users/111', path)
        self.assertEqual(v, path.view)
        self.assertEqual({'id': '111'}, path.args)
        
    def test_not_found(self):
        path = views.match('/users/create')
        self.assertIsNone(path)
        