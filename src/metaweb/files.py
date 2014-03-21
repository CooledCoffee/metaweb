# -*- coding: utf-8 -*-

CHUNK_SIZE = 4096

class FileField(object):
    def __init__(self, filename):
        self.filename = filename
        
    def chunks(self, size=CHUNK_SIZE):
        raise NotImplemented()
    
    def data(self):
        return ''.join(self.chunks())
    
    def save(self, path):
        with open(path, 'wb') as f:
            for chunk in self.chunks():
                f.write(chunk)
    