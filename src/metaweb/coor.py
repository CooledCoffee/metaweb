# -*- coding: UTF-8 -*-
from decorated.base.context import Context
from loggingd import log_enter, log_error
from metaweb import views
from metaweb.resps import Response, NotFoundResponse
import logging

log = logging.getLogger(__name__)

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
            for k, v in fields.items():
                log.debug('Field %s=%s' % (k, v))
            request = {
                'cookies': cookies,
                'fields': fields,
                'headers': headers,
                'path': path,
            }
            return path.view.render(request, self.context_class)
        
        def _parse_request(self):
            fields = self._read_fields()
            headers = self._read_headers()
            cookies = self._read_cookies()
            return fields, headers, cookies
            
        def _read_cookies(self):
            return {}

        def _read_fields(self):
            raise NotImplementedError()
        
        def _read_headers(self):
            return {}
    return _Coor

@log_error('View for {path} cannot be found.')
def _match_view(path):
    path = views.match(path)
    if path is None:
        raise NotFoundResponse()
    return path
