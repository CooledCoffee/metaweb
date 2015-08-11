# -*- coding: utf-8 -*-
import doctest

class WebError(Exception):
    def __init__(self, status, code, message):
        self.status = status
        self.code = code
        self.message = message
        
    def __json__(self):
        '''
        >>> e = WebError(500, 'INTERNAL_ERROR', 'Error message.')
        >>> e.__json__()
        {'message': 'Error message.', 'code': 'INTERNAL_ERROR'}
        '''
        return {
            'code': self.code,
            'message': self.message,
        }
        
    def __str__(self):
        '''
        >>> e = WebError(500, 'INTERNAL_ERROR', 'Error message.')
        >>> str(e)
        '[INTERNAL_ERROR] Error message.'
        '''
        return '[%s] %s' % (self.code, self.message)
    
if __name__ == '__main__':
    doctest.testmod()
    