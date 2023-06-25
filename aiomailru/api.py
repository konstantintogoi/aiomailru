"""My.Mail.Ru API."""
from typing import Any, Dict, Generator, Tuple

from .session import TokenSession


class API:
    """Platform@Mail.Ru REST API.

    Attributes:
        session (TokenSesion): session.

    """

    __slots__ = ('session', )

    def __init__(
        self,
        app_id: str,
        session_key: str,
        private_key: str = '',
        secret_key: str = '',
        uid: str = '',
    ) -> None:
        """Set session."""
        if uid and private_key:
            secret = private_key
            secure = '0'
        if secret_key:
            secret = secret_key
            secure = '1'
            uid = ''
        self.session = TokenSession(
            app_id=app_id,
            session_key=session_key,
            secret=secret,
            secure=secure,
            uid=uid,
        )

    def __await__(self) -> Generator['API', None, None]:
        """Await self."""
        yield self

    async def __aenter__(self) -> 'API':
        """Enter."""
        return self

    async def __aexit__(self, *args: Tuple[Any, Any, Any]) -> None:
        """Exit."""
        if not self.session.client.is_closed:
            await self.session.client.aclose()

    def __getattr__(self, name: str) -> 'APIMethod':
        """Return an API method."""
        return APIMethod(self, name)

    async def __call__(self, name: str, **params: Dict[str, Any]) -> 'APIMethod':  # noqa
        """Call an API method by its name.

        Args:
            name (str): full method's name
            params (Dict[str, Any]): query parameters

        Returns:
            APIMethod

        """
        return await getattr(self, name)(**params)


class APIMethod:
    """Platform@Mail.Ru REST API method.

    Attributes:
        api (API): API instance
        name (str): full method's name

    """

    __slots__ = ('api', 'name')

    def __init__(self, api: API, name: str) -> None:
        """Set method name."""
        self.api = api
        self.name = name

    def __getattr__(self, name: str) -> 'APIMethod':
        """Chain methods.

        Args:
            name (str): method name

        """
        return APIMethod(self.api, f'{self.name}.{name}')

    async def __call__(self, **params: Dict[str, Any]) -> Dict[str, Any]:
        """Execute a request.

        Args:
            params (Dict[str, Any]): query parameters

        Returns:
            Dict[str, Any]

        """
        params['method'] = self.name
        return await self.api.session.request(params=params)
