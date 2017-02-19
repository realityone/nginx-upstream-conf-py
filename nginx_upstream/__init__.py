from __future__ import absolute_import
from __future__ import unicode_literals

import re

import requests.exceptions

version = '0.1'

DEFAULT_TIMEOUT_SECONDS = 60
DEFAULT_NUM_POOLS = 25
DEFAULT_USER_AGENT = 'nginx-upstream-conf-python/{0}'.format(version)

SERVER_PATTERN = re.compile(r'server (?P<ip_address>\d+.\d+.\d+.\d+):(?P<port>\d+); # id=(?P<id>\d+)')


class NginxUpstreamError(requests.exceptions.HTTPError):
    """
    An HTTP error from the API.
    """

    def __init__(self, message, response=None, explanation=None):
        # requests 1.2 supports response as a keyword argument, but
        # requests 1.1 doesn't
        super(NginxUpstreamError, self).__init__(message)
        self.response = response
        self.explanation = explanation

    def __str__(self):
        message = super(NginxUpstreamError, self).__str__()

        if self.is_client_error():
            message = '{0} Client Error: {1}'.format(
                self.response.status_code, self.response.reason)

        elif self.is_server_error():
            message = '{0} Server Error: {1}'.format(
                self.response.status_code, self.response.reason)

        if self.explanation:
            message = '{0} ("{1}")'.format(message, self.explanation)

        return message

    @property
    def status_code(self):
        if self.response:
            return self.response.status_code

    def is_client_error(self):
        if self.status_code is None:
            return False
        return 400 <= self.status_code < 500

    def is_server_error(self):
        if self.status_code is None:
            return False
        return 500 <= self.status_code < 600
