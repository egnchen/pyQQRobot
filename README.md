**State**: stable (sometimes)

**Maintainance**: unknown

# pyQQRobot
基于Python3与WebQQ的QQ机器人框架。

A QQ Robot framework based on WebQQ and Python3.

## Disclaimer
As a **Senior Three student in China** there just cannot be enough time for me to maintain the project. I sincerely hope that there'll be coders interested to help.

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

No discuss groups included.

### Logs can be filtered and saved
the logger is fully rewritten and now support filteration and preservation. Check out `mLogger.py` for details.

```python
mlogger.supress_tag('this_tag_wont_be_shown_on_the_screen')
mlogger.supress_level(mlogger.levels.w)  # w, i, e, v
mlogger.unsupress_tag('show_this_tag_again')
mlogger.unsupress_level(mlogger.levels.w) # w, i, e, v
mlogger.unsupress_all_tags()
mlogger.unsupress_all_levels()

mlogger.i('tag', "this won't be saved in the file", save=False)
mlogger.save('/path/to/your/log/saved/in/json')
```

## Structure
Here's a brief list of the files included:

* **qqrobot.py** includes
    * **QQClient** A set of WebQQ APIs and the core runtime of pyQQRobot
    * **QQHandler** The simple plugin framework.
* **qqfriends.py** The QQ friends, groups and discus groups data parser.
* **qqhttp.py** Simple HTTP Client.
* **mlogger.py** Simple screen logger.

## Known bugs & Possible improvements
1. ~~`retcode 103` when sending `poll2` requests.~~ Problem solved.
2. ~~Possible unhandled `404` errors can lead to crash.~~ 404 errors ignored.
3. More APIs.
4. Using `gevents` instead of `urllib` with `multiprocessing.dummy`.
5. ~~Better `mLogger` with filtering functions.~~
6. ~~To save verification in files, and read them.~~
