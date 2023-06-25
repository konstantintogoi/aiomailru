[![LICENSE](https://img.shields.io/badge/license-BSD-blue.svg)](https://github.com/konstantintogoi/aiomailru/blob/master/LICENSE)
[![Last Release](https://img.shields.io/pypi/v/aiomailru.svg)](https://pypi.python.org/pypi/aiomailru)
[![Supported Python versions](https://img.shields.io/pypi/pyversions/aiomailru.svg)](https://pypi.python.org/pypi/aiomailru)

# aiomailru

aiomailru is a python [Mail.Ru API](https://api.mail.ru/) wrapper.
The main features are:

* authorization ([Authorization Code](https://oauth.net/2/grant-types/authorization-code/), [Implicit Flow](https://oauth.net/2/grant-types/implicit/), [Password Grant](https://oauth.net/2/grant-types/password/), [Refresh Token](https://oauth.net/2/grant-types/refresh-token/))
* [REST API](https://api.mail.ru/docs/reference/rest/) methods
* web scrapers

## Usage

To use [Mail.Ru API](https://api.mail.ru/) you need a registered app and [Mail.Ru](https://mail.ru) account.
For more details, see [aiomailru Documentation](https://konstantintogoi.github.io/aiomailru).

### Client application

Use `ClientSession` when REST API is needed in:

- a client component of the client-server application
- a standalone mobile/desktop application

i.e. when you embed your app's info (private key) in publicly available code.

```python
from aiomailru import ClientSession, API

session = ClientSession(app_id, private_key, access_token, uid)
api = API(session)

events = await api.stream.get()
friends = await api.friends.getOnline()
```

Use `access_token` and `uid` that were received after authorization.
For more details, see [authorization instruction](https://konstantintogoi.github.io/aiomailru/authorization.html).

### Server application

Use `ServerSession` when REST API is needed in:

- a server component of the client-server application
- requests from your servers

```python
from aiomailru import ServerSession, API

session = ServerSession(app_id, secret_key, access_token)
api = API(session)

events = await api.stream.get()
friends = await api.friends.getOnline()
```

Use `access_token` that was received after authorization.
For more details, see [authorization instruction](https://konstantintogoi.github.io/aiomailru/authorization.html).

## Installation

```shell
$ pip install aiomailru
```

or

```shell
$ python setup.py install
```

## Supported Python Versions

Python 3.5, 3.6, 3.7 and 3.8 are supported.

## Test

Run all tests.

```shell
$ python setup.py test
```

Run tests with PyTest.

```shell
$ python -m pytest [-k TEST_NAME]
```

## License

aiomailru is released under the BSD 2-Clause License.
