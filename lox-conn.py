import requests, random, hmac, hashlib, base64
from websocket import create_connection

LOX_ADDR = '130.126.29.12'

num = random.random()
r = requests.get('http://'+LOX_ADDR+'/jdev/sys/getkey?'+str(num))

if(r.status_code == 200):
  protocol = hmac.new(r.json()['LL']['value'].decode("hex"), "admin:admin", digestmod=hashlib.sha1).digest().encode("hex")
  ws = create_connection("ws://"+LOX_ADDR+"/ws/",header=["Sec-WebSocket-Protocol: "+protocol])
  
  # do someting
  #message = "dev/sps/io/BreadButton2/pulse"
  message = "dev/sps/enablestatusupdate"
  ws.send(message)
  print "sending: "+message
  
  print "receiving..."
  response = ws.recv()
  if response is None:
    print "no response"
  else:
    print "response received"
  print response
  
  ws.close()
else:
  print "getKey failed. Code: "+str(r.status_code)
