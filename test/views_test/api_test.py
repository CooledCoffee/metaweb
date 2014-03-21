# -*- coding: utf-8 -*-
from metaweb.resps import RedirectResponse
from metaweb.views import Api
from testutil import TestCase

@Api
def foo(a, b=2):
    pass

class TranslateResultTest(TestCase):
    def test_object(self):
        self.assertEqual('"aaa"', foo._translate_result('aaa').body)
        self.assertEqual('111', foo._translate_result(111).body)
         
    def test_resp(self):
        result = RedirectResponse('/')
        resp = foo._translate_result(result)
        self.assertEqual(result, resp)
        