# -*- coding: UTF-8 -*-
from datetime import date, time, datetime
from decorated.base.context import Context
from json.encoder import JSONEncoder
from loggingd import log_enter, log_error
from metaweb import views
from metaweb.errors import WebError
from metaweb.resps import Response, NotFoundResponse
import doctest
import json
import logging

log = logging.getLogger(__name__)

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
    
def coor_maker(base_class=object, context_class=None):
    context_class_ = context_class or Context
    class _Coor(base_class):
        context_class = context_class_
        
        @log_enter('Handling url {path} ...')
        @log_error('Failed to handle url {path}.', exc_info=True)
        def render(self, path):
            try:
                path = _match_view(path)
            except Response as resp:
                return resp
            fields, headers, cookies = self._parse_request()
            request = {
                'cookies': cookies,
                'fields': fields,
                'headers': headers,
                'path': path,
            }
            try:
                with self.context_class(request=request):
                    result = path.view.render(request)
                    resp = _encode_result(result, headers) # need context
            except Response as resp:
                pass
            except Exception as e:
                log.warning('Failed to render.', exc_info=True)
                if not isinstance(e, WebError):
                    e = WebError(500, 'INTERNAL_ERROR', 'Server encountered an internal error.')
                resp = _encode_result(e, headers)
            return resp
        
        def _parse_request(self):
            fields = self._read_fields()
            headers = self._read_headers()
            cookies = self._read_cookies()
            for k, v in fields.items():
                log.debug('Field %s=%s' % (k, v))
            return fields, headers, cookies
            
        def _read_cookies(self):
            return {}

        def _read_fields(self):
            raise NotImplementedError()
        
        def _read_headers(self):
            return {}
    return _Coor

def _encode_result(resp, req_headers):
    '''
    >>> resp = _encode_result(Response(200, 'aaa'), {})
    >>> resp.body
    'aaa'
    
    >>> resp = _encode_result('aaa', {})
    >>> resp.status
    200
    >>> resp.body
    'aaa'
    >>> resp.headers['Content-Type']
    'text/html; charset=utf-8'
    
    >>> resp = _encode_result('aaa', {'Accept': 'application/json'})
    >>> resp.body
    '"aaa"'
    >>> resp.headers['Content-Type']
    'application/json'
    
    >>> resp = _encode_result(WebError(400, 'ERROR_CODE', 'Error message.'), {})
    >>> resp.status
    400
    >>> resp.body
    '[ERROR_CODE] Error message.'
    >>> resp.headers['Content-Type']
    'text/html; charset=utf-8'
    '''
    if isinstance(resp, Response):
        return resp
    else:
        status = resp.status if isinstance(resp, WebError) else 200
        accept = req_headers.get('Accept')
        if accept == 'application/json':
            body = json.dumps(resp, cls=JsonEncoder)
            ctype = 'application/json'
        else:
            body = unicode(resp).encode('utf-8')
            ctype = 'text/html; charset=utf-8'
        headers = {'Content-Type': ctype}
        return Response(status, body, headers=headers)

@log_error('View for {path} cannot be found.')
def _match_view(path):
    path = views.match(path)
    if path is None:
        raise NotFoundResponse()
    return path

if __name__ == '__main__':
    doctest.testmod()
    