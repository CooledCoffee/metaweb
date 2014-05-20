# -*- coding: UTF-8 -*-
from decorated.base.context import Context
from loggingd import log_enter, log_error
from metaweb import views
from metaweb.resps import Response, MovedResponse, NotFoundResponse
import logging

log = logging.getLogger(__name__)

def coor_maker(base_class=object):
    class _Coor(base_class):
        context_class = Context
        
        @log_enter('Handling url {path} ...')
        @log_error('Failed to handle url {path}.', exc_info=True)
        def render(self, path):
            try:
                view = _get_view(path)
            except Response as resp:
                return resp
            fields, headers, cookies = self._parse_request()
            for k, v in fields.items():
                log.debug('Field %s=%s' % (k, v))
            with self._build_context(path, fields, headers, cookies):
                return view.render(fields)
            
        def _build_context(self, path, fields, headers, cookies):
            ctx = self.context_class()
            ctx.path = path
            ctx.headers = headers
            ctx.cookies = cookies
            return ctx
        
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

@log_error('Handler for {path} cannot be found.')
def _get_view(path):
    view = views.get(path)
    if view:
        return view
    if views.get(path + '/'):
        raise MovedResponse(path + '/')
    raise NotFoundResponse()
