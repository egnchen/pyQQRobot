import json
import traceback
from multiprocessing.dummy import Pool
from urllib import request, parse
from http.cookiejar import Cookie, MozillaCookieJar

import mlogger as log


class mHTTPClient(object):
    str_cb_unclear = 'Callback method not specified.'

    def req(self, url, *, data=None, headers={}):
        raise NotImplementedError()

    def req_async(self, url, *, data=None, headers={}, cb=None):
        if cb is None:
            raise ValueError(self.str_cb_unclear)
        cb(self.req(url, data=data, headers=headers),
            {'url': url, 'data': data, 'headers': headers})

    # ----------syntactic sugars------------

    def get_json(self, url, *, data=None, headers={}):
        return json.loads(self.get_text(url, data=data, headers=headers))

    def get_text(self, url, *, data=None, headers={}):
        return self.req(
            url, data=data, headers=headers).decode('utf-8').strip()

    def get_image(self, url, *, data=None, filename='./tmp', headers={}):
        with open(filename, 'wb') as f:
            f.write(self.req(url, data=data, headers=headers))
        return filename

    def get_text_async(self, url, *, data=None, headers={}, cb=None):
        if cb is None:
            raise ValueError(self.str_cb_unclear)

        def cb_text(x, y):
            return cb(x.decode('utf-8').strip(), y)
        self.req_async(url, data=data, headers=headers, cb=cb_text)

    def get_json_async(self, url, *, data=None, headers={}, cb=None):
        if cb is None:
            raise ValueError(self.str_cb_unclear)

        def cb_json(x, y):
            return cb(json.loads(x.decode('utf-8')), y)
        self.req_async(url, data=data, headers=headers, cb=cb_json)

    # --------end syntactic sugars---------

    def set_cookie(self, name, value, domain, expires=None):
        raise NotImplementedError()

    def get_cookie(self, name, domain):
        raise NotImplementedError()

    def get_cookies(self):
        raise NotImplementedError()

    def clear_cookie(self):
        raise NotImplementedError()


class mHTTPClient_urllib(mHTTPClient):
    def req(self, url, *, data=None, headers={}):
        r = request.Request(url)
        if data is not None:
            r.data = parse.urlencode(data).encode('utf-8')
        r.headers.update(headers)
        try:
            f = self.opener.open(r)
            return f.read()
        except Exception:
            log.w('http', 'HTTP error @ ' + url)
            traceback.print_exc()


    def req_async(self, url, *, data=None, headers={}, cb=None):
        if cb is None:
            raise ValueError(self.str_cb_unclear)

        def task():
            cb(self.req(url, data=data, headers=headers),
                {'url': url, 'data': data, 'headers': headers})
        self.threadPool.apply_async(task)

    def set_cookie(self, name, value, domain, path='/', expires=None):
        self.cj.set_cookie(Cookie(
            version=0, name=name, value=value, port=None,
            port_specified=False, domain=domain, domain_specified=True,
            domain_initial_dot=False, path=path, path_specified=True,
            secure=False, expires=expires, discard=False, comment=None,
            comment_url=None, rest=None))

    def get_cookie(self, name, domain, path='/'):
        try:
            return self.cj._cookies[domain][path][name].value
        except Exception:
            raise RuntimeError('Cookie not found:%s @ %s%s' % (
                name, domain, path))

    def get_cookies(self):
        '''get all the cookies saved.
        path is ignored here, as it's always '/'(root)
        '''
        d = {}
        for domain, cookieDict in self.cj._cookies.items():
            d[domain] = {}
            for path, cks in cookieDict.items():
                d[domain].update({n: ck.value for n, ck in cks.items()})
        return d

    def clear_cookie(self):
        self.cj.clear()

    def __init__(self):
        self.cj = MozillaCookieJar()
        self.opener = request.build_opener(
            request.HTTPCookieProcessor(self.cj))
        self.threadPool = Pool(processes=10)
