"""Sessions."""
import hashlib
import logging
from enum import Enum
from typing import Any, Dict, Generator, Tuple

from httpx import AsyncClient, Response

log = logging.getLogger(__name__)


def full_scope() -> str:
    """Full scope."""
    return ' '.join(['photos', 'guestbook', 'stream', 'messages', 'events'])


class SignatureCircuit(Enum):
    """Signature circuit.

    .. _Подпись запроса
        https://api.mail.ru/docs/guides/restapi/#sig

    """

    UNDEFINED = 0
    CLIENT_SERVER = 1
    SERVER_SERVER = 2


class Session:
    """A wrapper for httpx.AsyncClient.

    Attributes:
        client (AsyncClient): async client with default base url and encoding
        raise_for_status (bool): whether to raise an exception when 2xx or 3xx

    """

    __slots__ = ('client', 'raise_for_status')

    def __init__(
        self,
        raise_for_status: bool = True,
        base_url: str = 'http://appsmail.ru/platform',
        default_encoding: str = 'text/javascript; charset=utf-8',
    ) -> None:
        """Set base url and encoding."""
        self.raise_for_status = raise_for_status
        self.client = AsyncClient(
            base_url=base_url,
            default_encoding=default_encoding,
            follow_redirects=True,
        )


class PublicSession(Session):
    """Session for public API methods of Platform@Mail.Ru."""

    async def __aenter__(self) -> 'PublicSession':
        """Enter."""
        return self

    async def __aexit__(self, *args: Tuple[Any, Any, Any]) -> None:
        """Exit."""
        await self.close()

    def __await__(self) -> Generator[Any, None, 'PublicSession']:
        """Make `PublicSession` awaitable."""
        yield self

    async def close(self) -> None:
        """Close."""
        if not self.client.is_closed:
            await self.client.aclose()

    async def request(
        self,
        path: str,
        params: Dict[str, Any],
    ) -> Dict[str, Any]:
        """Request public data.

        Args:
            path (str): path
            params (Dict[str, Any]): query parameters

        Returns:
            response (Dict[str, Any]): JSON response

        Raises:
            HTTPStatusError: if one occurred

        """
        try:
            resp: Response = await self.client.get(path, params=params)
        except Exception:
            log.error(f'GET {path} request failed')
            raise
        else:
            log.info(f'GET {resp.url} {resp.status_code}')

        if self.raise_for_status:
            resp.raise_for_status()

        try:
            return resp.json()
        except Exception:
            content = resp.read().decode()
            log.error(f'GET {resp.url} {resp.status_code} {content}')
            raise


class TokenSession(PublicSession):
    """Session for executing authorized requests.

    Attributes:
        app_id (str): client id
        private_key (str): private key
        secret_key (str): secret key
        session_key (str): access token
        uid (str): user id

    """

    __slots__ = ('app_id', 'private_key', 'secret_key', 'session_key', 'uid')

    def __init__(
            self,
            app_id: str,
            private_key: str,
            secret_key: str,
            access_token: str,
            uid: str,
            raise_for_status: bool = True,
        ) -> None:
        """Set credentials."""
        super().__init__(raise_for_status, 'http://appsmail.ru/platform/api')
        self.app_id = app_id
        self.private_key = private_key
        self.secret_key = secret_key
        self.session_key = access_token
        self.uid = uid

    async def __aenter__(self) -> 'TokenSession':
        """Enter."""
        return await self.authorize()

    def __await__(self) -> Generator[Any, None, 'TokenSession']:
        """Make `TokenSession` awaitable."""
        return self.authorize().__await__()

    async def authorize(self) -> 'TokenSession':
        """Authorize."""
        return self

    @property
    def sig_circuit(self) -> SignatureCircuit:
        """Signature circuit."""
        if self.uid and self.private_key and self.app_id:
            return SignatureCircuit.CLIENT_SERVER
        elif self.secret_key and self.app_id:
            return SignatureCircuit.SERVER_SERVER
        else:
            return SignatureCircuit.UNDEFINED

    @property
    def required_params(self) -> Dict[str, Any]:
        """Required parameters."""
        params = {'app_id': self.app_id, 'session_key': self.session_key}
        if self.sig_circuit is SignatureCircuit.SERVER_SERVER:
            params['secure'] = '1'
        return params

    def params2str(self, params: Dict[str, Any]) -> str:
        """Convert query parameters to string.

        Args:
            params (Dict[str, Any]): query parameters

        Returns:
            str

        """
        query = ''.join(k + '=' + str(params[k]) for k in sorted(params))

        if self.sig_circuit is SignatureCircuit.CLIENT_SERVER:
            return str(self.uid) + query + self.private_key
        elif self.sig_circuit is SignatureCircuit.SERVER_SERVER:
            return query + self.secret_key
        else:
            log.error((
                'Signature circuit undefined. '
                'Set "uid" and "private_key" for using client-server circuit. '
                'Set "secret_key" for using server-server circuit.'
            ))
            return query

    def sign_params(self, params: Dict[str, Any]) -> str:
        """Sign query string according to signature circuit.

        See https://api.mail.ru/docs/guides/restapi/#sig.

        Args:
            params (Dict[str, Any]): query parameters

        Returns:
            str

        """
        query = self.params2str(params)
        sig = hashlib.md5(query.encode('UTF-8')).hexdigest()
        return sig

    async def request(self, path: str, params: Dict[str, Any]) -> Dict[str, Any]:  # noqa
        """Request data.

        Args:
            path (str): path
            params (Dict[str, Any]): query parameters

        Returns:
            Dict[str, Any]

        """
        params = {k: params[k] for k in params if params[k]}
        params.update(self.required_params)
        params.update({'sig': self.sign_params(params)})
        return await super().request(path, params)


class ClientSession(TokenSession):
    """`TokenSession` with client-server signature circuit."""

    def __init__(
        self,
        app_id: str,
        private_key: str,
        access_token: str,
        uid: str,
        raise_for_status: bool = True,
    ) -> None:
        """Set attributes."""
        super().__init__(app_id, private_key, '', access_token, uid, raise_for_status)  # noqa


class ServerSession(TokenSession):
    """`TokenSession` with server-server signature circuit."""

    def __init__(
        self,
        app_id: str,
        secret_key: str,
        access_token: str,
        raise_for_status: bool = True,
    ) -> None:
        """Set attributes."""
        super().__init__(app_id, '', secret_key, access_token, '', raise_for_status)  # noqa


class CodeSession(TokenSession):
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

    __slots__ = ('code', 'redirect_uri', 'refresh_token', 'expires_in')

    def __init__(
        self,
        app_id: str,
        private_key: str,
        secret_key: str,
        code: str,
        redirect_uri: str,
        raise_for_status: bool = True,
    ) -> None:
        """Set attributes."""
        super().__init__(app_id, private_key, secret_key, '', '', raise_for_status)  # noqa
        self.code = code
        self.redirect_uri = redirect_uri
        self.refresh_token = ''
        self.expires_in = 0

    @property
    def params(self) -> Dict[str, str]:
        """Query parameters for authorization."""
        return {
            'client_id': self.app_id,
            'client_secret': self.secret_key,
            'grant_type': 'authorization_code',
            'redirect_uri': self.redirect_uri,
            'code': self.code,
        }

    async def authorize(self) -> 'CodeSession':
        """Authorize with OAuth 2.0 (Authorization Code).

        Returns:
            CodeSession

        """
        async with AsyncClient(follow_redirects=True, default_encoding='text/javascript; charset=utf-8') as cli:  # noqa
            resp = await cli.post('https://connect.mail.ru/oauth/token', data=self.params)  # noqa

            if self.raise_for_status:
                resp.raise_for_status()

            try:
                respjson: Dict[str, Any] = resp.json()
            except Exception:
                content = resp.read().decode()
                log.error(f'GET {resp.url} {resp.status_code}: {content}')
                raise

            self.refresh_token = respjson.get('refresh_token', '')
            self.expires_in = respjson.get('expires_in', '')
            self.session_key = respjson.get('access_token', '')
            self.uid = respjson.get('x_mailru_vid', '')

        return self


class CodeClientSession(CodeSession):
    """`CodeSession` with client-server signature circuit."""

    def __init__(
        self,
        app_id: str,
        private_key: str,
        code: str,
        redirect_uri: str,
        raise_for_status: bool = True,
    ):
        """Set attributes."""
        super().__init__(app_id, private_key, '', code, redirect_uri, raise_for_status)  # noqa


class CodeServerSession(CodeSession):
    """`CodeSession` with server-server signature circuit."""

    def __init__(
        self,
        app_id: str,
        secret_key: str,
        code: str,
        redirect_uri: str,
        raise_for_status: bool = True,
    ):
        """Set attributes."""
        super().__init__(app_id, '', secret_key, code, redirect_uri, raise_for_status)  # noqa


class PasswordSession(TokenSession):
    """Session with authorization with OAuth 2.0 (Password Grant).

    The Password grant type is a way to exchange a user's credentials
    for an access token.

    .. _OAuth 2.0 Password Grant
        https://oauth.net/2/grant-types/password/

    .. _Авторизация по логину и паролю
        https://api.mail.ru/docs/guides/oauth/client-credentials/

    """

    __slots__ = ('email', 'password', 'scope', 'refresh_token', 'expires_in')

    def __init__(
        self,
        app_id: str,
        private_key: str,
        secret_key: str,
        email: str,
        password: str,
        scope: str,
        raise_for_status: bool = True,
    ) -> None:
        """Set attributes."""
        super().__init__(app_id, private_key, secret_key, '', '', raise_for_status)  # noqa
        self.email = email
        self.password = password
        self.scope = scope or full_scope()
        self.refresh_token = ''
        self.expires_in = 0

    @property
    def params(self) -> Dict[str, str]:
        """Query parameters for authorization."""
        return {
            'grant_type': 'password',
            'client_id': self.app_id,
            'client_secret': self.secret_key,
            'username': self.email,
            'password': self.password,
            'scope': self.scope,
        }

    async def authorize(self) -> 'PasswordSession':
        """Authorize with OAuth 2.0 (Password Grant).

        Returns:
            PasswordSession

        """
        async with AsyncClient(follow_redirects=True, default_encoding='text/javascript; charset=utf-8') as cli:  # noqa
            resp = await cli.post('https://appsmail.ru/oauth/token', data=self.params)  # noqa

            if self.raise_for_status:
                resp.raise_for_status()

            try:
                respjson: Dict[str, Any] = resp.json()
            except Exception:
                log.error(f'GET {resp.url} {resp.read().decode()}')
                raise

            self.refresh_token = respjson.get('refresh_token', '')
            self.expires_in = respjson.get('expires_in', 0)
            self.session_key = respjson.get('access_token', '')
            self.uid = respjson.get('x_mailru_vid', '')

        return self


class PasswordClientSession(PasswordSession):
    """`PasswordSession` with client-server signature circuit."""

    def __init__(
        self,
        app_id: str,
        private_key: str,
        email: str,
        password: str,
        scope: str,
        raise_for_status: bool = True,
    ) -> None:
        """Set attributes."""
        super().__init__(app_id, private_key, '', email, password, scope, raise_for_status)  # noqa


class PasswordServerSession(PasswordSession):
    """`PasswordSession` with server-server signature circuit."""

    def __init__(
        self,
        app_id: str,
        secret_key: str,
        email: str,
        password: str,
        scope: str,
        raise_for_status: bool = True,
    ) -> None:
        """Set attributes."""
        super().__init__(app_id, '', secret_key, email, password, scope, raise_for_status)  # noqa


class RefreshSession(TokenSession):
    """Session with authorization with OAuth 2.0 (Refresh Token).

    The Refresh Token grant type is used by clients to exchange
    a refresh token for an access token when the access token has expired.

    .. _OAuth 2.0 Refresh Token
        https://oauth.net/2/grant-types/refresh-token/

    .. _Использование refresh_token
        https://api.mail.ru/docs/guides/oauth/client-credentials/#refresh_token

    """

    __slots__ = ('refresh_token', 'expires_in')

    def __init__(
        self,
        app_id: str,
        private_key: str,
        secret_key: str,
        refresh_token: str,
        raise_for_status: bool = True,
    ) -> None:
        """Set attributes."""
        super().__init__(app_id, private_key, secret_key, '', '', raise_for_status)  # noqa
        self.refresh_token = refresh_token
        self.expires_in = 0

    @property
    def params(self) -> Dict[str, str]:
        """Query parameters for authorization."""
        return {
            'grant_type': 'refresh_token',
            'client_id': self.app_id,
            'refresh_token': self.refresh_token,
            'client_secret': self.secret_key,
        }

    async def authorize(self) -> 'RefreshSession':
        """Authorize with OAuth 2.0 (Refresh Token).

        Returns:
            RefreshSession

        """
        async with AsyncClient(follow_redirects=True, default_encoding='text/javascript; charset=utf-8') as cli:  # noqa
            resp = await cli.post('https://appsmail.ru/oauth/token', data=self.params)  # noqa

            if self.raise_for_status:
                resp.raise_for_status()

            try:
                respjson: Dict[str, Any] = resp.json()
            except Exception:
                log.error(f'GET {resp.url} {resp.read().decode()}')
                raise

            self.refresh_token = respjson.get('refresh_token', '')
            self.expires_in = respjson.get('expires_in', 0)
            self.session_key = respjson.get('access_token', '')
            self.uid = respjson.get('x_mailru_vid', '')

        return self


class RefreshClientSession(RefreshSession):
    """`RefreshSession` with client-server signature circuit."""

    def __init__(
        self,
        app_id: str,
        private_key: str,
        refresh_token: str,
        raise_for_status: bool = True,
    ) -> None:
        """Set attributes."""
        super().__init__(app_id, private_key, '', refresh_token, raise_for_status)  # noqa


class RefreshServerSession(RefreshSession):
    """`RefreshSession` with server-server signature circuit."""

    def __init__(
        self,
        app_id: str,
        secret_key: str,
        refresh_token: str,
        raise_for_status: bool = True,
    ) -> None:
        """Set attributes."""
        super().__init__(app_id, '', secret_key, refresh_token, raise_for_status)  # noqa
