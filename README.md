# pyQQRobot
基于Python3与WebQQ的QQ机器人框架。

A QQ Robot framework based on WebQQ and Python3.

## Disclaimer
As a Senior Two student(about to one in Senior Three) in China there just cannot be enough time for me to maintain the project often. I sincerely hope that there'll be coders interested to help.

## How to use?
Here is a simple example.

```python
#!/bin/usr/env python3
from qqRobot import qqClient,qqHandler

class myHandler(qqHandler):
	def onBuddyMessage(self,uin,msg):
		self.sendMessage(uin,"Hello, my name is pyQQRobot!")

if __name__=='__main__':
	qc=qqClient()
	qc.QRVeri()
	qc.Login()
	qc.addHandler(myHandler())
	qc.Listen(join=True)
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
1. `retcode 103` when sending `poll2` requests. A login @ `w.qq.com` from the internet browser is required to fix the problem, which make it not doable to run pyQQRobot in CLI-only environments.
2. Possible unhandled `404` errors can lead to crash.
3. More APIs.
4. Using `gevents` instead of `urllib` with `multiprocessing.dummy`.
5. Better `mLogger` with filtering functions.