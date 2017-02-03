import random

from pyVmomi import vim, vmodl
from tools import tasks


class VirtualMachine:

    @staticmethod
    def generate_mac():
        mac = [ 0x00, 0x16, 0x3e, random.randint(0x00, 0x7f), random.randint(0x00, 0xff), random.randint(0x00, 0xff) ]
        return ':'.join(map(lambda x: "%02x" % x, mac))

    @staticmethod
    def change_mac(vm, service_instance, new_mac=None ):
        device_change = []
        if new_mac is None:
            new_mac = VirtualMachine.generate_mac()
        try:
            for device in vm.config.hardware.device:
                if isinstance(device, vim.vm.device.VirtualEthernetCard):
                    nicspec = vim.vm.device.VirtualDeviceSpec()
                    nicspec.operation = \
                        vim.vm.device.VirtualDeviceSpec.Operation.edit

                    nicspec.device = device
                    nicspec.device.macAddress = new_mac
                    nicspec.device.addressType = 'manual'
                    nicspec.device.macAddress = new_mac

                    nicspec.device.connectable = \
                        vim.vm.device.VirtualDevice.ConnectInfo()
                    nicspec.device.connectable.startConnected = True
                    nicspec.device.connectable.allowGuestControl = True
                    device_change.append(nicspec)
                    break

            config_spec = vim.vm.ConfigSpec(deviceChange=device_change)
            task = vm.ReconfigVM_Task(config_spec)
            tasks.wait_for_tasks(service_instance, [task])
            print "Successfully changed network"

        except vmodl.MethodFault as error:
            print "Caught vmodl fault : " + error.msg
            return -1
