'''
Settings module responsible for loading and saving general settings
Author: Jan Vorcak <vorcak@mail.muni.cz>
'''

import ConfigParser

from pylint.lint import MSG_TYPES
from gpylint.settings import SettingsManager

CONFIG_FILE = 'settings.ini'
config = ConfigParser.SafeConfigParser()
config.read(CONFIG_FILE)

class GeneralSettingsManager(SettingsManager):

    _instance = None

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super(GeneralSettingsManager, cls).__new__(\
                    cls, *args, **kwargs)

        return cls._instance

    SECTIONS = ['pylint']

    def __init__(self):

        self.config = config
        self.CONFIG_FILE = CONFIG_FILE

        # make sure that all sections exists
        for section in self.SECTIONS:
            if not config.has_section(section):
                config.add_section(section)

    def get_pylint_msgs_types(self):
        msgs = {}
        for msg in MSG_TYPES.values():
            if not config.has_option('pylint', msg):
                config.set('pylint', msg, 'on')
            msgs[msg] = config.getboolean('pylint', msg)
        return msgs

