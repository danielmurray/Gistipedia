from twisted.internet import reactor
from autobahn.websocket import WebSocketClientFactory, WebSocketClientProtocol, connectWS
import requests, random, hmac, hashlib, base64
from light_ctrl import *

LOX_ADDR = '130.126.29.12'
PING_TIME = 10

class EchoIncoming(WebSocketClientProtocol):
    def __init__(self):
        self.light_ctrl = light_controller()
        # super(EchoIncoming, self).__init__()

    def onMessage(self,msg, binary):
        msg = self.parseMessage(msg)
        self.light_ctrl.on_message(msg)

    def parseMessage(self, msg):
        ''' parses the incoming message from the main loxone controller'''
        if '{"s":' in msg:
            return self.parseStateMsg(msg)
        elif '{"LL":' in msg:
            return self.parseVerMsg(msg)
        elif '{"LoxLIVE"' in msg:
            return self.parseConfigMsg(msg)
        else:
            return {
                "type":"ERR",
                "msg":None
            }

    def parseConfigMsg(self,msg):
        msg_dict = json.loads(msg)
        uuid_list = msg_dict['UUIDs']['UUID']
        return {
            "type":"config",
            "msg": uuid_list
        }

    def parseVerMsg(self,msg):
        msg_dict = json.loads(msg)
        return {
            "type":"ver",
            "msg":msg_dict
        }

    def parseStateMsg(self,msg):
        #parse the damn string
        states = msg.split('\r\n')
        states = states[:-1] #remove the last empty object
        state_list = []
        for each in states:
            tmp_dict = json.loads(each)['s']
            state_list.append(tmp_dict)
        return{
            "type":"state",
            "msg":state_list
        }
            

    def updateLight(self, n, v):
        pass

    def onOpen(self):
        self.a = 0
        self.initConnection()

    def initConnection(self):
        message = ["jdev/sps/LoxAPPversion","jdev/sps/getloxapp","jdev/sps/enablestatusupdate"]
        if self.a >= len(message):
            return
        self.sendMessage(message[self.a])
        self.a += 1
        reactor.callLater(1,self.initConnection)

    def onClose(self, wasClean, code, reason):
        print "Socket Closed--- Was Clean:"+str(wasClean)+" Code:"+str(code) + " Reason:" +reason




def main_app():
    num = random.random()
    r = requests.get('http://'+LOX_ADDR+'/jdev/sys/getkey?'+str(num))
    if(r.status_code == 200):
        print "Opening Socket---"
        protocol = hmac.new(r.json()['LL']['value'].decode("hex"), "admin:admin", digestmod=hashlib.sha1).digest().encode("hex")
        factory = WebSocketClientFactory("ws://"+LOX_ADDR+"/ws/",protocols = [protocol], debug=True)
        factory.protocol = EchoIncoming
        connectWS(factory)
        reactor.run()
    else:
        print "FAIL!"+r.status_code

if __name__== "__main__":
    main_app()