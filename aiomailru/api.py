"""My.Mail.Ru API."""
from typing import Any, Dict

from .sessions import TokenSession


class API:
    """Platform@Mail.Ru REST API."""

    __slots__ = ('session', )

    def __init__(self, session: TokenSession) -> None:
        """Set session."""
        self.session = session

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
        return await self.api.session.request('', params=params)
