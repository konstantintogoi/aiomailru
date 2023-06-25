"""Authurization."""
import logging
from typing import Any, Dict, Tuple

from httpx import AsyncClient

log = logging.getLogger(__name__)


def full_scope() -> str:
    """Full scope."""
    return ' '.join(['photos', 'guestbook', 'stream', 'messages', 'events'])


class Grant:
    """Authorization Grant."""

    __slots__ = ('_app_id', '_auth_client')

    def __init__(self, app_id: str) -> None:
        """Set app info."""
        self._app_id = app_id
        self._auth_client = AsyncClient(
            default_encoding='application/x-www-formurlencoded',
            follow_redirects=True,
        )

    async def __aenter__(self) -> 'Grant':
        """Enter."""
        await self.authorize()
        if not self._auth_client.is_closed:
            await self._auth_client.aclose()
        return self

    async def __aexit__(self, *args: Tuple[Any, Any, Any]) -> None:
        """Exit."""
        if not self._auth_client.is_closed:
            await self._auth_client.aclose()

    async def authorize(self) -> 'Grant':
        """Authorizate."""
        return self


class CodeGrant(Grant):
    """Session with authorization with OAuth 2.0 (Authorization Code Grant).

    The Authorization Code grant is used by confidential and public
    clients to exchange an authorization code for an access token.

    .. _OAuth 2.0 Authorization Code Grant
        https://oauth.net/2/grant-types/authorization-code/

    .. _Авторизация для сайтов
        https://api.mail.ru/docs/guides/oauth/sites/

    .. _Авторизация для мобильных сайтов
        https://api.mail.ru/docs/guides/oauth/mobile-web/

    """

    __slots__ = (
        '_code',
        '_secret_key',
        '_redirect_uri',
        'refresh_token',
        'session_key',
        'expires_in',
        'uid',
    )

    def __init__(
        self,
        app_id: str,
        redirect_uri: str,
        secret_key: str,
        code: str,
    ) -> None:
        """Set attributes."""
        super().__init__(app_id)
        self._redirect_uri = redirect_uri
        self._secret_key = secret_key
        self._code = code

    async def authorize(self) -> 'CodeGrant':
        """Authorize with OAuth 2.0 (Authorization Code).

        Returns:
            CodeGrant

        """
        resp = await self._auth_client.post(
            'https://connect.mail.ru/oauth/token',
            data={
                'client_id': self._app_id,
                'client_secret': self._secret_key,
                'grant_type': 'authorization_code',
                'redirect_uri': self._redirect_uri,
                'code': self._code,
            },
        )
        resp.raise_for_status()

        try:
            respjson: Dict[str, Any] = resp.json()
        except Exception:
            content = resp.read().decode()
            log.error(f'GET {resp.url} {resp.status_code}: {content}')
            raise

        try:
            self.session_key = respjson['access_token']
            self.refresh_token = respjson['refresh_token']
            self.expires_in = respjson['expires_in']
            self.uid = respjson['x_mailru_vid']
        except KeyError as e:
            raise KeyError(*e.args, respjson) from e

        return self


class PasswordGrant(Grant):
    """Session with authorization with OAuth 2.0 (Password Grant).

    The Password grant type is a way to exchange a user's credentials
    for an access token.

    .. _OAuth 2.0 Password Grant
        https://oauth.net/2/grant-types/password/

    .. _Авторизация по логину и паролю
        https://api.mail.ru/docs/guides/oauth/client-credentials/

    """

    __slots__ = (
        '_email',
        '_password',
        '_secret_key',
        '_scope',
        'session_key',
        'refresh_token',
        'expires_in',
        'uid',
    )

    def __init__(
        self,
        app_id: str,
        username: str,
        password: str,
        secret_key: str,
        scope: str,
    ) -> None:
        """Set attributes."""
        super().__init__(app_id)
        self._secret_key = secret_key
        self._username = username
        self._password = password
        self._scope = scope

    async def authorize(self) -> 'PasswordGrant':
        """Authorize with OAuth 2.0 (Password Grant).

        Returns:
            PasswordGrant

        """
        resp = await self._auth_client.post(
            'https://appsmail.ru/oauth/token',
            data={
                'grant_type': 'password',
                'client_id': self._app_id,
                'client_secret': self._secret_key,
                'username': self._username,
                'password': self._password,
                'scope': self._scope,
            },
        )

        resp.raise_for_status()

        try:
            respjson: Dict[str, Any] = resp.json()
        except Exception:
            log.error(f'GET {resp.url} {resp.read().decode()}')
            raise

        try:
            self.session_key = respjson['access_token']
            self.refresh_token = respjson['refresh_token']
            self.expires_in = respjson['expires_in']
            self.uid = respjson['x_mailru_vid']
        except KeyError as e:
            raise KeyError(*e.args, respjson) from e

        return self


class RefreshGrant(Grant):
    """Session with authorization with OAuth 2.0 (Refresh Token).

    The Refresh Token grant type is used by clients to exchange
    a refresh token for an access token when the access token has expired.

    .. _OAuth 2.0 Refresh Token
        https://oauth.net/2/grant-types/refresh-token/

    .. _Использование refresh_token
        https://api.mail.ru/docs/guides/oauth/client-credentials/#refresh_token

    """

    __slots__ = (
        '_secret_key',
        '_refresh_token',
        'refresh_token',
        'session_key',
        'expires_in',
        'uid',
    )

    def __init__(
        self,
        app_id: str,
        secret_key: str,
        refresh_token: str,
    ) -> None:
        """Set attributes."""
        super().__init__(app_id)
        self._refresh_token = refresh_token
        self._secret_key = secret_key

    async def authorize(self) -> 'RefreshGrant':
        """Authorize with OAuth 2.0 (Refresh Token).

        Returns:
            RefreshGrant

        """
        resp = await self._auth_client.post(
            'https://appsmail.ru/oauth/token',
            data={
                'client_id': self._app_id,
                'grant_type': 'refresh_token',
                'refresh_token': self._refresh_token,
                'client_secret': self._secret_key,
            },
        )

        resp.raise_for_status()

        try:
            respjson: Dict[str, Any] = resp.json()
        except Exception:
            log.error(f'GET {resp.url} {resp.read().decode()}')
            raise

        try:
            self.session_key = respjson['access_token']
            self.refresh_token = respjson['refresh_token']
            self.expires_in = respjson['expires_in']
            self.uid = respjson['x_mailru_vid']
        except KeyError as e:
            raise KeyError(*e.args, respjson) from e

        return self
