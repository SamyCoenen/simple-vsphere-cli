from pyVim import connect

class Connection:
    @staticmethod
    def connect(settings_list):
        return connect.SmartConnect(host=settings_list['host'],
                                                user=settings_list['username'],
                                                pwd=settings_list['password'],
                                                port=int(settings_list['port']))
