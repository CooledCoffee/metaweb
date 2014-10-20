# -*- coding: UTF-8 -*-
from datetime import date, datetime, time
from decorated import Function
from decorated.util import modutil
from json.encoder import JSONEncoder
from metaweb.files import FileField
from metaweb.resps import Response, RedirectResponse
import doctest
import inflection
import json
import loggingd

log = loggingd.getLogger(__name__)
_pending_views = []
_views = {}

class View(Function):
    mime = None
    
    def bind(self, path):
        self.path = path
        _views[path] = self
    
    def render(self, fields):
        try:
            fields = self._decode_fields(fields)
            result = self._call(**fields)
            return self._translate_result(result)
        except Response as resp:
            return resp
        except Exception as e:
            log.warning('Failed to handle.', exc_info=True)
            return Response(200, self._translate_error(e))
        
    def _decode_field(self, value):
        return value if isinstance(value, unicode) else value.decode('utf-8')
    
    def _decode_fields(self, fields):
        try:
            for k, v in fields.items():
                if k not in self.params:
                    continue
                if isinstance(v, FileField):
                    continue
                fields[k] = self._decode_field(v)
            return self._resolve_args(**fields)
        except Exception as e:
            raise Response(400, self._translate_error(e))
    
    def _decorate(self, func):
        super(View, self)._decorate(func)
        _pending_views.append(self)
        return self
        
    def _translate_error(self, err):
        code = _translate_error_code(err)
        return '%s: %s' % (code, str(err))
        
    def _translate_result(self, result):
        if isinstance(result, Response):
            return result
        else:
            result = unicode(result)
            headers = {}
            if self.mime:
                headers['Content-Type'] = self.mime + '; charset=utf-8'
            return Response(200, result, headers)
        
class Page(View):
    mime = 'text/html'
        
class Api(View):
    mime = 'application/json'
    
    def _decode_field(self, value):
        value = super(Api, self)._decode_field(value)
        return json.loads(value)
            
    def _translate_error(self, err):
        code = _translate_error_code(err)
        return json.dumps({'error': code, 'message': str(err)})
    
    def _translate_result(self, result):
        if isinstance(result, Response):
            return result
        else:
            result = json.dumps(result, cls=JsonEncoder)
            return super(Api, self)._translate_result(result)
    
class JsonEncoder(JSONEncoder):
    def default(self, obj):
        if hasattr(obj, '__json__'):
            return getattr(obj, '__json__')()
        elif isinstance(obj, datetime):
            return obj.strftime('%Y-%m-%d %H:%M:%S')
        elif isinstance(obj, date):
            return obj.strftime('%Y-%m-%d')
        elif isinstance(obj, time):
            return obj.strftime('%H:%M:%S')
        else:
            return obj
    
def add_default_view(url):
    @View
    def _default():
        raise RedirectResponse(url)
    _default.path = '/'
    _views['/'] = _default
    
def get(path):
    return _views.get(path)

def load(roots=('views',)):
    for root in roots:
        modutil.load_tree(root)
    for v in _pending_views:
        path = _obj_to_path(v)
        for root in roots:
            if path.startswith(root + '.'):
                path = _calc_path(path, root)
                v.bind(path)
        
def _calc_path(path, root):
    '''
    >>> _calc_path('views.users.get', 'views')
    '/users/get'
    >>> _calc_path('views.users.root.get', 'views')
    '/users/get'
    >>> _calc_path('views.root.get', 'views')
    '/get'
    >>> _calc_path('views.get', 'views')
    '/get'
    >>> _calc_path('views.users.root', 'views')
    '/users/'
    >>> _calc_path('views.root', 'views')
    '/'
    '''
    path = path[len(root) + 1:]
    ss = path.split('.')
    path = '/' + '/'.join([s for s in ss if s != 'root'])
    if ss[-1] == 'root':
        path += '/'
    return path.replace('//', '/')

def _obj_to_path(obj):
    '''
    >>> from metaweb.views import View
    >>> _obj_to_path(View)
    'metaweb.views.View'
    '''
    return obj.__module__ + '.' + obj.__name__

def _translate_error_code(e):
    '''
    >>> _translate_error_code(AttributeError())
    'ATTRIBUTE_ERROR'
    >>> _translate_error_code(EOFError())
    'EOF_ERROR'
    >>> class MyEOFError(EOFError): pass
    >>> _translate_error_code(MyEOFError())
    'MY_EOF_ERROR'
    '''
    code = type(e).__name__
    code = inflection.underscore(code)
    return code.upper()

if __name__ == '__main__':
    doctest.testmod()
    