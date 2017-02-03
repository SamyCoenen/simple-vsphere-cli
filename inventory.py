import atexit
import subprocess
from tools import cli
from tools import tasks
from pyVim import connect
from pyVmomi import vim, vmodl
import deploy_vm_ovf

def get_args():
    """Get command line args from the user.
    """
    parser = cli.build_arg_parser()
    args = parser.parse_args()
    cli.prompt_for_password(args)
    return args


class Inventory:
    def __init__(self, service_instance):
        self.service_instance = service_instance

    def get_vms(self):
        """
        Find a virtual machine by it's name and return it
        """
        return self._get_obj(self.service_instance.RetrieveContent(), [vim.VirtualMachine])

    def _get_obj(self, content, vimtype):
        """
        Get the vsphere object associated with a given text name
        """
        obj = None
        container = content.viewManager.CreateContainerView(content.rootFolder, vimtype, True)
        return container

    def deploy_vm_ovf(self, settings_list, vm_name, vmdk_path, ovf_path):
        list = settings_list
        list['vm_name'] = vm_name
        list['ovf_path'] = ovf_path
        list['vmdk_path'] = vmdk_path
        deploy_vm_ovf.deploy(list)


def main():
    """
    Simple command-line program for changing network virtual machines NIC.
    """

    args = get_args()

    try:

        service_instance = connect.SmartConnect(host=args.host,
                                                user=args.user,
                                                pwd=args.password,
                                                port=int(args.port))

        atexit.register(connect.Disconnect, service_instance)
        inventory = Inventory(service_instance)
        vms = inventory.get_vms()
        width = 15
        widthuuid = 45
        print '{:{width}} {:{widthuuid}} {:{width}} {:{width}}'.format('name ', 'uuid ', 'cpu ', 'ram ', width=width,widthuuid=widthuuid)

        for vm in vms.view:
            print '{:{width}} {:{widthuuid}} {:{width}} {:{width}}'.format(vm.name, vm.summary.config.uuid, str(vm.summary.config.numCpu), str(vm.summary.config.memorySizeMB),width=width,widthuuid=widthuuid)

    except vmodl.MethodFault as error:
        print "Caught vmodl fault : " + error.msg
        return -1

    return 0

# Start program
if __name__ == "__main__":
    main()
