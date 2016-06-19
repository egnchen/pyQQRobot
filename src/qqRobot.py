import time
import os
import json
import threading
import traceback

from qqFriends import qqFriends
from qqHttp import mHTTPClient_urllib
import mLogger as log

utime=lambda:int(time.time())

# WARN: the following command set default `print` to
#       mLogger output command. Use this at your own risk.
#       It's suggested to use log.v(TAG,'message....')
#       instead of using `print` directly.
# print=log.output

class qqClient():
    defaultHeaders=dict(referer='http://s.web2.qq.com/proxy.html?v=20130916001&callback=1&id=1',
        User_Agent='Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_4) AppleWebKit/537.36 (KHTML,like Gecko) Chrome/50.0.2661.86 Safari/537.36')
    pollHeaders=dict(Host='d1.web2.qq.com',
        Origin='http://d1.web2.qq.com',
        Referer='http://d1.web2.qq.com/proxy.html?v=20151105001&callback=1&id=2',
        User_Agent='Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_4) AppleWebKit/537.36 (KHTML,like Gecko) Chrome/50.0.2661.86 Safari/537.36')

    def __init__(self,HTTPClient=mHTTPClient_urllib,handlers=[]):
        self.fl=qqFriends()
        self.HC=HTTPClient()
        self.msgid=50500001
        self.handlers=handlers

    def _callback_receive(self,response,previous):
        TAG='Listener'
        try:
            response=json.loads(response.decode('utf-8'))
            if response.get('retcode',0)!=0 or response.get('result')==None:
                # something is wrong
                log.e(TAG,'error retcode %d errmsg %s' % 
                    (response.get('retcode',0),response.get('errmsg','none')))
                if response.get('retcode',0)==103:
                    # TODO solve this problem
                    log.w(TAG,'Meet with error 103.')
                    log.w(TAG,'This is a problem to solve.')
                    log.w(TAG,'You\'ll have to login to w.qq.com manually '
                        'on this very computer first.')
                    exit()
            else:
                uin=response['result'][0]['value']['from_uin']
                msg=response['result'][0]['value']['content'][1]
                if response['result'][0]['poll_type'] == 'message':
                    log.v(TAG,'got message from friend '+str(uin))
                    for h in self.handlers:
                        h.onBuddyMessage(uin,msg)
                if response['result'][0]['poll_type']=='group_message':
                    log.v(TAG,'got message from group '+str(uin))
                    for h in self.handlers:
                        h.onGroupMessage(uin,msg)
        except Exception:
            log.e(TAG,'Fatal error parsing messages.')
            log.e(TAG,response)
            traceback.print_exc()

    def _callback_send(self,response,previous):
        TAG='Sender'
        response=json.loads(response.decode('utf-8'))
        log.v(TAG,'Got feedback.')
        if response.get('errCode',0) != 0 or response.get('retcode',0) != 0:
            # something is wrong
            if response.get('retcode',0) == 1202:
                log.e(TAG,'Message sending failed.')
                self.HC.reqAsync(previous['url'],data=previous['data'],
                    headers=previous['headers'],cb=self._callback_send)


    def _parseArg(self,jsStr):
        jsStr=jsStr[jsStr.index('(')+1:len(jsStr)-2]
        return list(map(lambda x:x.strip().strip("'"),jsStr.split(',')))

    def getQHash(self):
        # rewrite from an javascript function
        # see mq_private.js for original version
        if not hasattr(self,'_qhash'):
            x=int(self.uin)
            I=self.ptwebqq
            N=[0,0,0,0]
            i=0
            while i<len(I):
                N[i % 4] ^= ord(I[i])
                i+=1
            V = []
            V.append(x >> 24 & 255 ^ ord('E'))
            V.append(x >> 16 & 255 ^ ord('C'))
            V.append(x >> 8 & 255 ^ ord('O'))
            V.append(x & 255 ^ ord('K'))
            U = [];
            for T in range(8):
                if T%2==0:
                    U.append(N[T>>1])
                else:
                    U.append(V[T>>1])
            N = ["0","1","2","3","4","5","6","7","8","9","A","B","C","D","E","F"]
            V = ""
            for T in range(len(U)):
                V += N[U[T] >> 4 & 15]
                V += N[U[T] & 15]
            self._qhash=V
        return self._qhash

    # def saveVeri(self,filename=None):
    #     if filename==None:
    #         filename=self.uin+'.veri'
        

    # def loadVeri(self,filename):
    #     self.HC.loadCookie(filename)

    def QRVeri(self,showQR=None):
        TAG='Verify'
        # --------------necessary urls--------------
        # urlLogin = "https://ui.ptlogin2.qq.com/cgi-bin/login?daid=164&target=self&style=16&mibao_css=m_webqq&appid=501004106&enable_qlogin=0&no_verifyimg=1&s_url=http%3A%2F%2Fw.qq.com%2Fproxy.html&f_url=loginerroralert&strong_login=1&login_state=10&t=20131024001"
        urlgetQRImage = "https://ssl.ptlogin2.qq.com/ptqrshow?appid=501004106&e=0&l=M&s=5&d=72&v=4&t=0.5"
        urlcheckQRState = "https://ssl.ptlogin2.qq.com/ptqrlogin?webqq_type=10&remember_uin=1&login2qq=1&aid=501004106&u1=http%3A%2F%2Fw.qq.com%2Fproxy.html%3Flogin2qq%3D1%26webqq_type%3D10&ptredirect=0&ptlang=2052&daid=164&from_ui=1&pttype=1&dumy=&fp=loginerroralert&action=0-0-{timer}&mibao_css=m_webqq&t=undefined&g=1&js_type=0&js_ver=10139&login_sig=&pt_randsalt=0"
        # ------------end necessary urls------------

        # get QR image
        if showQR == None:
            # Mac OSX
            showQR = lambda :os.system('open '+self.HC.getImage(urlgetQRImage))
        showQR()

        # check QR verification state
        t=int(time.clock()*10000)+10000 # default clock
        prev=-1
        while True:
            time.sleep(1)
            t+=int(time.clock()*10000)
            res=self._parseArg(self.HC.getText(urlcheckQRState.format(timer=t)))
            if prev!=res[0]:
                if res[0] == '65':
                    log.i(TAG,'QR code expired.')
                    showQR()
                elif res[0] == '66':
                    log.i(TAG,'Please scan the QRCode image shown on your screen.')
                elif res[0] == '67':
                    log.i(TAG,'Please press confirm on your phone.')
                elif res[0] == '0':
                    # QR code verification completed
                    log.i(TAG,res[-2])
                    self.username=res[-1]
                    log.i(TAG,'User name: '+self.username)
                    break
                prev=res[0]

        # first step login
        self.HC.req(res[2])

        # cookie proxy
        self.HC.setCookie('p_skey',self.HC.getCookie('p_skey','.web2.qq.com'),'w.qq.com')
        self.HC.setCookie('p_uin',self.HC.getCookie('p_uin','.web2.qq.com'),'w.qq.com')
        self.ptwebqq=self.HC.getCookie('ptwebqq','.qq.com')

        log.i(TAG,'Saving verification...')
        # save verification now
        # self.saveVeri('./'+username+'.veri')

    def login(self):
        # --------necessary urls & data--------
        urlgetVFWebQQ="http://s.web2.qq.com/api/getvfwebqq?ptwebqq={ptwebqq}&psessionid=&t=1456633306528"
        urlLogin2="http://d1.web2.qq.com/channel/login2"
        postLogin2={'clientid':53999199,'pssessionid':'','status':'online'}
        # ------end necessary urls & data------

        # get vfwebqq
        self.vfwebqq=self.HC.getJson(urlgetVFWebQQ.format(ptwebqq=self.ptwebqq),
            headers=dict(referer='http://s.web2.qq.com/proxy.html'))['result']['vfwebqq']

        # second step login
        postLogin2['ptwebqq']=self.ptwebqq
        j2=self.HC.getJson(urlLogin2,data={'r':json.dumps(postLogin2)})

        self.uin=j2['result']['uin']
        self.psessionid=j2['result']['psessionid']
        self.status=j2['result']['status']
        self.getQHash()
        self.getUserFriends()
        self.getGroupList()
        self.getDiscusList()

    def getUserFriends(self):
        self.fl.parseFriends(self.HC.getText('http://s.web2.qq.com/api/get_user_friends2',
            data={'r':json.dumps({
                'hash':self.getQHash(),
                'vfwebqq':self.vfwebqq})},
            headers=self.defaultHeaders))
        log.i('list','Finished getting friend list.')

    def getGroupList(self):
        self.fl.parseGroups(self.HC.getText('http://s.web2.qq.com/api/get_group_name_list_mask2',
            data={'r':json.dumps({
                'hash':self.getQHash(),
                'vfwebqq':self.vfwebqq})},
            headers=self.defaultHeaders))
        log.i('list','Finished getting group list.')

    def getDiscusList(self):
        self.fl.parseDiscus(self.HC.getText(
            'http://s.web2.qq.com/api/get_discus_list',
            data={'clientid':53999199,
                'psessionid':self.psessionid,
                'vfwebqq':self.vfwebqq,
                't':utime()},
            headers=self.defaultHeaders))
        log.i('list','Finished getting discus group list.')

    def listen(self,join=False):
        urlPoll2='http://d1.web2.qq.com/channel/poll2'
        d={'r':json.dumps({"ptwebqq":self.ptwebqq,"clientid":53999199,
            "psessionid":self.psessionid,"key":""})}
        def l():
            while True:
                r=self.HC.req(urlPoll2,data=d,headers=self.pollHeaders)
                self._callback_receive(r,{'url':urlPoll2,'data':d,'headers':self.pollHeaders})
        t=threading.Thread(name='qqClientListener',target=l)
        t.start()
        if join:
            t.join()

    def sendMessage(self,receiver,content):
        self.msgid = self.msgid + 1
        receiver=int(receiver)
        c=json.dumps([content,["font",{ "name": "宋体","size": 10,
                    "style": [0,0,0],"color": "000000" }]])
        self.HC.reqAsync(
            'http://d1.web2.qq.com/channel/send_buddy_msg2',
            data={'r':json.dumps({
                'to':receiver,'content':c,
                'face':self.fl.f[receiver]['face'],
                'clientid':53999199,'msg_id':self.msgid,
                'psessionid':self.psessionid})},
            headers=self.pollHeaders,
            cb=self._callback_send)

    def addHandler(self,handler):
        handler.qqClt=self
        self.handlers.append(handler)


class qqHandler(object):
    def __init__(self):
        self._qqClt=None

    @property
    def qqClt(self):
        return self._qqClt
    
    @qqClt.setter
    def qqClt(self,value):
        if not isinstance(value,qqClient):
            raise TypeError('qqHandler: not a qqClient object.')
        else:
            self._qqClt = value

    def __getattr__(self,name):
        return self._qqClt.__getattribute__(name)

    def onFail(self,response,previous):
        pass

    def onBuddyMessage(self,uin,msg):
        pass

    def onGroupMessage(self,gin,msg):
        pass
