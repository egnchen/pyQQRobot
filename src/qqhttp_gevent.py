import traceback

import gevent
from gevent import monkey
monkey.patch_all()

from urllib import request, parse
from qqhttp import mHTTPClient_urllib

import mlogger as log

class mHTTPClient_gevent(mHTTPClient_urllib):
    def __init__(self):
        # mHTTPClient running gevent
        # during test
        log.w('http', "You're using gevent based http client.")
        super(mHTTPClient_gevent, self).__init__()

    def _gevent_req(self, url, data, headers):
        r = request.Request(url)
        if data is not None:
            r.data = parse.urlencode(data).encode('utf-8')
        r.headers.update(headers)
        try:
            f = self.opener.open(r)
            # hang up here
            # gevent will automatically switch to different jobs
            return f.read()
        except Exception:
            log.w('http', 'HTTP error @ ' + url)
            traceback.print_exc()

    def req(self, url, *, data=None, headers={}):
        # spawn a job and join
        j = gevent.spawn(self._gevent_req, url, data=data, headers=headers)
        j.join() # timeout = None
        return j.value

    def req_async(self, url, *, data=None, headers={}, cb=None):
        if cb is None:
            raise ValueError(self.str_cb_unclear)

        # new callback with a greenlet object as the argument
        def gevent_cb(g):
            return cb(g.value, {'url': url, 'data': data, 'headers': headers})

        j = gevent.spawn(self._gevent_req, url, data=data, headers=headers)
        j.link(gevent_cb)
        j.join(timeout = 0) # don't wait and exit