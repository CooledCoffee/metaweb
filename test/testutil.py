# -*- coding: utf-8 -*-
from fixtures2.case import TestCase
from fixtures2.patches import PatchesFixture

class TestCase(TestCase):
    def setUp(self):
        super(TestCase, self).setUp()
        self.patches = self.useFixture(PatchesFixture())
        self.patches.patch('metaweb.views._pending_views', [])
        self.patches.patch('metaweb.views._abs_pathes', {})
        self.patches.patch('metaweb.views._regex_pathes', {})
