import time
import os
import json
import threading
import traceback

from qqfriends import QQFriends
from qqhttp import mHTTPClient_urllib
import mlogger as log


def utime():
    return int(time.time())

# WARN: the following command set default `print` to
#       mLogger output command.
#       It's suggested to use log.v(TAG, 'message....')
#       instead of using `print` directly.
# print = log.output


class QQClient():
    default_headers = dict(
        Referer='http://s.web2.qq.com/proxy.html',
        User_Agent=(
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_4) AppleWebKit/'
            '537.36 (KHTML, like Gecko) Chrome/50.0.2661.86 Safari/537.36'))
    poll_headers = dict(
        Origin='http://d1.web2.qq.com',
        Referer='http://d1.web2.qq.com/proxy.html',
        User_Agent=(
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_4) AppleWebKit/'
            '537.36 (KHTML, like Gecko) Chrome/50.0.2661.86 Safari/537.36'))

    def __init__(self, HTTPClient=mHTTPClient_urllib, handlers=[]):
        self.friend_list = QQFriends()
        self.http_client = HTTPClient()
        self.msg_id = 50500000
        self.handlers = handlers

    def _callback_receive(self, resp, previous):
        tag = 'listener'
        try:
            resp = json.loads(resp.decode('utf-8'))
            if resp.get('retcode', 0) != 0:
                # something is wrong
                log.e(tag, 'error retcode %d errmsg %s' % (
                    resp.get('retcode', 0), resp.get('errmsg', 'none')))
                if resp.get('retcode', 0) == 103:
                    # Connection failed, log in again.
                    log.w(tag, 'Meet with error 103.')
                    log.w(tag, 'Please log in again')
                    exit()
            else:
                if resp.get('errmsg') is not None:
                    # {errmsg: "error!!!", retcode: 0}
                    # time exceeds every minute, just ignore it.
                    log.v(tag, 'listening...')
                    return
                for c in resp['result']:
                    num = c['value']['from_uin']
                    msg = c['value']['content'][1]
                    if c['poll_type'] == 'message':
                        log.v(tag, 'got message from friend ' + str(num))
                        for h in self.handlers:
                            h.on_buddy_message(num, msg)
                    elif c['poll_type'] == 'group_message':
                        log.v(tag, 'got message from group ' + str(num))
                        uin = c['value']['send_uin']
                        for h in self.handlers:
                            h.on_group_message(num, uin, msg)
        except Exception:
            log.e(tag, 'Fatal error parsing messages.')
            log.e(tag, resp)
            traceback.print_exc()

    def _callback_send(self, resp, previous):
        tag = 'Sender'
        resp = json.loads(resp.decode('utf-8'))
        log.v(tag, 'Got feedback.')
        if resp.get('errCode', 0) != 0 or resp.get('retcode', 0) != 0:
            # retcode1202 is an error which is not and should be ignored.
            if resp.get('retcode', 0) == 1202:
                log.v(tag, 'retcode 1202.')

    def _parse_arg(self, js_str):
        js_str = js_str[js_str.index('(') + 1: len(js_str) - 2]
        return list(map(lambda x: x.strip().strip("'"), js_str.split(',')))

    def get_qq_hash(self):
        # rewrite from an javascript function
        # see mq_private.js for original version
        if not hasattr(self, '_qhash'):
            x = int(self.uin)
            I = self.ptwebqq
            N = [0, 0, 0, 0]
            i = 0
            while i < len(I):
                N[i % 4] ^= ord(I[i])
                i += 1
            V = []
            V.append(x >> 24 & 255 ^ ord('E'))
            V.append(x >> 16 & 255 ^ ord('C'))
            V.append(x >> 8 & 255 ^ ord('O'))
            V.append(x & 255 ^ ord('K'))
            U = []
            for T in range(8):
                if T % 2 == 0:
                    U.append(N[T >> 1])
                else:
                    U.append(V[T >> 1])
            N = ["0", "1", "2", "3", "4", "5", "6", "7",
                 "8", "9", "A", "B", "C", "D", "E", "F"]
            V = ""
            for T in range(len(U)):
                V += N[U[T] >> 4 & 15]
                V += N[U[T] & 15]
            self._qhash = V
        return self._qhash

    # def saveVeri(self, filename = None):
    #     if filename =  = None:
    #         filename = self.uin+'.veri'

    # def loadVeri(self, filename):
    #     self.http_client.loadCookie(filename)

    def QR_veri(self, show_QR=None):
        tag = 'verify'
        # --------------necessary urls--------------
        url_get_QR_image = "https://ssl.ptlogin2.qq.com/ptqrshow?" \
                           "appid=501004106&e=0&l=M&s=5&d=72&v=4&t=0.5"
        url_check_QR_state = (
            "https://ssl.ptlogin2.qq.com/ptqrlogin?webqq_type=10&"
            "remember_uin=1&login2qq=1&aid=501004106&u1="
            "http%3A%2F%2Fw.qq.com%2Fproxy.html%3Flogin2qq%3D1%26webqq_type"
            "%3D10&ptredirect=0&ptlang=2052&daid=164&from_ui=1&pttype=1&"
            "dumy=&fp=loginerroralert&action=0-0-{timer}&mibao_css=m_webqq&"
            "t=undefined&g=1&js_type=0&js_ver=10139&login_sig=&pt_randsalt=0"
        )
        # ------------end necessary urls------------

        # get QR image
        if show_QR is None:
            log.w(tag, ("showQR method is not specified, will use default "
                "which is only runs in Mac OSX."))
            # Mac OSX
            def s():
                os.system('open ' +
                          self.http_client.get_image(url_get_QR_image))
            show_QR = s
        show_QR()

        # check QR verification state
        t = int(time.clock() * 10000) + 10000  # default clock
        prev = -1
        while True:
            time.sleep(1)
            t += int(time.clock() * 10000)
            res = self._parse_arg(
                self.http_client.get_text(url_check_QR_state.format(timer=t)))
            if prev != res[0]:
                if res[0] == '65':
                    log.i(tag, 'QR code expired.')
                    show_QR()
                elif res[0] == '66':
                    log.i(tag, 'Please scan the QRCode shown on your screen.')
                elif res[0] == '67':
                    log.i(tag, 'Please press confirm on your phone.')
                elif res[0] == '0':
                    # QR code verification completed
                    log.i(tag, res[-2])
                    self.username = res[-1]
                    log.i(tag, 'User name: ' + self.username)
                    break
                prev = res[0]

        # first step login
        self.http_client.req(res[2])

        # cookie proxy
        self.http_client.set_cookie(
            'p_skey',
            self.http_client.get_cookie('p_skey', '.web2.qq.com'),
            'w.qq.com')
        self.http_client.set_cookie(
            'p_uin',
            self.http_client.get_cookie('p_uin', '.web2.qq.com'),
            'w.qq.com')

    def login(self, get_info=True, save_veri=False, filename=None):
        # --------necessary urls & data--------
        url_get_vfwebqq = "http://s.web2.qq.com/api/getvfwebqq?" \
                          "ptwebqq={ptwebqq}&psessionid=&t=1456633306528"
        url_login2 = "http://d1.web2.qq.com/channel/login2"
        post_login2 = {'clientid': 53999199,
                       'pssessionid': '', 'status': 'online'}
        # ------end necessary urls & data------

        # get ptwebqq
        self.ptwebqq = self.http_client.get_cookie('ptwebqq', '.qq.com')
        # get vfwebqq
        self.vfwebqq = self.http_client.get_json(
            url_get_vfwebqq.format(ptwebqq=self.ptwebqq),
            headers=self.default_headers)['result']['vfwebqq']

        # second step login
        post_login2['ptwebqq'] = self.ptwebqq
        j2 = self.http_client.get_json(url_login2,
                                       data={'r': json.dumps(post_login2)})

        self.uin = j2['result']['uin']
        self.psessionid = j2['result']['psessionid']
        self.status = j2['result']['status']
        self.get_qq_hash()
        if get_info:
            self.get_user_friends()
            self.get_group_list()
            self.get_discus_list()
        if save_veri:
            self.save_veri()
        self.get_online_buddies()
        self.get_recent_list()

    def save_veri(self, filename=None):
        if filename is None:
            filename = './' + str(self.uin) + '.veri'

        with open(filename, 'w') as f:
            # save all cookies
            f.write('{"cookies":')
            json.dump(self.http_client.get_cookies(), f)
            # save user friends, groups and discus groups
            f.write(',\n"friends":')
            json.dump(self.friend_list.f, f)
            f.write(',\n"groups":')
            json.dump(self.friend_list.g, f)
            f.write(',\n"discus_groups":')
            json.dump(self.friend_list.d, f)
            f.write('}')

        return filename

    def load_veri(self, filename):
        with open(filename, 'r') as f:
            v = json.load(f)
        for domain, cookies in v['cookies'].items():
            for name, value in cookies.items():
                self.http_client.set_cookie(name, value, domain)
        # TODO deal with the int-key conversion issues
        self.friend_list.f = {
            int(id): value for id, value in v['friends'].items()}
        self.friend_list.g = {
            int(id): value for id, value in v['groups'].items()}
        self.friend_list.d = {
            int(id): value for id, value in v['discus_groups'].items()}

    def listen(self, join=False):
        url_poll2 = 'http://d1.web2.qq.com/channel/poll2'
        d = {'r': json.dumps({
            "ptwebqq": self.ptwebqq, "clientid": 53999199,
            "psessionid": self.psessionid, "key": ""})}

        def l():
            while True:
                r = self.http_client.req(
                    url_poll2, data=d, headers=self.poll_headers)
                self._callback_receive(
                    r, {'url': url_poll2,
                        'data': d, 'headers': self.poll_headers})

        t = threading.Thread(name='qq_client_listener', target=l)
        t.start()
        log.i('listener', 'Listener thread started.')
        if join:
            t.join()

    def get_user_friends(self):
        self.friend_list.parse_friends(self.http_client.get_json(
            'http://s.web2.qq.com/api/get_user_friends2',
            data={'r': json.dumps({
                  'hash': self.get_qq_hash(),
                  'vfwebqq': self.vfwebqq})},
            headers=self.default_headers))
        log.i('list', 'Finished getting friend list.')

    def get_group_list(self):
        self.friend_list.parse_groups(self.http_client.get_json(
            'http://s.web2.qq.com/api/get_group_name_list_mask2',
            data={'r': json.dumps({
                  'hash': self.get_qq_hash(),
                  'vfwebqq': self.vfwebqq})},
            headers=self.default_headers))
        log.i('list', 'Group list fetched.')

    def get_discus_list(self):
        self.friend_list.parse_discus(self.http_client.get_json(
            'http://s.web2.qq.com/api/get_discus_list',
            data={'clientid': 53999199,
                  'psessionid': self.psessionid,
                  'vfwebqq': self.vfwebqq,
                  't': utime()},
            headers=self.default_headers))
        log.i('list', 'Discus group list fetched.')

    def get_online_buddies(self):
        # method is GET
        url_get_online = (
            'http://d1.web2.qq.com/channel/get_online_buddies2?'
            'vfwebqq={}&clientid={}&psessionid={}&t={}').format(
            self.vfwebqq, 53999199, self.psessionid, utime())
        self.friend_list.parse_online_buddies(
            self.http_client.get_json(
                url_get_online, headers=self.poll_headers))
        log.i('list', 'Online buddies list fetched.')

    def get_recent_list(self):
        self.friend_list.parse_recent(self.http_client.get_json(
            'http://d1.web2.qq.com/channel/get_recent_list2',
            data={'r': json.dumps({
                  'vfwebqq': self.vfwebqq,
                  'clientid': 53999199,
                  'psessionid': self.psessionid})},
            headers=self.poll_headers))
        log.i('list', 'Recent list fetched.')

    def get_self_info(self):
        # method is GET
        if not hasattr(self, 'info'):
            r = self.http_client.get_json(
                'http://s.web2.qq.com/api/get_self_info2?t' + str(utime()),
                headers=self.default_header)
            if r['retcode'] == 0:
                self.info = r['result']
            else:
                log.e('info', 'User self info fetching failed.')
        return self.info
        

    def get_user_info(self, uin):
        # method is GET
        r = self.friend_list.get_user_info(uin)
        if r is not None:
            return r
        else:
            url_get_user_info = (
                'http://s.web2.qq.com/api/get_friend_info2?'
                'tuin={}&vfwebqq={}&t={}})').format(
                uin, self.vfwebqq, utime())
            j = self.http_client.get_json(
                url_get_user_info, headers=self.default_headers)
            return self.friend_list.parse_user_info(j)

    def get_group_info(self, gid):
        # method is GET
        r = self.friend_list.get_group_info(gid)
        if r is not None:
            return r
        else:
            url_get_group_info = (
                'http://s.web2.qq.com/api/get_group_info_ext2?'
                'gcode={}&vfwebqq={}&t={}}').format(
                gid, self.vfwebqq, utime())
            j = self.http_client.get_json(
                url_get_group_info, headers=self.default_headers)
            return self.friend_list.parse_group_info(j)

    def send_buddy_message(self, uin, content,
                           font="宋体", size=10, color='000000'):
        self.msg_id += 1
        c = json.dumps([
            content, ["font",
                      {"name": font, "size": size,
                       "style": [0, 0, 0], "color": color}]])
        self.http_client.req_async(
            'http://d1.web2.qq.com/channel/send_buddy_msg2',
            data={'r': json.dumps({
                'to': uin, 'content': c,
                'face': self.friend_list.f[uin]['face'],
                'clientid': 53999199, 'msg_id': self.msg_id,
                'psessionid': self.psessionid})},
            headers=self.poll_headers,
            cb=self._callback_send)

    def send_group_message(self, gid, content,
                           font="宋体", size=10, color='000000'):
        self.msg_id += 1
        c = json.dumps([
            content, ["font",
                      {"name": font, "size": size,
                       "style": [0, 0, 0], "color": color}]])
        self.http_client.req_async(
            'http://d1.web2.qq.com/channel/send_qun_msg2',
            data={'r': json.dumps({
                'group_uin': gid, 'content': c,
                'face': 0,  # TODO figure out what `face` is
                'clientid': 53999199, 'msg_id': self.msg_id,
                'psessionid': self.psessionid})},
            headers=self.poll_headers,
            cb=self._callback_send)

    def add_handler(self, handler):
        handler.set_qq_client(self)
        self.handlers.append(handler)


class QQHandler(object):
    _alloc = ('get_user_info', 'get_user_info', 'get_group_info',
              'send_buddy_message', 'send_group_message')

    def __init__(self):
        self._qq_client = None

    def set_qq_client(self, c):
        if not isinstance(c, QQClient):
            raise TypeError('QQHandler: not a QQClient object.')
        self._qq_client = c

    def __getattr__(self, name):
        if name in self._alloc:
            return self._qq_client.__getattribute__(name)

    def on_fail(self, resp, previous):
        pass

    def on_buddy_message(self, uin, msg):
        pass

    def on_group_message(self, gid, uin, msg):
        pass

