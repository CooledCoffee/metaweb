# -*- coding: utf-8 -*-
from datetime import date, datetime, time
from metaweb.resps import RedirectResponse
from metaweb.views import Api, JsonEncoder
from testutil import TestCase
import json

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

@Api
def foo(a, b=2):
    pass

class TranslateResultTest(TestCase):
    def test_object(self):
        self.assertEqual('"aaa"', foo._translate_result('aaa').body)
        self.assertEqual('111', foo._translate_result(111).body)
        self.assertEqual('"2010-01-02"', foo._translate_result(date(2010, 1, 2)).body)
         
    def test_resp(self):
        result = RedirectResponse('/')
        resp = foo._translate_result(result)
        self.assertEqual(result, resp)
        