"""Exceptions."""


class Error(Exception):
    """Base exception."""

    ERROR = 'internal_error'

    @property
    def error(self):
        return self.args[0]

    def __init__(self, error: str or dict):
        arg = error if isinstance(error, dict) else {
            'error': self.ERROR,
            'error_description': error,
        }
        super().__init__(arg)


class OAuthError(Error):
    """OAuth error."""

    ERROR = 'oauth_error'


class APIError(Error):
    """API error."""

    def __init__(self, error: dict):
        super().__init__(error)
        self.code = error['error']['error_code']
        self.msg = error['error']['error_msg']

    def __str__(self):
        return 'Error {code}: {msg}'.format(code=self.code, msg=self.msg)
