import json
from urllib import request,parse

from qqRobot import qqClient,qqHandler
import mLogger as log

class qqTulingHandler(qqHandler):
    def __init__(self,APIKey=None):
        if APIKey==None:
            print('You\'ll have to provide an APIKey first.')
            print('Get it @ http://tuling123.com')
            raise ValueError('APIKey not available')
        else:
            self.APIKey=APIKey

    def onBuddyMessage(self,uin,msg):
        d=parse.urlencode(
            [('key',self.APIKey),('info',msg),('userid',uin)]).encode('utf-8')
        with request.urlopen("http://www.tuling123.com/openapi/api",data=d) as f:
            j=json.loads(f.read().decode('utf-8'))
        log.i('Tuling',':'.join((str(uin),msg)))
        log.i('Tuling','response:'+j['text'])
        self.sendMessage(uin,j['text'])


if __name__=="__main__":
    a=qqClient()
    h=qqTulingHandler(input('API Key:'))
    a.QRVeri()
    # a.loadVeri('./ekTester.veri')
    a.login()

    a.addHandler(h)
    a.listen(join=True)