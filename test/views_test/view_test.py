# -*- coding: utf-8 -*-
from metaweb import views, resps
from metaweb.resps import Response, RedirectResponse
from metaweb.views import View
from testutil import TestCase

def foo(a, b='2'):
    return int(a) + int(b)
foo.__module__ = 'views.users'
foo = View(foo)

class DecorateTest(TestCase):
    def test_success(self):
        def foo(a, b=2):
            pass
        foo.__module__ = 'views.users'
        View(foo)
        self.assertEquals(1, len(views._views))
        h = views._views['/users/foo']
        self.assertEquals(('a',), h.required_params)
        self.assertEquals((('b', 2),), h.optional_params)
        
    def test_invalid_module(self):
        def foo(a, b=2):
            pass
        View(foo)
        self.assertEquals(0, len(views._views))
        
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
        self.assertEqual(resps.STATUS_400, resp.code)
        self.assertIn('Missing', resp.body)
        
class HandleTest(TestCase):
    def test_success(self):
        resp = foo.handle({'a': '1', 'b': '3'})
        self.assertEquals(resps.STATUS_200, resp.code)
        self.assertEquals('4', resp.body)
        
    def test_response(self):
        def foo():
            raise RedirectResponse('/redirect')
        foo.__module__ = 'views.user'
        foo = View(foo)
        resp = foo.handle({})
        self.assertIsInstance(resp, RedirectResponse)
        
    def test_error(self):
        # set up
        def _view(key):
            raise NotImplementedError()
        _view.__module__ = 'views.user'
        v = View(_view)
        
        # test
        resp = v.handle({'key': '111'})
        self.assertEqual(resps.STATUS_200, resp.code)
        self.assertIn('NotImplementedError', resp.body)
        
class AddDefaultViewTest(TestCase):
    def test(self):
        views.add_default_view('/users/home')
        view = views._views['/']
        resp = view.handle({})
        self.assertIsInstance(resp, RedirectResponse)
        self.assertEqual('/users/home', resp.headers['Location'])
        