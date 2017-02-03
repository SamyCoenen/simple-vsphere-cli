from pick import pick
from settings import Settings
from inventory import Inventory
from connection import Connection
from virtual_machine import VirtualMachine

class Menu:
    def __init__(self, settings_list):
        self.settings_list = settings_list
        self.title = 'Please choose an option: '
        self.options_main = ['Inventory', 'Reconfigure connection settings', 'Exit']
        self.options_inventory = ['virtual machines', 'datastores', 'Exit']
        self.options_vm = ['Quick Info', 'Start', 'Shutdown', 'Change Settings', 'Exit']
        self.options_vm_hardware = ['Change mac', 'Add disk','Return', 'Exit']
        self.inventory = None

    def get_choices_main(self):
        chosen_option, index = pick(self.options_main, self.title)
        if index == 0:
            self.inventory = Inventory(Connection.connect(self.settings_list))
            self.get_choices_inventory()
        elif index == 1:
            settings = Settings()
            settings.reset()
            self.get_choices_inventory()
        elif index == 2:
            exit(0)

    def get_choices_inventory(self):
        chosen_option, index = pick(self.options_inventory, self.title)
        if index == 0:
            self.get_list_vms()
        elif index == 1:
            self.get_list_datastores()
        elif index == 2:
            exit(0)

    def get_list_vms(self):
        width = 15
        width_uuid = 45
        vms = self.inventory.get_vms()
        overview = []
        title ='{:{width}} {:{widthuuid}} {:{width}} {:{width}} {:{width}}'.format('name ', 'uuid ', 'cpu ', 'ram ', 'powerstate ', width=width,
                                                                         widthuuid=width_uuid)
        overview.append('New Virtual Machine')
        for vm in vms.view:
            overview.append('{:{width}} {:{widthuuid}} {:{width}} {:{width}} {:{width}}'.format(vm.name, vm.summary.config.uuid,
                                                                              str(vm.summary.config.numCpu),
                                                                              str(vm.summary.config.memorySizeMB), vm.summary.runtime.powerState,
                                                                              width=width, widthuuid=width_uuid))
        overview.append('\n')
        overview.append('\nExit')
        chosen_option, index = pick(overview, title)
        if index == 0:
            self.inventory.deploy_vm_ovf(self.settings_list, 'samymaaktedit', '../deployscripts1/disk-0.vmdk', '../deployscripts1/TestVM.ovf')
        # if last element, exit
        if index == len(overview) - 1:
            exit(0)
        # everything before blank line
        elif index < len(overview) - 2:
            self.get_choices_vm(vms.view[index])


    def get_list_datastores(self):
        return None

    def get_choices_vm(self, vm):
        title = 'Current virtual machine: ' + vm.name
        chosen_option, index = pick(self.options_vm, title)
        # if last element, exit
        if index == len(self.options_vm) - 1:
            exit(0)
        elif index == 0:
            print vm.summary
            user_input = raw_input('Press enter to return\n')
            if user_input == "":
                self.get_choices_vm(vm)
            user_input = raw_input('This program will exit now, type STAY to return\n')
            if str.lower(user_input) == str.lower('stay'):
                self.get_choices_vm(vm)
            print 'Bye!'
            exit(0)
        elif index == 3:
            self.get_choices_vm_hardware(vm)

    def get_choices_vm_hardware(self, vm):
        chosen_option, index = pick(self.options_vm_hardware, self.title)
        # if last element, exit
        if index == len(self.options_vm_hardware) - 1:
            exit(0)
        elif index == 0:
            VirtualMachine.change_mac(vm, self.inventory.service_instance)
        elif index == 2:
            exit(0)

