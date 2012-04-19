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

    PYLINT_SECTION = 'pylint'
    GENERAL_SECTION = 'general'

    SECTIONS = [PYLINT_SECTION, GENERAL_SECTION]

    # config values
    VIM_EDITOR = 'vim'
    VISUAL_EDITOR = 'visual'

    # values (name, section, default)
    EDITOR = 'editor', GENERAL_SECTION, VISUAL_EDITOR


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
            if not config.has_option(self.PYLINT_SECTION, msg):
                config.set(self.PYLINT_SECTION, msg, 'on')
            msgs[msg] = config.getboolean(self.PYLINT_SECTION, msg)
        return msgs

    def code_is_ignored(self, code):
        error_type = MSG_TYPES[code[0]]
        if config.has_option(self.PYLINT_SECTION, error_type):
            return not config.getboolean(self.PYLINT_SECTION, error_type)
        return False

    def set(self, cname, value):
        name, section, default = cname
        config.set(section, name, value)

    def get(self, cname):
        name, section, default = cname
        if config.has_option(section, name):
            return config.get(section, name)
        else:
            return default
