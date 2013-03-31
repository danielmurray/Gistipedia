import geventreactor; geventreactor.install()
from twisted.internet import reactor
from flask import Flask, send_file, url_for, render_template, request, \
  session, redirect, flash, Markup, abort, Response
from socketio.server import SocketIOServer
import os
import hashlib
import socketio
import logger
import logging
import controller
import time
import random
from gevent import monkey; monkey.patch_all()
import gevent

import args

args.init({
  "port": 8000,
  "debug": True
})
if args.get("debug"):
  logging.basicConfig(level=logging.DEBUG)
else:
  logging.basicConfig(level=logging.INFO)

app = Flask(__name__) 

app.config.update(
  SECRET_KEY = hashlib.sha1(os.urandom(24)).digest(),
  DEBUG = args.get("debug")
)

eventLogger = logger.EventLogger()
loxoneController = controller.LoxoneController()
# loxone controller works fine, just have to test registering the listeners and also making sure that sending message through the proxy method works

# singleton controllers
debugController = controller.DebugController()
lightController = controller.LightController(loxoneController)

# add the logger to every controller
map(lambda x: x.add_client(eventLogger), [
  debugController, lightController
])

@app.route("/")
def index():
  return render_template("index.html", debug=request.args.get("debug", False))

@app.route("/ws")
def debugger():
  return render_template("websockets.html")

@app.route("/poke_debug")
def poke_debug():
  for i in range(0, 10):
    debugController.update({"id": "i-%s" % random.randint(0,5), "val1": hashlib.sha1(os.urandom(10)).hexdigest()})
    time.sleep(1)
  return "Poked debug sensor"

@app.route("/socket.io/<path:remaining>")
def socket_path(remaining=None):
  print "New websocket connection"
  socketio.socketio_manage(request.environ, {
    "/debug": debugController,
    "/light": lightController
  }, request)
  return "end"

if __name__ == '__main__':
  import signal
  print "Starting up"
  server = SocketIOServer(('', args.get("port")), app, transports=["websocket", "xhr-polling"])
  
  def stop_handler(signum, stackframe):
      print "Got signal: %s" % signum
      reactor.callFromThread(reactor.stop)
      os.exit(-1)
  signal.signal(signal.SIGINT, stop_handler)
  g = gevent.spawn(reactor.run)
  server.serve_forever()
