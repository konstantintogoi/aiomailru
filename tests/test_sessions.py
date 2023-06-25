"""Sessions tests."""
import pytest
from httpx import HTTPStatusError

from aiomailru.sessions import PublicSession, SignatureCircuit, TokenSession


class TestPublicSession:
    """Tests for PublicSession class."""

    async def test_error_request(self, error_server, error):
        """Test error request."""
        async with PublicSession() as session:
            session.client.base_url = error_server.url

            session.raise_for_status = False
            response = await session.request('', {})
            assert response == error

    async def test_error_request_with_raising(self, error_server):
        """Test error request that raises an error."""
        async with PublicSession() as session:
            session.client.base_url = error_server.url

            session.raise_for_status = True
            with pytest.raises(HTTPStatusError):
                await session.request('', {})

    async def test_data_request(self, data_server, data):
        """Test regular request."""
        async with PublicSession() as session:
            session.client.base_url = data_server.url

            session.raise_for_status = False
            response = await session.request('', {})
            assert response == data

            session.raise_for_status = True
            response = await session.request('', {})
            assert response == data


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

    async def test_sig_circuit(self, app, token):
        """Test signature circuit."""
        async with TokenSession(**app, **token) as session:
            assert session.sig_circuit is SignatureCircuit.UNDEFINED

            session.secret_key = 'secret key'
            assert session.sig_circuit is SignatureCircuit.SERVER_SERVER

            session.uid = 456
            session.private_key = 'private key'
            assert session.sig_circuit is SignatureCircuit.CLIENT_SERVER

    async def test_required_params(self, app, token):
        """Test required query parameters."""
        async with TokenSession(**app, **token) as session:
            assert 'app_id' in session.required_params
            assert 'session_key' in session.required_params
            assert 'secure' not in session.required_params
            session.uid = 456
            session.private_key = ''
            session.secret_key = 'secret key'
            assert 'secure' in session.required_params

    async def test_params2str(self, app, token):
        """Test query string."""
        async with TokenSession(**app, **token) as session:
            params = {'"a"': 1, '"b"': 2, '"c"': 3}

            session.uid = 789
            session.private_key = 'private key'
            query = session.params2str(params)
            assert query == '789"a"=1"b"=2"c"=3private key'

            session.uid = 0
            session.private_key = ''
            session.secret_key = 'secret key'
            query = session.params2str(params)
            assert query == '"a"=1"b"=2"c"=3secret key'

            session.secret_key = ''
            query = session.params2str(params)
            assert query == '"a"=1"b"=2"c"=3'

    async def test_error_request(self, app, token, error_server, error):
        """Test error request."""
        async with TokenSession(**app, **token) as session:
            session.client.base_url = error_server.url
            session.secret_key = 'secret key'

            session.raise_for_status = False
            response = await session.request('', params={'key': 'value'})
            assert response == error

    async def test_error_request_with_raising(self, app, token, error_server):
        """Test error request that raises an error."""
        async with TokenSession(**app, **token) as session:
            session.client.base_url = error_server.url
            session.secret_key = 'secret key'

            session.raise_for_status = True
            with pytest.raises(HTTPStatusError):
                await session.request('', params={'key': 'value'})

    async def test_data_request(self, app, token, data_server, data):
        """Test regular request."""
        async with TokenSession(**app, **token) as session:
            session.client.base_url = data_server.url
            session.secret_key = 'secret key'

            session.raise_for_status = False
            response = await session.request('', params={'key': 'value'})
            assert response == data

            session.raise_for_status = True
            response = await session.request('', params={'key': 'value'})
            assert response == data
