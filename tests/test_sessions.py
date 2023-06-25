"""Sessions tests."""
import pytest

from aiomailru.exceptions import Error, APIError
from aiomailru.sessions import PublicSession, SignatureCircuit, TokenSession


class TestPublicSession:
    """Tests of PublicSession class."""

    @pytest.mark.asyncio
    async def test_error_request(self, error_server, error):
        async with PublicSession() as session:
            session.PUBLIC_URL = error_server.url

            session.pass_error = True
            response = await session.public_request()
            assert response == error

    @pytest.mark.asyncio
    async def test_error_request_with_raising(self, error_server):
        async with PublicSession() as session:
            session.PUBLIC_URL = error_server.url

            session.pass_error = False
            with pytest.raises(APIError):
                await session.public_request()

    @pytest.mark.asyncio
    async def test_data_request(self, data_server, data):
        async with PublicSession() as session:
            session.PUBLIC_URL = data_server.url

            session.pass_error = True
            response = await session.public_request()
            assert response == data

            session.pass_error = False
            response = await session.public_request()
            assert response == data


class TestTokenSession:
    """Tests of TokenSession class."""

    @pytest.fixture
    def app(self):
        return {'app_id': 123, 'private_key': '', 'secret_key': ''}

    @pytest.fixture
    def token(self):
        return {'access_token': '', 'uid': 0}

    @pytest.mark.asyncio
    async def test_sig_circuit(self, app, token):
        async with TokenSession(**app, **token) as session:
            assert session.sig_circuit is SignatureCircuit.UNDEFINED

            session.secret_key = 'secret key'
            assert session.sig_circuit is SignatureCircuit.SERVER_SERVER

            session.uid = 456
            session.private_key = 'private key'
            assert session.sig_circuit is SignatureCircuit.CLIENT_SERVER

    @pytest.mark.asyncio
    async def test_required_params(self, app, token):
        async with TokenSession(**app, **token) as session:
            assert 'app_id' in session.required_params
            assert 'session_key' in session.required_params
            assert 'secure' not in session.required_params
            session.uid = 456
            session.private_key = ''
            session.secret_key = 'secret key'
            assert 'secure' in session.required_params

    @pytest.mark.asyncio
    async def test_params_to_str(self, app, token):
        async with TokenSession(**app, **token) as session:
            params = {'"a"': 1, '"b"': 2, '"c"': 3}

            session.uid = 789
            session.private_key = 'private key'
            query = session.params_to_str(params)
            assert query == '789"a"=1"b"=2"c"=3private key'

            session.uid = 0
            session.private_key = ''
            session.secret_key = 'secret key'
            query = session.params_to_str(params)
            assert query == '"a"=1"b"=2"c"=3secret key'

            session.secret_key = ''
            with pytest.raises(Error):
                _ = session.params_to_str(params)

    @pytest.mark.asyncio
    async def test_error_request(self, app, token, error_server, error):
        async with TokenSession(**app, **token) as session:
            session.API_URL = error_server.url
            session.secret_key = 'secret key'

            session.pass_error = True
            response = await session.request(params={'key': 'value'})
            assert response == error

    @pytest.mark.asyncio
    async def test_error_request_with_raising(self, app, token, error_server):
        async with TokenSession(**app, **token) as session:
            session.API_URL = error_server.url
            session.secret_key = 'secret key'

            session.pass_error = False
            with pytest.raises(APIError):
                await session.request(params={'key': 'value'})

    @pytest.mark.asyncio
    async def test_data_request(self, app, token, data_server, data):
        async with TokenSession(**app, **token) as session:
            session.API_URL = data_server.url
            session.secret_key = 'secret key'

            session.pass_error = True
            response = await session.request(params={'key': 'value'})
            assert response == data

            session.pass_error = False
            response = await session.request(params={'key': 'value'})
            assert response == data
