# Getting Started

## Installation

If you use pip, just type

```shell
$ pip install aiomailru
```

You can install from the source code like

```shell
$ git clone https://github.com/konstantintogoi/aiomailru.git
$ cd aiomailru
$ python setup.py install
```

## Account

Sign up in [Mail.Ru](https://mail.ru).

## Application

After signing up visit Mail.Ru API [documentation page](https://api.mail.ru/docs/)
and create a new application: https://api.mail.ru/apps/my/add.

Save **client_id** (aka **app_id**), **private_key** and **secret_key**
for user authorization and executing API requests.

```python
app_id = 'your_client_id'
private_key = 'your_private_key'
secret_key = 'your_secret_key'
```
