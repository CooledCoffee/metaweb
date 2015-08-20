# -*- coding: utf-8 -*-
from datetime import date, datetime, time
from decorated.base.context import Context
from metaweb.resps import RedirectResponse
from metaweb.views import Api, JsonEncoder
from testutil import TestCase
import json

@Api
def foo(a, b=2):
    return {'a': a, 'b': b}

class JsonEncoderTest(TestCase):
    def test_normal(self):
        self.assertEqual('111', json.dumps(111, cls=JsonEncoder))
        self.assertEqual('"aaa"', json.dumps('aaa', cls=JsonEncoder))
        
    def test_datetime(self):
        self.assertEqual('"2010-01-02"', json.dumps(date(2010, 1, 2), cls=JsonEncoder))
        self.assertEqual('"12:30:40"', json.dumps(time(12, 30, 40), cls=JsonEncoder))
        self.assertEqual('"2010-01-02 12:30:40"', json.dumps(datetime(2010, 1, 2, 12, 30, 40), cls=JsonEncoder))
        
    def test_customized(self):
        class Foo(object):
            def __json__(self):
                return 'foo'
        self.assertEqual('"foo"', json.dumps(Foo(), cls=JsonEncoder))

class TranslateResultTest(TestCase):
    def test_object(self):
        self.assertEqual('"aaa"', foo._translate_result('aaa').body)
        self.assertEqual('111', foo._translate_result(111).body)
        self.assertEqual('"2010-01-02"', foo._translate_result(date(2010, 1, 2)).body)
         
    def test_resp(self):
        result = RedirectResponse('/')
        resp = foo._translate_result(result)
        self.assertEqual(result, resp)
        
class RenderTest(TestCase):
    def test_normal(self):
        resp = foo.render(Context(), {}, {'a': '1', 'b': '3'})
        self.assertEqual(200, resp.status)
        self.assertEqual({'a': 1, 'b': 3}, json.loads(resp.body))
        
    def test_400(self):
        resp = foo.render(Context(), {}, {})
        self.assertEqual(400, resp.status)
        
    def test_500(self):
        # set up
        def _view(key):
            raise NotImplementedError('Error message.')
        _view.__module__ = 'views.user'
        v = Api(_view)
        
        # test
        resp = v.render(Context(), {}, {'key': '111'})
        self.assertEqual(500, resp.status)
        self.assertEqual({'code': 'INTERNAL_ERROR', 'message': 'Error message.'}, json.loads(resp.body))
        