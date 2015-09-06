# -*- coding: utf-8 -*-
from StringIO import StringIO
from cgi import FieldStorage
from decorated.base.context import Context
from decorated.base.dict import Dict
from metaweb.impls import webpy
from metaweb.impls.webpy import WebpyFileField
from testutil import TestCase
from web.utils import threadeddict

class WebpyFileFieldTest(TestCase):
    def test(self):
        field = FieldStorage()
        field.filename = 'aaa'
        field.file = StringIO('abc')
        field = WebpyFileField(field)
        self.assertEqual('aaa', field.filename)
        self.assertEqual(['abc'], list(field.chunks()))
        
class ReadFieldsTest(TestCase):
    def setUp(self):
        super(ReadFieldsTest, self).setUp()
        self.patches.patch('web.webapi.ctx', threadeddict())
        
    def test_get_empty(self):
        env = {
            'QUERY_STRING': '',
            'REQUEST_METHOD': 'GET',
        }
        self.patches.patch('web.webapi.ctx.env', env)
        coor = webpy._create_coor(Context)()
        fields = coor._read_fields()
        self.assertEqual(0, len(fields))
        
    def test_get_with_query_string(self):
        env = {
            'QUERY_STRING': 'a=0',
            'REQUEST_METHOD': 'GET',
        }
        self.patches.patch('web.webapi.ctx.env', env)
        coor = webpy._create_coor(Context)()
        fields = coor._read_fields()
        self.assertEqual(1, len(fields))
        self.assertEqual('0', fields['a'])
        
    def test_post_empty(self):
        env = {
            'QUERY_STRING': '',
            'REQUEST_METHOD': 'POST',
            'wsgi.input': StringIO(),
        }
        self.patches.patch('web.webapi.ctx.env', env)
        coor = webpy._create_coor(Context)()
        fields = coor._read_fields()
        self.assertEqual(0, len(fields))
        
    def test_post_www_form(self):
        data = 'a=1'
        env = {
            'CONTENT_LENGTH': len(data),
            'CONTENT_TYPE': 'application/x-www-form-urlencoded',
            'QUERY_STRING': '',
            'REQUEST_METHOD': 'POST',
            'wsgi.input': StringIO(data),
        }
        self.patches.patch('web.webapi.ctx.env', env)
        coor = webpy._create_coor(Context)()
        fields = coor._read_fields()
        self.assertEqual(1, len(fields))
        self.assertEqual('1', fields['a'])
        
    def test_post_multipart(self):
        data = '''--------------------------19dc7a5df0647b1a
Content-Disposition: form-data; name="a"

1
--------------------------19dc7a5df0647b1a--'''
        env = {
            'CONTENT_LENGTH': len(data),
            'CONTENT_TYPE': 'multipart/form-data; boundary=------------------------19dc7a5df0647b1a',
            'QUERY_STRING': '',
            'REQUEST_METHOD': 'POST',
            'wsgi.input': StringIO(data),
        }
        self.patches.patch('web.webapi.ctx.env', env)
        coor = webpy._create_coor(Context)()
        fields = coor._read_fields()
        self.assertEqual(1, len(fields))
        self.assertEqual('1', fields['a'])
        
    def test_post_json(self):
        data = '{"a": 1}'
        env = {
            'CONTENT_LENGTH': len(data),
            'CONTENT_TYPE': 'application/json',
            'QUERY_STRING': '',
            'REQUEST_METHOD': 'POST',
            'wsgi.input': StringIO(data),
        }
        self.patches.patch('web.webapi.ctx.env', env)
        coor = webpy._create_coor(Context)()
        fields = coor._read_fields()
        self.assertEqual(1, len(fields))
        self.assertEqual(1, fields['a'])
        