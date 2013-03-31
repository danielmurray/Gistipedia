"""
socket.io namespaces

Each backbone.js model connects to a namespace
"""
import socketio
from socketio.namespace import BaseNamespace

class BackboneCollectionInstance(BaseNamespace):
  """
  This class is created once per client, used for proxying requests to the
  BackboneCollection singleton.
  """
  
  def __init__(self, collection, *args, **kwargs):
    """
    Collection is an object with the following methods:

    (optional) collection.do_save(data)
    self.collection = None
    """
    self.collection = collection
    BaseNamespace.__init__(self, *args, **kwargs)

  def on_fetch(self, args):
    """
    Websocket fetch event from client.
    """
    self.emit(args["tid"], {"success": True, "data": self.collection.fetch()})

  def on_save(self, args):
    """
    Websocket save event from client.
    """
    self.collection.save(args["data"])
    self.emit(args["tid"], "saved")

  def do_update(self, data):
    """
    Send a websocket update event to the client.
    """
    self.emit("update", data)

class BackboneCollection:
  """
  cache of the current state of the sensors
  dict of model id: {model attributes}
  """
  models = None
  clients = None

  def __init__(self):
    self.models = {}
    self.clients = []

  def __call__(self, *args, **kwargs):
    """
    This is called once for every new connected client.

    It should return a new object used for communicating with the client
    (handling new events, sending data)
    """
    instance = BackboneCollectionInstance(self, *args, **kwargs)
    self.add_client(instance)
    return instance

  def add_client(self, client):
    """
    Websocket-compatible client. Has the following methods:

    client.do_update(data)
    - data = array of model dictionaries
    """
    self.clients.append(client)

  def fetch(self):
    """
    Return an array of all models
    """
    return self.models.values()

  def update(self, data):
    """
    Update(id, data) is called with a dictionary of model attributes whenever a
    sensor value is updated (from a remote API call, over websockets, etc).
    """
    if not "id" in data:
      raise Exception("id attr not in %s" % data)

    self.models[data["id"]] = data

    for client in self.clients:
      client.do_update(data)

  def save(self, data):
    self.models[data["id"]] = data
    self.do_save(data)

  def do_save(self, data):
    """
    Override for each implementation. Not supported by default.
    """
    raise Exception("Save not supported")
