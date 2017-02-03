import os
from settings import Settings
from menu import Menu


def main():
    settings = Settings()
    settings_list = settings.load()
    menu = Menu(settings_list)
    menu.get_choices_main()

if __name__ == '__main__':
    main()
