# pyQQRobot
基于Python3与WebQQ的QQ机器人框架。

A QQ Robot framework based on WebQQ and Python3.

## Disclaimer
As a Senior Two student(about to one in Senior Three) in China there just cannot be enough time for me to maintain the project often. I sincerely hope that there'll be coders interested to help.

## How to use?
Here is a simple example.

```python
#!/bin/usr/env python3

from qqrobot import QQClient, QQHandler


class MyHandler(QQHandler):
    def on_buddy_message(self, uin, msg):
        self.send_message(uin, "Hello, my name is pyQQRobot!")

if __name__ == '__main__':
    qc = QQClient()
    qc.QR_veri()
    qc.login()
    qc.add_handler(MyHandler())
    qc.listen(join=True)
```

You can refer to src/example.py for another example, using some sort of intelligent robot to respond to messages.

## Structure
Here's a brief list of the files included:

* **qqRobot.py** includes
    * **qqClient** A set of WebQQ APIs and the core runtime of pyQQRobot
    * **qqHandler** The simple plugin framework.
* **qqFriends.py** The QQ friends, groups and discus groups data parser.
* **qqHttp.py** Simple HTTP Client.
* **mLogger.py** Simple screen logger.

Commonly **qqRobot** is what you all need.

## Known bugs & Possible improvements
1. ~~`retcode 103` when sending `poll2` requests.~~ Problem solved.
2. Possible unhandled `404` errors can lead to crash.
3. More APIs.
4. Using `gevents` instead of `urllib` with `multiprocessing.dummy`.
5. Better `mLogger` with filtering functions.
