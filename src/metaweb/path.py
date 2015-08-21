# -*- coding: utf-8 -*-
import doctest

class Path(str):
    def __init__(self, path):
        '''
        >>> path = Path('/test')
        >>> path
        '/test'
        >>> path.args
        {}
        '''
        super(Path, self).__init__(path)
        self.args = {}
        self.view = None
    
if __name__ == '__main__':
    doctest.testmod()
    