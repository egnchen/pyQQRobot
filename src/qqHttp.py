import json
from multiprocessing.dummy import Pool
from urllib import request,parse
from http.cookiejar import Cookie,MozillaCookieJar

class mHTTPClient(object):

    strNotImplemented='Method not implemented. Try another mHTTPClient class.'

    def req(self,url,*,data=None,headers={}):
        raise NotImplementedError(self.strNotImplemented)

    def reqAsync(self,url,*,data=None,headers={},cb=lambda x,y:x):
        cb(self.req(url,data=data,headers=headers),
            {'url':url,'data':data,'headers':headers})
        
    # ----------syntactic sugars------------

    def getJson(self,url,*,data=None,headers={}):
        return json.loads(self.getText(url,data=data,headers=headers))

    def getText(self,url,*,data=None,headers={}):
        return self.req(url,data=data,headers=headers).decode('utf-8').strip()

    def getImage(self,url,*,data=None,filename='./tmp',headers={}):
        with open(filename,'wb') as f:
            f.write(self.req(url,data=data,headers=headers))
        return filename

    def getTextAsync(self,url,*,data=None,headers={},cb=lambda x,y:x):
        cbText=lambda x,y:cb(x.decode('utf-8').strip(),y)
        self.reqAsync(url,data=data,headers=headers,cb=cbText)

    def getJsonAsync(self,url,*,data=None,headers={},cb=lambda x,y:x):
        cbJson=lambda x,y:cb(json.loads(x.decode('utf-8')),y)
        self.reqAsync(url,data=data,headers=headers,cb=cbJson)

    # --------end syntactic sugars---------

    def setCookie(self,name,value,domain,expires=None):
        raise NotImplementedError(self.strNotImplemented)

    def getCookie(self,name,domain):
        raise NotImplementedError(self.strNotImplemented)

    def clearCookie(self):
        raise NotImplementedError(self.strNotImplemented)


class mHTTPClient_urllib(mHTTPClient):
    def req(self,url,*,data=None,headers={}):
        r=request.Request(url)
        if data != None:
            r.data=parse.urlencode(data).encode('utf-8')
        r.headers.update(headers)
        with self.opener.open(r) as f:
            return f.read()

    def reqAsync(self,url,*,data=None,headers={},cb=lambda x:x):
        def task():
            cb(self.req(url,data=data,headers=headers),
                {'url':url,'data':data,'headers':headers})
        self.threadPool.apply_async(task)

    def setCookie(self,name,value,domain,path='/',expires=None):
        self.cj.set_cookie(Cookie(version=0,name=name,value=value,port=None,
            port_specified=False,domain=domain,domain_specified=True,
            domain_initial_dot=False,path=path,path_specified=True,
            secure=False,expires=expires,discard=False,comment=None,
            comment_url=None,rest=None))

    def getCookie(self,name,domain,path='/'):
        try:
            return self.cj._cookies[domain][path][name].value
        except Exception:
            raise RuntimeError('Cookie not found:%s @ %s%s' % 
                (name,domain,path))

    def getCookies(self):
        d={}
        for domain,cookieDict in self.cj._cookies.items():
            d[domain]={}
            for path,cookies in cookieDict.items():
                d[domain][path]={cookiename:cookie.value for cookiename,cookie in cookies.items()}
        return d

    def clearCookie(self):
        self.cj.clear()

    def __init__(self):
        self.cj=MozillaCookieJar()
        self.opener=request.build_opener(request.HTTPCookieProcessor(self.cj))
        self.threadPool=Pool(processes=10)