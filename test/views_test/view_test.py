# -*- coding: utf-8 -*-
from metaweb import views
from metaweb.resps import Response, RedirectResponse
from metaweb.views import View
from testutil import TestCase

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
        
class DecodeFieldsTest(TestCase):
    def test_normal(self):
        fields = foo._decode_fields({'a': '1', 'b': '2'})
        self.assertEqual({'a': '1', 'b': '2'}, fields)
        
    def test_chinese(self):
        fields = foo._decode_fields({'a': u'中文'.encode('utf-8')})
        self.assertEqual({'a': u'中文', 'b': '2'}, fields)

    def test_extra_fields(self):
        fields = foo._decode_fields({'a': '1', 'b': '2', 'timestamp': '111'})
        self.assertEqual({'a': '1', 'b': '2'}, fields)
        
    def test_missing_field(self):
        with self.assertRaises(Response) as e:
            foo._decode_fields({})
        resp = e.exception
        self.assertEqual(400, resp.code)
        self.assertIn('Missing', resp.body)
        
class RenderTest(TestCase):
    def test_success(self):
        resp = foo.render({'a': '1', 'b': '3'})
        self.assertEquals(200, resp.code)
        self.assertEquals('4', resp.body)
        
    def test_response(self):
        def foo():
            raise RedirectResponse('/redirect')
        foo.__module__ = 'views.user'
        foo = View(foo)
        resp = foo.render({})
        self.assertIsInstance(resp, RedirectResponse)
        
    def test_error(self):
        # set up
        def _view(key):
            raise NotImplementedError()
        _view.__module__ = 'views.user'
        v = View(_view)
        
        # test
        resp = v.render({'key': '111'})
        self.assertEqual(200, resp.code)
        self.assertIn('NOT_IMPLEMENTED_ERROR', resp.body)
        
class AddDefaultViewTest(TestCase):
    def test(self):
        views.add_default_view('/users/home')
        view = views._views['/']
        resp = view.render({})
        self.assertIsInstance(resp, RedirectResponse)
        self.assertEqual('/users/home', resp.headers['Location'])
        
class LoadTest(TestCase):
    def test(self):
        # set up
        self.patches.patch('metaweb.views._pending_views', [])
        self.patches.patch('metaweb.views._views', {})
        
        # test
        View(foo)
        views.load(roots=['views_test.view_test'])
        self.assertEquals(1, len(views._views))
        self.assertEqual(foo, views._views['/foo']._func)
    