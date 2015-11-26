# -*- coding: UTF-8 -*-
from decorated import Function
from decorated.base.function import ArgError
from decorated.util import modutil
from metaweb.errors import ValidationError
from metaweb.path import Path
from metaweb.resps import RedirectResponse
import doctest
import loggingd
import re

REGEX_PATH_PARAM = re.compile('<(.*?)(:.*?)?>')
log = loggingd.getLogger(__name__)
_pending_views = []
_abs_pathes = {}
_regex_pathes = {}

class View(Function):
    mimetype = 'application/octet-stream'
    
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
                self._path_params[name] = type
            path = REGEX_PATH_PARAM.sub(lambda m: '(?P<%s>.*?)' % m.group(1), path)
            path = re.compile('^%s$' % path)
            _regex_pathes[path] = self
        else:
            _abs_pathes[path] = self
    
    def render(self, request):
        args = self._parse_args(request['fields'], request['path'].args)
        args = self._resolve_args(**args)
        return self._call(**args)
        
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
                results[param] = fields[param]
            elif param in path_args:
                type = self._path_params[param]
                results[param] = type(path_args[param])
            elif param in defaults:
                results[param] = defaults[param]
            else:
                raise ValidationError('ARGUMENT_MISSING', param=param)
        return results
    
class Api(View):
    mimetype = 'application/json'
    
class Page(View):
    mimetype = 'text/html; charset=utf-8'
    
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
    