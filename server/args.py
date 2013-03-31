import argparse

config = None

def init(c):
  global config
  config = c
  parser = argparse.ArgumentParser()
  for (key, val) in config.iteritems():
    parser.add_argument("--" + key, type=type(val))
  args = vars(parser.parse_args())
  for (key, val) in args.iteritems():
    if val:
      config[key] = val

def get(key):
  return config[key]
