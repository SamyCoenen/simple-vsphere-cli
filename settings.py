import os
import pickle


class Settings:
    def __init__(self):
        self.path = os.path.join(os.curdir, '.settings_simple_vsphere_cli')

    def ask(self):
        questions = ['host', 'username', 'password', 'port']
        settings_list = {}
        for question in (questions):
            settings_list[question] = raw_input("What's the ESXI or Vcenter " + question + '?\n')
        return settings_list

    def save(self, settings_list):
        with open(self.path, 'w') as settings_file:
            # Save list as object to file
            pickle.dump(settings_list, settings_file)

    def load(self):
        # Does settings file already exist?
        if os.path.isfile(self.path):
            with open(self.path) as settings_file:
                return pickle.load(settings_file)
        else:
            settings_list = self.ask()
            self.save(settings_list)
            return settings_list

    def reset(self):
        settings_list = self.ask()
        self.save(settings_list)
