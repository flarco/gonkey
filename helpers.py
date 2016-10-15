import yaml, os
from yaml import Loader, SafeLoader
import logging, datetime

# logger = logging.getLogger()
# handler = logging.StreamHandler()
# formatter = logging.Formatter('%(asctime)s %(name)-12s %(levelname)-8s %(message)s')
# handler.setFormatter(formatter)
# logger.addHandler(handler)
# logger.setLevel(logging.INFO)

DIR = os.path.dirname(os.path.realpath(__file__))


def construct_yaml_str(self, node):
    # Override the default string handling function
    # to always return unicode objects
    return self.construct_scalar(node)

Loader.add_constructor(u'tag:yaml.org,2002:str', construct_yaml_str)
SafeLoader.add_constructor(u'tag:yaml.org,2002:str', construct_yaml_str)


class dict2(dict):
  """ Dict with attributes getter/setter. """
  def __getattr__(self, name):
    return self[name]
  
  def __setattr__(self, name, value):
    self[name] = value

def load_settings():
  with open(DIR + '/settings.yml') as settings_file:
    settings = yaml.load(settings_file)
  return settings

def log(text):
  # logger.info(text)
  print('{} >> {}'.format(datetime.datetime.now(), text))

# Get credentials & settings
settings = load_settings()