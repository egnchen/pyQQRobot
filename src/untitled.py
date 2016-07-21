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
    else:
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