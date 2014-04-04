# -*- coding: utf-8 -*-
from __future__ import absolute_import
from decorated.util import modutil
from metaweb import coor, views

if modutil.module_exists('webapp2'):
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
                self.response.headers[k] = v
            self.response.out.write(resp.body)
            
        def _read_fields(self):
            fields = dict(self.request.GET)
            fields.update(self.request.POST)
            return fields
        
        def _read_headers(self):
            return self.request.headers
        
    def start(default_url=None):
        modutil.load_tree('views')
        if default_url is not None:
            views.add_default_view(default_url)
        return WSGIApplication([('(.*)', GaeCoor)], debug=False)
    