'''
Settings Manager
'''
class SettingsManager(object):

    def save_boolean(self, section, option, value):
        value = {
                    True: 'on',
                    False: 'off'
                }[value]
        self.config.set(section, option, value)

    def get_boolean(self, section, option):
        return self.config.getboolean(section, option)

    def save(self):
        with open(self.CONFIG_FILE, 'w') as configfile:
            self.config.write(configfile)

