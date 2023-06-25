# REST API

List of all methods is available here: https://api.mail.ru/docs/reference/rest/.

## Executing requests

For executing API requests call an instance of `APIMethod` class.
You can get it as an attribute of `API` class instance or
as an attribute of other `APIMethod` class instance.

```python
from aiomailru import API

api = API(session)

events = await api.stream.get()  # events for current user
friends = await api.friends.get()  # current user's friends
```

Under the hood each API request is enriched with parameters to generate signature:

* `method`
* `app_id`
* `session_key`
* `secure`

and with the following parameter after generating signature:

* `sig`, see https://api.mail.ru/docs/guides/restapi/#sig
