'''
Settings module responsible for loading and saving settings
Author Jan Vorcak <vorcak@mail.muni.cz>
'''

import ConfigParser

from pylint.lint import MSGS, MSG_TYPES, PyLinter

CONFIG_FILE = 'pylint_settings.ini'
config = config = ConfigParser.SafeConfigParser()
config.read(CONFIG_FILE)

class PylintMessagesManager(object):

    _instance = None

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super(PylintMessagesManager, cls).__new__(\
                    cls, *args, **kwargs)

        return cls._instance

    # dictionary where k=>v , checker_name => dict
    #   where dict k=>v , error_msg => (msg, description)
    # example:
    # {'logging': 
    #         {'E1205': ('Too many arguments for logging format string',
    #                    'Used when a logging format string is given too few
    #                     arguments.'),
    #          'W1201': ('Specify string format arguments as logging function
    #                     parameters', 'Used when a logging statement has a 
    #                     call form of "logging.<logging method>(format_string
    #                     % (format_args...))"',
    #          ...
    #         }
    # }
    msgs = {}

    def __init__(self):


        linter = PyLinter()
        linter.load_default_plugins()
        linter.read_config_file()
        linter.load_config_file()

        for checkers in linter._checkers.values():
            for checker in checkers:

                # for each checker add section to the config
                if not config.has_section(checker.name):
                    config.add_section(checker.name)

                # construct dictionary from the pylint checkers msgs
                if checker.name not in self.msgs.keys():
                    self.msgs[checker.name] = dict()
                self.msgs[checker.name].update(checker.msgs)

        for section, dictionary in self.msgs.iteritems():
            for code in dictionary.keys():
                if not config.has_option(section, code):
                    config.set(section, code, 'on')

    def save_boolean(self, section, option, value):
        value = {
                    True: 'on',
                    False: 'off'
                }[value]
        config.set(section, option, value)

    def get_boolean(self, section, option):
        return config.getboolean(section, option)

    def get_pylint_msgs(self):
        return self.msgs

    def save(self):
        with open(CONFIG_FILE, 'w') as configfile:
            config.write(configfile)

