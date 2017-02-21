from __future__ import absolute_import
from __future__ import unicode_literals

import requests

from . import (
    DEFAULT_TIMEOUT_SECONDS, DEFAULT_USER_AGENT, NginxUpstreamError,
    SERVER_PATTERN
)
from . import models


class Client(requests.Session):
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
            models.Server(*s.groups())
            for s in SERVER_PATTERN.finditer(upstream_content)
            ]

    def get_upstream(self, name, is_stream=False, id_=None):
        params = {
            'upstream': name,
        }
        if is_stream:
            params['stream'] = ''
        if id_ is not None:
            params['id'] = id_

        return self.parse_upstream(self._result(self._get(self.base_url, params=params)))
