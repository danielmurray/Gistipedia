from ws import BackboneCollection

import logging

class DebugController(BackboneCollection):
  def do_save(self, data):
    logging.debug("Saved sensor data: %s" % data)

