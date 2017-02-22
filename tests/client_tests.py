from __future__ import absolute_import
from __future__ import unicode_literals

import os
import subprocess
import time
import unittest

from nginx_upstream import client

TEST_BASE_URL = 'http://127.0.0.1:8080/upstream_conf'


class TestParser(unittest.TestCase):
    def setUp(self):
        self.current_dir = os.path.dirname(os.path.abspath(__file__))
        self.fixtures_dir = os.path.join(self.current_dir, 'fixtures')
        self.client = client.Client(TEST_BASE_URL)

        self.recreate_nginx()
        time.sleep(1)

    def recreate_nginx(self):
        subprocess.call(['docker-compose', 'up', '-d', '--force-recreate'], cwd=self.fixtures_dir)

    def test_fetch_upstream(self):
        upstreams = self.client.get_upstream('backend')
        self.assertIsNotNone(upstreams)

    def test_remove_server(self):
        retain_servers = self.client.remove_server('backend', id_=0)
        self.assertIsNotNone(retain_servers)

    def test_add_server(self):
        retain_servers = self.client.add_server('backend', '127.0.0.1:5800', backup=True)
        self.assertIsNotNone(retain_servers)
