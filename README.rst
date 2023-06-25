.. image:: https://img.shields.io/badge/license-BSD-blue.svg
    :target: https://github.com/konstantintogoi/aiomailru/blob/master/LICENSE

.. image:: https://img.shields.io/pypi/v/aiomailru.svg
    :target: https://pypi.python.org/pypi/aiomailru

.. image:: https://img.shields.io/pypi/pyversions/aiomailru.svg
    :target: https://pypi.python.org/pypi/aiomailru

.. image:: https://readthedocs.org/projects/aiomailru/badge/?version=latest
    :target: https://aiomailru.readthedocs.io/en/latest

.. image:: https://github.com/konstantintogoi/aiomailru/actions/workflows/pages/pages-build-deployment/badge.svg
    :target: https://konstantintogoi.github.io/aiomailru

.. index-start-marker1

aiomailru
=========

aiomailru is a python `Mail.Ru API <https://api.mail.ru/>`_ wrapper.
The main features are:

Usage
-----

To use `Mail.Ru API <https://api.mail.ru/>`_ you need a registered app and
`Mail.Ru <https://mail.ru>`_ account.
For more details, see
`aiomailru Documentation <https://konstantintogoi.github.io/aiomailru>`_.

Client application
~~~~~~~~~~~~~~~~~~

Use :code:`ClientSession` when REST API is needed in:

- a client component of the client-server application
- a standalone mobile/desktop application

i.e. when you embed your app's info (private key) in publicly available code.

.. code-block:: python

    from aiomailru import ClientSession, API

    session = ClientSession(app_id, private_key, access_token, uid)
    api = API(session)

    events = await api.stream.get()
    friends = await api.friends.getOnline()

Use :code:`access_token` and :code:`uid`
that were received after authorization. For more details, see
`authorization instruction <https://konstantintogoi.github.io/aiomailru/authorization>`_.

Server application
~~~~~~~~~~~~~~~~~~

Use :code:`ServerSession` when REST API is needed in:

- a server component of the client-server application
- requests from your servers

.. code-block:: python

    from aiomailru import ServerSession, API

    session = ServerSession(app_id, secret_key, access_token)
    api = API(session)

    events = await api.stream.get()
    friends = await api.friends.getOnline()

Use :code:`access_token` that was received after authorization.
For more details, see
`authorization instruction <https://konstantintogoi.github.io/aiomailru/authorization>`_.

Installation
------------

.. code-block:: shell

    $ pip install aiomailru

Supported Python Versions
-------------------------

Python 3.7, 3.8, 3.9 are supported.

.. index-end-marker1

License
-------

aiomailru is released under the BSD 2-Clause License.
