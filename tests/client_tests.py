from __future__ import absolute_import
from __future__ import unicode_literals

import unittest

from nginx_upstream import client

TEST_BASE_URL = 'http://127.0.0.1:8080/upstream_conf'


class TestParser(unittest.TestCase):
    def setUp(self):
        self.client = client.Client(TEST_BASE_URL)

    def test_fetch_upstream(self):
        upstreams = self.client.get_upstream('backend')
        self.assertIsNotNone(upstreams)
