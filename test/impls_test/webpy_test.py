# -*- coding: utf-8 -*-
from StringIO import StringIO
from cgi import FieldStorage
from metaweb.impls.webpy import WebpyFileField
from testutil import TestCase

class WebpyFileFieldTest(TestCase):
    def test(self):
        field = FieldStorage()
        field.filename = 'aaa'
        field.file = StringIO('abc')
        field = WebpyFileField(field)
        self.assertEqual('aaa', field.filename)
        self.assertEqual(['abc'], list(field.chunks()))
        