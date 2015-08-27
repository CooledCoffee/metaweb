# -*- coding: utf-8 -*-
from metaweb.validations import Validator, ValidationError, \
    Required, Range, LengthRange, Type, Regex
from fixtures2 import TestCase
import six

class ValidatorTest(TestCase):
    def test_success(self):
        # set up
        class TestValidator(Validator):
            def _validate(self, value):
                pass
        @TestValidator('key', 'ERROR')
        def foo(key):
            pass
        
        # test
        foo('aaa')
        
    def test_failed(self):
        # set up
        class TestValidator(Validator):
            def _validate(self, value):
                return 'error message'
        @TestValidator('key', 'ERROR')
        def foo(key):
            pass
        
        # test
        with self.assertRaises(ValidationError) as ctx:
            foo('aaa')
        self.assertEqual('key', ctx.exception._extras['param'])
        self.assertEqual('ERROR', ctx.exception.code)
        self.assertEqual('error message', ctx.exception.message)
        
class RequiredTest(TestCase):
    def test_string(self):
        @Required('key')
        def foo(key):
            pass
        foo('aaa')
        
    def test_number(self):
        @Required('key')
        def foo(key):
            pass
        foo(0)
        
    def test_none(self):
        @Required('key')
        def foo(key):
            pass
        with self.assertRaises(ValidationError):
            foo(None)
            
    def test_empty_string(self):
        @Required('key')
        def foo(key):
            pass
        with self.assertRaises(ValidationError):
            foo('')
        
class TypeValidator(TestCase):
    def test_success(self):
        @Type('key', six.string_types)
        def foo(key):
            pass
        foo('aaa')
        
    def test_failed(self):
        @Type('key', six.string_types)
        def foo(key):
            pass
        with self.assertRaises(ValidationError):
            foo(111)
            
    def test_none(self):
        @Type('key', six.string_types)
        def foo(key):
            pass
        with self.assertRaises(ValidationError):
            foo(None)
            
class RangeTest(TestCase):
    def test_success(self):
        @Range('value', 1, 10)
        def foo(value):
            pass
        foo(5)
        
    def test_too_small(self):
        @Range('value', 1, 10)
        def foo(value):
            pass
        with self.assertRaises(ValidationError):
            foo(0)
        
    def test_too_large(self):
        @Range('value', 1, 10)
        def foo(value):
            pass
        with self.assertRaises(ValidationError):
            foo(11)
        
    def test_not_number(self):
        @Range('value', 1, 10)
        def foo(value):
            pass
        with self.assertRaises(ValidationError):
            foo('aaa')
        
class LengthRangeTest(TestCase):
    def test_success(self):
        @LengthRange('value', 1, 10)
        def foo(value):
            pass
        foo('aaaaa')
        
    def test_too_short(self):
        @LengthRange('value', 1, 10)
        def foo(value):
            pass
        with self.assertRaises(ValidationError):
            foo('')
        
    def test_too_long(self):
        @LengthRange('value', 1, 10)
        def foo(value):
            pass
        with self.assertRaises(ValidationError):
            foo('aaaaaaaaaaa')
        
    def test_not_string(self):
        @LengthRange('value', 1, 10)
        def foo(value):
            pass
        with self.assertRaises(ValidationError):
            foo(1)
        
class RegexTest(TestCase):
    def test_success(self):
        @Regex('value', '\\d+')
        def foo(value):
            pass
        foo('123456')
        
    def test_failed(self):
        @Regex('value', '\\d+')
        def foo(value):
            pass
        with self.assertRaises(ValidationError):
            foo('')
        