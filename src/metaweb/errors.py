# -*- coding: utf-8 -*-
import doctest

class WebError(Exception):
    def __init__(self, status, code, message='', **extras):
        self.status = status
        self.code = code
        self.message = message
        self._extras = extras
        
    def __json__(self):
        '''
        >>> e = WebError(500, 'INTERNAL_ERROR', 'Error message.')
        >>> e.__json__()
        {'message': 'Error message.', 'code': 'INTERNAL_ERROR'}
        
        >>> e = WebError(500, 'INTERNAL_ERROR', 'Error message.', param='key')
        >>> e.__json__()
        {'message': 'Error message.', 'code': 'INTERNAL_ERROR', 'param': 'key'}
        '''
        result = {
            'code': self.code,
            'message': self.message,
        }
        result.update(self._extras)
        return result
        
    def __str__(self):
        '''
        >>> e = WebError(500, 'INTERNAL_ERROR', 'Error message.')
        >>> str(e)
        '[INTERNAL_ERROR] Error message.'
        '''
        return '[%s] %s' % (self.code, self.message)
    
class NotFoundError(WebError):
    def __init__(self, code='NOT_FOUND', message=''):
        super(NotFoundError, self).__init__(404, code, message=message)
        
class PermissionDeniedError(WebError):
    def __init__(self, code='PERMISSION_DENIED', message=''):
        super(PermissionDeniedError, self).__init__(403, code, message=message)
        
class ValidationError(WebError):
    def __init__(self, code, param=None, message=''):
        super(ValidationError, self).__init__(400, code, message=message, param=param)
        
    def __str__(self):
        '''
        >>> str(ValidationError('INVALID_ARGUMENT', param='key', message='Error message.'))
        '[INVALID_ARGUMENT] Error message. (param=key)'
        >>> str(ValidationError('INVALID_ARGUMENT', message='Error message.'))
        '[INVALID_ARGUMENT] Error message.'
        '''
        result = super(ValidationError, self).__str__()
        param = self._extras.get('param')
        if param is not None:
            result += ' (param=%s)' % param
        return result
    
if __name__ == '__main__':
    doctest.testmod()
    