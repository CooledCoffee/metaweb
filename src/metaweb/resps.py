# -*- coding: UTF-8 -*-
import doctest
import httplib

class Response(Exception):
    def __init__(self, code, body, headers=None, cookies=None):
        super(Response, self).__init__('')
        self.code = code
        self.body = body
        self.headers = headers or {}
        self.cookies = cookies or {}
        
    def status(self):
        '''
        >>> Response(200, '').status()
        '200 OK'
        >>> Response(404, '').status()
        '404 Not Found'
        '''
        message = httplib.responses[self.code]
        return '%d %s' % (self.code, message)
        
class MovedResponse(Response):
    def __init__(self, url):
        headers = {'Location': url}
        super(MovedResponse, self).__init__(301, '', headers)
        
class RedirectResponse(Response):
    def __init__(self, url):
        headers = {'Location': url}
        super(RedirectResponse, self).__init__(302, '', headers)
    
class NotFoundResponse(Response):
    def __init__(self):
        super(NotFoundResponse, self).__init__(404, '')
        
if __name__ == '__main__':
    doctest.testmod()
    