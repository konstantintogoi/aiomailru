"""Sessions tests."""
import pytest
from httpx import HTTPStatusError

from aiomailru.session import PublicSession, TokenSession


class TestPublicSession:
    """Tests for PublicSession class."""

    async def test_failed_request(self, error_server):
        """Test failed request."""
        session = PublicSession()
        session.client.base_url = error_server.url

        with pytest.raises(HTTPStatusError):
            await session.request({})

    async def test_regulat_request(self, data_server):
        """Test regular request."""
        session = PublicSession()
        session.client.base_url = data_server.url

        assert await session.request({}) == {'key': 'value'}


class TestTokenSession:
    """Tests of TokenSession class."""

    @pytest.fixture
    def app(self):
        """Return app info."""
        return {'app_id': 123, 'private_key': '', 'secret_key': ''}

    @pytest.fixture
    def token(self):
        """Return token info."""
        return {'access_token': '', 'uid': 0}

    async def test_error_request_with_raising(self, error_server):
        """Test error request that raises an error."""
        session = TokenSession(
            app_id='123',
            session_key='session key',
            secret='secret key',
            secure='1',
            uid='',
        )
        session.client.base_url = error_server.url

        with pytest.raises(HTTPStatusError):
            await session.request(params={'key': 'value'})

    async def test_data_request(self, data_server):
        """Test regular request."""
        session = TokenSession(
            app_id='123',
            session_key='session key',
            secret='secret key',
            secure='1',
            uid='',
        )
        session.client.base_url = data_server.url

        assert await session.request(params={'k': 'v'}) == {'key': 'value'}
