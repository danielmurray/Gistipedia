"""
Logging endpoint
"""

import logging

class EventLogger:
  def do_update(self, data):
    logging.debug("Sensor update: %s" % data)
