# -*- coding: utf-8 -*-
from fixtures._fixtures.tempdir import TempDir
from metaweb.files import FileField
from testutil import TestCase

class FakeFileField(FileField):
    def chunks(self):
        return ('a', 'b', 'c')
    
class FileFieldTest(TestCase):
    def test_filename(self):
        field = FileField('aaa')
        self.assertEqual('aaa', field.filename)
        
    def test_data(self):
        field = FakeFileField('aaa')
        self.assertEqual('abc', field.data())
        
    def test_save(self):
        # set up
        fixture = TempDir()
        self.useFixture(fixture)
        
        # test
        field = FakeFileField('aaa')
        path = fixture.join('file')
        field.save(path)
        
        # verify
        with open(path) as f:
            self.assertEqual('abc', f.read())
        