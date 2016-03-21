import os
import yaml

__location__ = os.path.realpath(
    os.path.join(os.getcwd(), os.path.dirname(__file__)))

with open(os.path.join(__location__, 'settings.yaml')) as yaml_settings:
    settings = yaml.load(yaml_settings)


class Config(object):
    DEBUG = False
    SECRET_KEY = settings['secret_key']
    DATABASE = settings['database']
    USER = settings['user']


class DevelopmentConfig(Config):
    DEBUG = True
