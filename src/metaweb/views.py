# -*- coding: UTF-8 -*-
from datetime import date, datetime, time
from decorated import Function
from decorated.base.function import ArgError
from decorated.util import modutil
from json.encoder import JSONEncoder
from metaweb.errors import WebError, ValidationError
from metaweb.files import FileField
from metaweb.resps import Response, RedirectResponse
import doctest
import json
import loggingd
import re

REGEX_PATH_PARAM = re.compile('<(.*?)(:.*?)?>')
log = loggingd.getLogger(__name__)
_pending_views = []
_abs_pathes = {}
_regex_pathes = {}

class View(Function):
    mimetype = None
    
    def bind(self, path):
        self.path = path
        if '<' in path and '>' in path:
            params = {}
            for name, type in REGEX_PATH_PARAM.findall(path):
                if type == '':
                    params[name] = {'type': unicode}
                else:
                    if type == ':int':
                        type = int
                    else:
                        raise Exception('Unknown type "%s" in path "%s".' % (type[1:], path))
                    params[name] = {'type': type}
            path = REGEX_PATH_PARAM.sub(lambda m: '(?P<%s>.*?)' % m.group(1), path)
            path = re.compile('^%s$' % path)
            _regex_pathes[path] = {'handler': self, 'params': params}
        else:
            _abs_pathes[path] = {'handler': self}
    
    def render(self, path_args, fields):
        try:
            fields = self._decode_fields(fields)
            args = path_args
            args.update(fields)
            try:
                args = self._resolve_args(**args)
            except ArgError as e:
                e = ValidationError(e.param, 'ARGUMENT_MISSING', str(e))
                resp = self._translate_error(e)
                raise resp
            result = self._call(**args)
            return self._translate_result(result)
        except Response as resp:
            return resp
        except Exception as e:
            log.warning('Failed to handle.', exc_info=True)
            return self._translate_error(e)
        
    def _decode_field(self, value):
        return value if isinstance(value, unicode) else value.decode('utf-8')
    
    def _decode_fields(self, fields):
        results = {}
        for k, v in fields.items():
            if k not in self.params:
                continue
            results[k] = v if isinstance(v, FileField) else self._decode_field(v)
        return results
    
    def _decorate(self, func):
        super(View, self)._decorate(func)
        _pending_views.append(self)
        return self
    
    def _init(self, path=None, mimetype=None):
        super(View, self)._init()
        self._specified_path = path
        if mimetype is not None:
            self.mimetype = mimetype
        
    def _translate_error(self, err):
        '''
        >>> resp = View()._translate_error(WebError(400, 'INVALID_ARGUMENT', 'Bad argument.'))
        >>> resp.status
        400
        >>> resp.body
        '[INVALID_ARGUMENT] Bad argument.'

        >>> resp = View()._translate_error(NotImplementedError('Method not implemented.'))
        >>> resp.status
        500
        >>> resp.body
        '[INTERNAL_ERROR] Method not implemented.'
        '''
        if not isinstance(err, WebError):
            err = WebError(500, 'INTERNAL_ERROR', str(err))
        return Response(err.status, str(err))
        
    def _translate_result(self, result):
        if isinstance(result, Response):
            return result
        else:
            headers = {}
            if self.mimetype is not None:
                headers['Content-Type'] = self.mimetype
            return Response(200, result, headers)
        
class Page(View):
    mimetype = 'text/html; charset=utf-8'
        
class Api(View):
    mimetype = 'application/json'
    
    def _decode_field(self, value):
        value = super(Api, self)._decode_field(value)
        return json.loads(value)
    
    def _translate_error(self, err):
        '''
        >>> resp = Api()._translate_error(WebError(400, 'INVALID_ARGUMENT', 'Bad argument.'))
        >>> resp.body
        '{"message": "Bad argument.", "code": "INVALID_ARGUMENT"}'
        >>> resp.status
        400
        
        >>> resp = Api()._translate_error(NotImplementedError('Method not implemented.'))
        >>> resp.status
        500
        >>> resp.body
        '{"message": "Method not implemented.", "code": "INTERNAL_ERROR"}'
        '''
        if not isinstance(err, WebError):
            err = WebError(500, 'INTERNAL_ERROR', str(err))
        body = json.dumps(err.__json__())
        return Response(err.status, body)
    
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
    _default.bind('/')
    
def load(roots=('views',)):
    if isinstance(roots, (list, tuple)):
        roots = {r: '' for r in roots}
    for root in roots:
        modutil.load_tree(root)
    for v in _pending_views:
        obj_path = _obj_to_path(v)
        path = _calc_path(roots, obj_path, v._specified_path)
        if path is not None:
            v.bind(path)
        
def match(path):
    view = _abs_pathes.get(path)
    if view is not None:
        return view['handler'], {}
    for pattern, view in _regex_pathes.items():
        match = pattern.match(path)
        if match is None:
            continue
        args = match.groupdict()
        args = {k: view['params'][k]['type'](v) for k, v in args.items()}
        return view['handler'], args
    return None, None

def _calc_path(roots, obj_path, specified_path):
    '''
    >>> _calc_path({'views': ''}, 'views.users.get', None)
    '/users/get'
    >>> _calc_path({'views': ''}, 'views.get', None)
    '/get'
    >>> _calc_path({'views': '', 'views2': ''}, 'views2.users.get', None)
    '/users/get'
    >>> _calc_path({'admin': '/admin'}, 'admin.users.get', None)
    '/admin/users/get'
    >>> _calc_path({'views': ''}, 'views2.users.get', None) is None
    True
    '''
    for package, prefix in roots.items():
        if obj_path.startswith(package + '.'):
            if specified_path is None:
                specified_path = obj_path[len(package):].replace('.', '/')
            return prefix + specified_path
    return None

def _obj_to_path(obj):
    '''
    >>> from metaweb.views import View
    >>> _obj_to_path(View)
    'metaweb.views.View'
    '''
    return obj.__module__ + '.' + obj.__name__

if __name__ == '__main__':
    doctest.testmod()
    