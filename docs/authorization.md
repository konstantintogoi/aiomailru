# Authorization

The preferred way to authorize is an `async with` statement.
After authorization the session will have the following attributes:

* `session_key` aka `access_token`
* `refresh_token`
* `expires_in`
* `uid`

## Authorization Code Grant

```python
from aiomailru import CodeSession, API

app_id = 123456
private_key = ''
secret_key = 'xyz'

async with CodeSession(app_id, private_key, secret_key, code, redirect_uri) as session:
    api = API(session)
    ...
```

About OAuth 2.0 Authorization Code Grant: https://oauth.net/2/grant-types/authorization-code/

For more details, see https://api.mail.ru/docs/guides/oauth/sites/
and https://api.mail.ru/docs/guides/oauth/mobile-web/

## Password Grant

```python
from aiomailru import PasswordSession, API

app_id = 123456
private_key = 'abcde'
secret_key = ''

async with PasswordSession(app_id, private_key, secret_key, email, password, scope) as session:
    api = API(session)
    ...
```

About OAuth 2.0 Password Grant: https://oauth.net/2/grant-types/password/

For more details, see https://api.mail.ru/docs/guides/oauth/client-credentials/

## Refresh Token

```
from aiomailru import RefreshSession, API

app_id = 123456
private_key = ''
secret_key = 'xyz'

async with RefreshSession(app_id, private_key, secret_key, refresh_token) as session:
    api = API(session)
    ...
```

About OAuth 2.0 Refresh Token: https://oauth.net/2/grant-types/refresh-token/

For more details, see https://api.mail.ru/docs/guides/oauth/client-credentials/#refresh_token
