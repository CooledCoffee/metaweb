# -*- coding: utf-8 -*-
from __future__ import absolute_import
from decorated.util import modutil

if modutil.module_exists('webapp2'):
    from metaweb import coor, views
    from webapp2 import RequestHandler, WSGIApplication
    
    class GaeCoor(coor.coor_maker(RequestHandler)):
        def get(self, path):
            resp = self.render(path)
            self._process_resp(resp)
            
        def post(self, path):
            resp = self.render(path)
            self._process_resp(resp)
            
        def _process_resp(self, resp):
            self.response.set_status(resp.status())
            for k, v in resp.headers.items():
                self.response.headers[k] = str(v)
            self.response.out.write(resp.body)
            
        def _read_fields(self):
            fields = dict(self.request.GET)
            fields.update(self.request.POST)
            return fields
        
        def _read_headers(self):
            return self.request.headers
        
    def wsgi(default_url=None, roots=('views',)):
        views.load(roots=roots)
        if default_url is not None:
            views.add_default_view(default_url)
        return WSGIApplication([('(.*)', GaeCoor)], debug=False)
