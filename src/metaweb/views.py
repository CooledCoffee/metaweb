# -*- coding: UTF-8 -*-
from datetime import date, datetime, time
from decorated import Function
from decorated.base.function import ArgError
from decorated.util import modutil
from json.encoder import JSONEncoder
from metaweb.errors import WebError, ValidationError
from metaweb.files import FileField
from metaweb.path import Path
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
            for name, type in REGEX_PATH_PARAM.findall(path):
                if type == '':
                    type = unicode
                elif type == ':int':
                    type = int
                else:
                    raise Exception('Unknown type "%s" in path "%s".' % (type[1:], path))
                self._path_params[name] = {'type': type}
            path = REGEX_PATH_PARAM.sub(lambda m: '(?P<%s>.*?)' % m.group(1), path)
            path = re.compile('^%s$' % path)
            _regex_pathes[path] = self
        else:
            _abs_pathes[path] = self
    
    def render(self, request, context_class):
        try:
            with context_class(request=request):
                args = self._parse_args(request['fields'], request['path'].args)
                args = self._resolve_args(**args)
                result = self._call(**args)
                return self._translate_result(result)
        except Response as resp:
            return resp
        except Exception as e:
            log.warning('Failed to handle.', exc_info=True)
            return self._translate_error(e)
        
    def _decode_field(self, value):
        return value if isinstance(value, unicode) else value.decode('utf-8')
    
    def _decorate(self, func):
        super(View, self)._decorate(func)
        _pending_views.append(self)
        return self
    
    def _init(self, path=None, mimetype=None):
        super(View, self)._init()
        self._specified_path = path
        if mimetype is not None:
            self.mimetype = mimetype
        self._path_params = {}
        
    def _parse_args(self, fields, path_args):
        results = {}
        defaults = dict(self.optional_params)
        for param in self.params:
            if param in fields:
                results[param] = self._decode_field(fields[param])
            elif param in path_args:
                type = self._path_params[param]
                results[param] = type(path_args[param])
            elif param in defaults:
                results[param] = defaults[param]
            else:
                raise ValidationError(param, 'ARGUMENT_MISSING')
        return results
    
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
        '[INTERNAL_ERROR] Server encountered an internal error.'
        '''
        if not isinstance(err, WebError):
            err = WebError(500, 'INTERNAL_ERROR', 'Server encountered an internal error.')
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
        '{"message": "Server encountered an internal error.", "code": "INTERNAL_ERROR"}'
        '''
        if not isinstance(err, WebError):
            err = WebError(500, 'INTERNAL_ERROR', 'Server encountered an internal error.')
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
        path = Path(path)
        path.view = view
        return path
    for pattern, view in _regex_pathes.items():
        match = pattern.match(path)
        if match is None:
            continue
        args = match.groupdict()
        path = Path(path)
        path.view = view
        path.args = args
        return path
    return None

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
    