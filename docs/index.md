[![LICENSE](https://img.shields.io/badge/license-BSD-blue.svg)](https://github.com/konstantintogoi/aiomailru/blob/master/LICENSE)
[![Latest Release](https://img.shields.io/pypi/v/aiomailru.svg)](https://pypi.python.org/pypi/aiomailru)
[![Supported Python Versions](https://img.shields.io/pypi/pyversions/aiomailru.svg)](https://pypi.python.org/pypi/aiomailru)
[![Read the Docs](https://readthedocs.org/projects/aiomailru/badge/?version=latest)](https://aiomailru.readthedocs.io/en/latest)
[![GitHub Pages](https://github.com/konstantintogoi/aiomailru/actions/workflows/pages/pages-build-deployment/badge.svg)](https://konstantintogoi.github.io/aiomailru)

# aiomailru

aiomailru is a python [Mail.Ru API](https://api.mail.ru/) wrapper.

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

## Supported Python Versions

Python 3.7, 3.8, 3.9 are supported.

## License

aiomailru is released under the BSD 2-Clause License.
