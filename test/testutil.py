# -*- coding: utf-8 -*-
from fixtures._fixtures.monkeypatch import MonkeyPatch
from fixtures.testcase import TestWithFixtures

class TestCase(TestWithFixtures):
    def setUp(self):
        super(TestCase, self).setUp()
        self.useFixture(MonkeyPatch('metaweb.views._views', {}))
