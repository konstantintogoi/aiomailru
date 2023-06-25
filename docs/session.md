# Session

The session makes **GET** requests when you call instance of `APIMethod`
class that are returned as attributes of an `API` class instance.

## Request

By default, the session (`CodeSession`, `PasswordSession`, `RefreshSession`)
tries to infer which signature generation circuit to use:

* if `uid` and `private_key` are not empty strings - **client-server** signature generation circuit is used
* else if `secret_key` is not an empty string - **server-server** signature generation circuit is used
* else exception is raised

You can explicitly set a signature generation circuit for signing requests
by passing to `API` one of the sessions below.

### Client-Server signature generation circuit

Let's consider the following example of API request with client-server signature:

```python
from aiomailru import TokenSession, API

session = TokenSession(
    app_id=423004,
    private_key='7815696ecbf1c96e6894b779456d330e',
    secret_key='',
    access_token='be6ef89965d58e56dec21acb9b62bdaa',
    uid='1324730981306483817',
)
api = API(session)

friends = await api.friends.get()
```

It is equivalent to **GET** request:

```shell
https://appsmail.ru/platform/api
    ?method=friends.get
    &app_id=423004
    &session_key=be6ef89965d58e56dec21acb9b62bdaa
    &sig=5073f15c6d5b6ab2fde23ac43332b002
```

The following steps were taken:

1. request parameters were sorted and concatenated - `app_id=423004method=friends.getsession_key=be6ef89965d58e56dec21acb9b62bdaa`
2. `uid`, sorted request parameters, `private_key` were concatenated - `1324730981306483817app_id=423004method=friends.getsession_key=be6ef89965d58e56dec21acb9b62bdaa7815696ecbf1c96e6894b779456d330e`
3. signature `5073f15c6d5b6ab2fde23ac43332b002` calculated as MD5 of the previous string
4. signature appended to **GET** request parameters

For more details, see https://api.mail.ru/docs/guides/restapi/#client.

#### ClientSession

`ClientSession` is a subclass of `TokenSession`.

```python
from aiomailru import ClientSession, API

session = ClientSession(app_id, 'private key', 'access token', uid)
api = API(session)
...
```

#### CodeClientSession

`CodeClientSession` is a subclass of `CodeSession`.

```python
from aiomailru import CodeClientSession, API

async with CodeClientSession(app_id, 'private key', code, redirect_uri) as session:
    api = API(session)
    ...
```

#### PasswordClientSession

`PasswordClientSession` is a subclass of `PasswordSession`.

```python
from aiomailru import PasswordClientSession, API

async with PasswordClientSession(app_id, 'private key', email, passwd, scope) as session:
    api = API(session)
    ...
```

#### RefreshClientSession

`RefreshClientSession` is a subclass of `RefreshSession`.

```python
from aiomailru import RefreshClientSession, API

async with RefreshClientSession(app_id, 'private key', refresh_token) as session:
    api = API(session)
    ...
```

### Server-Server signature generation circuit

Let's consider the following example of API request with server-server signature:

```python
from aiomailru import TokenSession, API

session = TokenSession(
    app_id=423004,
    private_key='',
    secret_key='3dad9cbf9baaa0360c0f2ba372d25716',
    access_token='be6ef89965d58e56dec21acb9b62bdaa',
    uid='',
)
api = API(session)

friends = await api.friends.get()
```

It is equivalent to **GET** request:

```shell
https://appsmail.ru/platform/api
    ?method=friends.get
    &app_id=423004
    &session_key=be6ef89965d58e56dec21acb9b62bdaa
    &sig=4a05af66f80da18b308fa7e536912bae
```

The following steps were taken:

1. parameter `secure` = `1` appended to parameters
2. request parameters were sorted and concatenated - `app_id=423004method=friends.getsecure=1session_key=be6ef89965d58e56dec21acb9b62bdaa`
3. sorted request parameters and `secret_key` were concatenated - `1324730981306483817app_id=423004method=friends.getsession_key=be6ef89965d58e56dec21acb9b62bdaa3dad9cbf9baaa0360c0f2ba372d25716`
4. signature `4a05af66f80da18b308fa7e536912bae` calculated as MD5 of the previous string
5. signature appended to **GET** request parameters

For more details, see  https://api.mail.ru/docs/guides/restapi/#server.

#### ServerSession

`ServerSession` is a subclass of `TokenSession`.

```python
from aiomailru import ServerSession, API

session = ServerSession(app_id, 'secret key', 'access token')
api = API(session)
...
```

#### CodeServerSession

`CodeServerSession` is a subclass of `CodeSession`.

```python
from aiomailru import CodeServerSession, API

async with CodeServerSession(app_id, 'secret key', code, redirect_uri) as session:
    api = API(session)
    ...
```

#### PasswordServerSession

`PasswordServerSession` is a subclass of `PasswordSession`.

```python
from aiomailru import PasswordServerSession, API

async with PasswordServerSession(app_id, 'secret key', email, password, scope) as session:
    api = API(session)
    ...
```

#### RefreshServerSession

`RefreshServerSession` is a subclass of `RefreshSession`.

```python
from aiomailru import RefreshServerSession, API

async with RefreshServerSession(app_id, 'secret key', refresh_token) as session:
    api = API(session)
    ...
```

## Response

By default, a session after executing request returns response's body
as `dict` if executing was successful, otherwise it raises exception.

You can pass `pass_error` parameter to `TokenSession`
for returning original response (including errors).

## Error

In case of an error, by default, exception is raised.
You can pass `pass_error` parameter to `TokenSession`
for returning original error's body as `dict`:

```python
{
    "error": {
        "error_code": 202,
        "error_msg": "Access to this object is denied"
    }
}
```
