# -*- coding: utf-8 -*-
from cgi import FieldStorage
from decorated.util import modutil
import json

if modutil.module_exists('web'):
    from metaweb import files, coor, views
    from metaweb.files import FileField
    from web import webapi
    import web
    
    class WebpyFileField(FileField):
        def __init__(self, storage):
            super(WebpyFileField, self).__init__(storage.filename)
            self._file = storage.file
            
        def chunks(self, size=files.CHUNK_SIZE):
            while True:
                chunk = self._file.read(size)
                if len(chunk):
                    yield chunk
                else:
                    break
                
    def run(cls=None, context_class=None, default_url=None, roots=('views',)):
        cls = cls or _create_coor(context_class=context_class)
        app = _create_app(cls, default_url, roots)
        app.run()
        
    def wsgi(cls=None, context_class=None, default_url=None, roots=('views',)):
        cls = cls or _create_coor(context_class=context_class)
        app = _create_app(cls, default_url, roots)
        return app.wsgifunc()
        
    def _create_app(cls, default_url, roots):
        views.load(roots=roots)
        if default_url is not None:
            views.add_default_view(default_url)
        mapping = ('(.+)', cls)
        web.config.debug = False
        return web.application(mapping)
        
    def _create_coor(context_class):
        class _Coor(coor.coor_maker(context_class=context_class)):
            def GET(self, path):
                resp = self.render(path)
                return self._process_resp(resp)
        
            def POST(self, path):
                resp = self.render(path)
                return self._process_resp(resp)
            
            def _read_cookies(self):
                return web.cookies()
            
            def _read_fields(self):
                env = webapi.ctx.env
                json_fields = {}
                method = env.get('REQUEST_METHOD', '').upper()
                ctype = env.get('CONTENT_TYPE', '').lower()
                if method == 'POST' and ctype.startswith('application/json'):
                    data = env['wsgi.input'].read().decode('utf-8')
                    json_fields = json.loads(data)
                fields = webapi.rawinput(method='both')
                results = {k: v[-1] if isinstance(v, list) else v for k, v in fields.items()}
                results = {k: v if isinstance(v, FieldStorage) else v.decode('utf-8') for k, v in results.items()}
                results.update(json_fields)
                return results
            
            def _read_headers(self):
                def _normalize_key(key):
                    key = key[len('HTTP_'):]
                    ss = key.split('_')
                    ss = [s.capitalize() for s in ss]
                    return '-'.join(ss)
                return {_normalize_key(k): v \
                        for k, v in web.ctx.env.items() \
                        if k.startswith('HTTP_')}
            
            def _process_resp(self, resp):
                web.ctx.status = resp.status_string()
                for k, v in resp.headers.items():
                    web.header(k, str(v))
                return resp.body
        return _Coor
