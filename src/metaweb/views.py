# -*- coding: UTF-8 -*-
from decorated import Function
from metaweb import resps
from metaweb.files import FileField
from metaweb.resps import Response, RedirectResponse
import doctest
import json
import loggingd

log = loggingd.getLogger(__name__)
_views = {}

def get(path):
    return _views.get(path)

class View(Function):
    def handle(self, fields):
        try:
            fields = self._decode_fields(fields)
            result = self._call(**fields)
            return self._translate_result(result)
        except Response as resp:
            return resp
        except Exception as e:
            log.warning('Failed to handle.', exc_info=True)
            return Response(resps.STATUS_200, self._translate_error(e))
        
    def _decode_field(self, value):
        return value.decode('utf-8')
    
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
            raise Response(resps.STATUS_400, self._translate_error(e))
    
    def _decorate(self, func):
        super(View, self)._decorate(func)
        self.path = _calc_path(func.__module__, func.__name__)
        if self.path:
            _views[self.path] = self
        return self
    
    def _init(self, mimetype=None):
        super(View, self)._init()
        self._mimetype = mimetype
        
    def _translate_error(self, err):
        return '%s: %s' % (type(err).__name__, str(err))
        
    def _translate_result(self, result):
        if isinstance(result, Response):
            return result
        else:
            result = unicode(result)
            headers = {}
            if self._mimetype:
                headers['Content-Type'] = self._mimetype + '; charset=utf-8'
            return Response(resps.STATUS_200, result, headers)
        
class Page(View):
    def _create_default_handler(self):
        @View
        def _default():
            raise RedirectResponse(self.path)
        default_path = self.path[:self.path.rfind('/') + 1]
        _views[default_path] = _default
            
    def _decorate(self, func):
        super(Page, self)._decorate(func)
        if self.path and self._default:
            self._create_default_handler()
        return self
    
    def _init(self, default=False):
        super(Page, self)._init(mimetype='text/html')
        self._default = default
        
class Api(View):
    def _decode_field(self, value):
        value = super(Api, self)._decode_field(value)
        return json.loads(value)
            
    def _init(self):
        super(Api, self)._init(mimetype='application/json')
        
    def _translate_error(self, err):
        return json.dumps({'error': type(err).__name__, 'message': str(err)})
    
    def _translate_result(self, result):
        if isinstance(result, Response):
            return result
        else:
            result = json.dumps(result)
            return super(Api, self)._translate_result(result)
    
def add_default_view(url):
    @View
    def _default():
        raise RedirectResponse(url)
    _default.path = '/'
    _views['/'] = _default
    
def _calc_path(mod_name, func_name):
    '''
    >>> _calc_path('views.users', 'get')
    '/users/get'
    >>> _calc_path('views.users.root', 'get')
    '/users/get'
    >>> _calc_path('views.root', 'get')
    '/get'
    >>> _calc_path('views', 'get')
    '/get'
    '''
    if mod_name == 'views':
        return '/' + func_name
    if mod_name.startswith('views.'):
        dir_name = '/' + mod_name[len('views.'):].replace('.', '/')
        if dir_name.endswith('/root'):
            dir_name = dir_name[:-len('/root')]
        return dir_name + '/' + func_name
    return None

if __name__ == '__main__':
    doctest.testmod()
    