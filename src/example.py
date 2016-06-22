#!/usr/bin/env python3

import json
from urllib import request, parse

from qqrobot import QQClient, QQHandler
import mlogger as log


class QQTulingHandler(QQHandler):
    url_req = "http://www.tuling123.com/openapi/api"

    def __init__(self, APIKey=None):
        if str(APIKey) in ('None', ''):
            print('You\'ll have to provide an APIKey first.')
            print('Get it @ http://tuling123.com')
            raise ValueError('APIKey not available')
        else:
            self.key = APIKey

    def on_buddy_message(self, uin, msg):
        d = parse.urlencode(
            {'key': self.key, 'info': msg, 'userid': uin}).encode('utf-8')
        with request.urlopen(self.url_req, data=d) as f:
            j = json.loads(f.read().decode('utf-8'))
        log.i('Tuling', ':'.join((str(uin), msg)))
        log.i('Tuling', 'response:' + j['text'])
        self.send_buddy_message(uin, j['text'])


if __name__ == "__main__":
    a = QQClient()
    h = QQTulingHandler(input('API Key:'))
    a.QR_veri()
    # a.loadVeri('./ekTester.veri')
    a.login()
    a.add_handler(h)
    a.listen(join=True)
