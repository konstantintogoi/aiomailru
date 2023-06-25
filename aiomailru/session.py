"""Sessions."""
import hashlib
import logging
from typing import Any, Dict

from httpx import AsyncClient

log = logging.getLogger(__name__)


class Session:
    """A wrapper for httpx.AsyncClient.

    Attributes:
        client (AsyncClient): async client with default base url and encoding

    """

    __slots__ = ('client',)

    def __init__(self) -> None:
        """Set base url and encoding."""
        self.client = AsyncClient(
            default_encoding='text/javascript; charset=utf-8',
            base_url='http://appsmail.ru',
            follow_redirects=True,
        )


class PublicSession(Session):
    """Session for public API methods of Platform@Mail.Ru."""

    async def request(self, params: Dict[str, Any],
    ) -> Dict[str, Any]:
        """Request public data.

        Args:
            params (Dict[str, Any]): query parameters

        Returns:
            Dict[str, Any]

        Raises:
            HTTPStatusError: if one occurred

        """
        try:
            resp = await self.client.get('platform/api', params=params)
        except Exception:
            log.error(f'GET {params["method"]} request failed')
            raise
        else:
            log.info(f'GET {resp.url} {resp.status_code}')

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

    __slots__ = ('app_id', 'session_key', 'secret', 'secure', 'uid')

    def __init__(
            self,
            app_id: str,
            session_key: str,
            secret: str,
            secure: str,
            uid: str,
        ) -> None:
        """Set credentials."""
        super().__init__()
        self.app_id = app_id
        self.session_key = session_key
        self.secret = secret
        self.secure = secure
        self.uid = uid

    def sign_params(self, params: Dict[str, Any]) -> str:
        """Sign query string according to signature circuit.

        See https://api.mail.ru/docs/guides/restapi/#sig.

        Args:
            params (Dict[str, Any]): query parameters

        Returns:
            str

        """
        query = ''.join(k + '=' + str(params[k]) for k in sorted(params))
        query = self.uid + query + self.secret
        sig = hashlib.md5(query.encode('UTF-8')).hexdigest()
        return sig

    async def request(self, params: Dict[str, Any]) -> Dict[str, Any]:  # noqa
        """Request data.

        Args:
            params (Dict[str, Any]): query parameters

        Returns:
            Dict[str, Any]

        """
        params = {k: params[k] for k in params if params[k]}
        params['session_key'] = self.session_key
        params['app_id'] = self.app_id
        params['secure'] = self.secure
        params.update({'sig': self.sign_params(params)})
        return await super().request(params)
