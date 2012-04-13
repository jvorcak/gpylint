from gpylint.settings.PylintMessagesManager import PylintMessagesManager
from gpylint.settings.GeneralSettingsManager import GeneralSettingsManager

pmm = PylintMessagesManager()
gsm = GeneralSettingsManager()

class SettingsFilter(object):

    _instance = None

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super(SettingsFilter, cls).__new__(\
                    cls, *args, **kwargs)

        return cls._instance

    def code_is_ignored(self, code):
        return pmm.code_is_ignored(code) or \
                gsm.code_is_ignored(code)
