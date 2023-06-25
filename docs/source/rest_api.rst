REST API
========

List of all methods is available here: https://api.mail.ru/docs/reference/rest/.

Executing requests
------------------

For executing API requests call an instance of :code:`APIMethod` class.
You can get it as an attribute of :code:`API` class instance or
as an attribute of other :code:`APIMethod` class instance.

.. code-block:: python

    from aiomailru import API

    api = API(session)

    events = await api.stream.get()  # events for current user
    friends = await api.friends.get()  # current user's friends

Under the hood each API request is enriched with parameters to generate signature:

* :code:`method`
* :code:`app_id`
* :code:`session_key`
* :code:`secure`

and with the following parameter after generating signature:

* :code:`sig`, see https://api.mail.ru/docs/guides/restapi/#sig
