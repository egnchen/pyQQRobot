# pyQQRobot
基于Python3与WebQQ的QQ机器人框架。

A QQ Robot framework based on WebQQ and Python3.

## How to use?
Here is a simple example.

```python
#!/usr/bin/env python3

from qqrobot import QQClient, QQHandler
import mlogger as log

class MyHandler(QQHandler):
    def on_buddy_message(self, uin, msg):
        log.i('QQ', 'got message from ' + str(uin))
        self.send_buddy_message(uin, "Powered by pyQQRobot.")

if __name__ == '__main__':
    client = QQClient()
    # to use a gevent-based client, use:
    # from qqhttp_gevent import mHTTPClient_gevent
    # client = QQClient(HTTPClient=mHTTPClient_gevent)
    log_or_load = 'log'

    if log_or_load == 'log':
        # you can log in manually
        client.QR_veri()
        client.login()
        # and then save your verification
        client.save_veri('./' + client.uin + '.veri')
    elif log_or_load == 'load':
        # or load from a file instead
        client.load_veri('./my_verification.veri')
        # You don't need to fetch all that lists,
        # as they are already loaded from verfication files.
        client.login(get_info=False)

    # create & add a message handler
    h = MyHandler()
    client.add_handler(h)
    # then start your journey...
    client.listen()
```

You can refer to `src/example.py` for another example, using some sort of intelligent robot to respond to messages.

## Functions
Now you can:

* send messages to your buddies and group
* set listeners to messages from your buddies and group
* get information about yourself, your buddies and group

Discuss groups aren't supported.

## Structure
Here's a brief list of the files included:

* **qqrobot.py** includes
    * **QQClient** A set of WebQQ APIs and the core runtime of pyQQRobot.
    * **QQHandler** The simple plugin framework.
* **qqfriends.py** The QQ friends, groups and discus groups data parser.
* **qqhttp.py** Simple HTTP Client.
* **mlogger.py** Simple screen logger.

## Disclaimer
As a **Senior Three student in China** there just cannot be enough time for me to maintain the project. I sincerely hope that there'll be coders interested to help.

## so, what TODO next?
Well, no maintainance guaranteed. Maybe I'll turn a blind eye to issues and PRs. But if you insist, just send one.
1. **`QQClient` itself is a little messy.** To solve this, I think `qqhttp` should be dumped, and take a normal way to do it - like using `requests` library instead. Concurrency and asynchrization can be implemented with `gevent` or other libraries.
2. **Sending messages to discus groups.** Technically not difficult.
3. **Finding friends.** I was suprised to find out that there's no standard way to determine a specified user by account num(QQ号) in WebQQ protocol. Sure there's way to do it(I already have something in mind).
