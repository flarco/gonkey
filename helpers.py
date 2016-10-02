import yaml, os
import logging, datetime

logger = logging.getLogger()
handler = logging.StreamHandler()
formatter = logging.Formatter('%(asctime)s %(name)-12s %(levelname)-8s %(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)
logger.setLevel(logging.INFO)

DIR = os.path.dirname(os.path.realpath(__file__))

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
  logger.info(text)

# Get credentials & settings
settings = load_settings()