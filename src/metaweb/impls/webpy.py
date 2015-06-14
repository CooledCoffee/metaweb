# -*- coding: utf-8 -*-
from decorated.util import modutil

if modutil.module_exists('web'):
    from cgi import FieldStorage
    from metaweb import files, coor, views
    from metaweb.files import FileField
    from web import webapi, utils
    from web.webapi import BadRequest
    import web
    
    class WebPyCoor(coor.coor_maker()):
        def GET(self, path):
            resp = self.render(path)
            return self._process_resp(resp)
    
        def POST(self, path):
            resp = self.render(path)
            return self._process_resp(resp)
        
        def _read_fields(self):
            fields = webapi.rawinput('both')
            try:
                defaults = {k: {} for k in fields}
                fields = utils.storify(fields, _unicode=True, **defaults)
                for k, v in fields.items():
                    if isinstance(v, FieldStorage):
                        fields[k] = WebpyFileField(v)
                return fields
            except KeyError:
                raise BadRequest()
        
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
            web.ctx.status = resp.status()
            for k, v in resp.headers.items():
                web.header(k, str(v))
            return resp.body
        
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
                
    def run(cls=WebPyCoor, default_url=None, roots=('views',)):
        app = _create_app(cls, default_url, roots)
        app.run()
        
    def wsgi(cls=WebPyCoor, default_url=None, roots=('views',)):
        app = _create_app(cls, default_url, roots)
        return app.wsgifunc()
        
    def _create_app(cls, default_url, roots):
        views.load(roots=roots)
        if default_url is not None:
            views.add_default_view(default_url)
        mapping = ('(.+)', cls)
        web.config.debug = False
        return web.application(mapping)
        