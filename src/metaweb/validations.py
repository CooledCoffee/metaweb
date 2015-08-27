# -*- coding: utf-8 -*-
from decorated.base.function import Function
from metaweb.errors import ValidationError
import doctest
import re

class Validator(Function):
    def _call(self, *args, **kw):
        value = self._evaluate_expression(self._param, *args, **kw)
        error = self._validate(value)
        if error is None:
            return super(Validator, self)._call(*args, **kw)
        else:
            raise ValidationError(self._code, param=self._param, message=error)
        
    def _init(self, param, code):
        super(Validator, self)._init()
        self._param = param
        self._code = code
        
    def _validate(self, value):
        raise NotImplementedError()

class Type(Validator):
    def _init(self, param, type_or_types, code='BAD_ARGUMENT_TYPE'):
        super(Type, self)._init(param, code)
        self._type_or_types = type_or_types
        
    def _validate(self, value):
        if not isinstance(value, self._type_or_types):
            return 'Value should be of type %s.' % (self._type_or_types,)
type = Type

class LengthRange(Type):
    def _init(self, param, lower, upper, code='BAD_ARGUMENT_LENGTH'):
        super(LengthRange, self)._init(param, basestring, code=code)
        self._lower = lower
        self._upper = upper
        
    def _validate(self, value):
        error = super(LengthRange, self)._validate(value)
        if error is not None:
            return error
        length = len(value)
        if length < self._lower or length > self._upper:
            return 'String length should be within [%s, %s].' % (self._lower, self._upper)
length_range = LengthRange

class Range(Type):
    def _init(self, param, lower, upper, code='ARGUMENT_OUT_OF_RANGE'):
        super(Range, self)._init(param, (int, float), code=code)
        self._lower = lower
        self._upper = upper
        
    def _validate(self, value):
        error = super(Range, self)._validate(value)
        if error is not None:
            return error
        if value < self._lower or value > self._upper:
            return 'Value should be within [%s, %s].' % (self._lower, self._upper)
range = Range

class Required(Validator):
    def _init(self, param, code='ARGUMENT_MISSING'):
        super(Required, self)._init(param, code)
        
    def _validate(self, value):
        if value is None or value == '':
            return 'Argument cannot be null.'
required = Required
    
class Regex(Type):
    def _init(self, param, pattern, code='BAD_ARGUMENT'):
        super(Regex, self)._init(param, code, basestring)
        self._pattern = re.compile(pattern)
        
    def _validate(self, value):
        if not self._pattern.match(value):
            return 'Value does not match "%s".' % self._pattern.pattern
regex = Regex

if __name__ == '__main__':
    doctest.testmod()
    