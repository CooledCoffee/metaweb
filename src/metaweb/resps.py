# -*- coding: UTF-8 -*-

STATUS_200 = '200 OK'
STATUS_301 = '301 Moved Permanently'
STATUS_302 = '302 Found'
STATUS_400 = '400 Bad Request'
STATUS_404 = '404 Not Found'
STATUS_500 = '500 Internal Server Error'

class Response(Exception):
    def __init__(self, code, body, headers=None, cookies=None):
        super(Response, self).__init__('')
        self.code = code
        self.body = body
        self.headers = headers or {}
        self.cookies = cookies or {}
        
class MovedResponse(Response):
    def __init__(self, url):
        headers = {'Location': url}
        super(MovedResponse, self).__init__(STATUS_301, '', headers)
        
class RedirectResponse(Response):
    def __init__(self, url):
        headers = {'Location': url}
        super(RedirectResponse, self).__init__(STATUS_302, '', headers)
    
class NotFoundResponse(Response):
    def __init__(self):
        super(NotFoundResponse, self).__init__(STATUS_404, '')
        