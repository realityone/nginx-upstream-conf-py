from __future__ import absolute_import
from __future__ import unicode_literals

import urllib

import requests
import requests.adapters

from . import (
    DEFAULT_TIMEOUT_SECONDS, DEFAULT_USER_AGENT, NginxUpstreamError,
    SERVER_PATTERN, Server
)


class Client(requests.Session):
    AVAILABLE_ARGS = {
        'server', 'backup', 'service', 'weight', 'max_conns',
        'max_fails', 'fail_timeout', 'slow_start', 'down',
        'drain', 'up', 'route', 'stream',
    }

    def __init__(self, base_url, timeout=DEFAULT_TIMEOUT_SECONDS,
                 tls=False, user_agent=DEFAULT_USER_AGENT):
        super(Client, self).__init__()

        if tls and not base_url.startswith('https://'):
            raise NginxUpstreamError(
                'If using TLS, the base_url must be starts with `https://`.'
            )

        self.base_url = base_url
        self.timeout = timeout
        self.headers['User-Agent'] = user_agent

    def _set_request_timeout(self, kwargs):
        """Prepare the kwargs for an HTTP request by inserting the timeout
        parameter, if not already present."""
        kwargs.setdefault('timeout', self.timeout)
        return kwargs

    def _get(self, url, **kwargs):
        return self.get(url, **self._set_request_timeout(kwargs))

    def _raise_for_status(self, response):
        """Raises stored :class:`APIError`, if one occurred."""
        try:
            response.raise_for_status()
        except requests.exceptions.HTTPError as e:
            raise NginxUpstreamError(e, response=response)

    def _result(self, response):
        self._raise_for_status(response)
        return response.text

    def send(self, request, **kwargs):
        request.url = request.url.replace(urllib.quote(':'), ':')
        return super(Client, self).send(request, **kwargs)

    @classmethod
    def parse_upstream(cls, upstream_content):
        """
        parse for
        ```
        server 111.13.101.208:80; # id=0
        server 220.181.57.217:80; # id=1
        server 123.125.114.144:80; # id=2
        server 180.149.132.47:80; # id=3
        ```
        """
        return [
            Server(*s.groups())
            for s in SERVER_PATTERN.finditer(upstream_content)
            ]

    @classmethod
    def prepare_request_args(cls, **kwargs):
        for k in cls.AVAILABLE_ARGS:
            kwargs[k] = kwargs.get(k)

        return {k: v for k, v in kwargs.items() if v is not None}

    def get_upstream(self, name, id_=None, stream=False):
        params = {
            'upstream': name,
        }
        if stream:
            params['stream'] = ''
        if id_ is not None:
            params['id'] = id_

        return self.parse_upstream(self._result(self._get(self.base_url, params=params)))

    def remove_server(self, name, id_):
        params = {
            'upstream': name,
            'id': id_,
            'remove': ''
        }

        return self.parse_upstream(self._result(self._get(self.base_url, params=params)))

    def update_server(self, name, id_, **kwargs):
        params = {
            'upstream': name,
            'id': id_,
        }
        params.update(self.prepare_request_args(**kwargs))

        return self.parse_upstream(self._result(self._get(self.base_url, params=params)))

    def add_server(self, name, server, **kwargs):
        params = {
            'upstream': name,
            'server': server,
            'add': ''
        }
        params.update(self.prepare_request_args(**kwargs))

        return self.parse_upstream(self._result(self._get(self.base_url, params=params)))
