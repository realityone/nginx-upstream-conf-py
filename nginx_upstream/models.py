from __future__ import absolute_import
from __future__ import unicode_literals

import collections


class Server(collections.namedtuple('_Server', ['ip_address', 'port', 'id'])):
    pass
