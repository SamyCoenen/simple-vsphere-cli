#!/usr/bin/env python
"""
 Written by Tony Allen
 Github: https://github.com/stormbeard
 Blog: https://stormbeard.net/
 This code has been released under the terms of the Apache 2 licenses
 http://www.apache.org/licenses/LICENSE-2.0.html

 Script to deploy VM via a single .ovf and a single .vmdk file.
"""
import sys
reload(sys)
sys.setdefaultencoding("utf-8")
import random
from os import system, path
from sys import exit
from threading import Thread
from time import sleep
from pyVim import connect
from pyVmomi import vim

def get_ovf_descriptor(ovf_path):
    """
    Read in the OVF descriptor.
    """
    if path.exists(ovf_path):
        with open(ovf_path, 'r') as f:
            try:
                ovfd = f.read()
                f.close()
                return ovfd
            except:
                print "Could not read file: %s" % ovf_path
                exit(1)


def get_obj_in_list(obj_name, obj_list):
    """
    Gets an object out of a list (obj_list) whos name matches obj_name.
    """
    for o in obj_list:
        if o.name == obj_name:
            return o
    print ("Unable to find object by the name of %s in list:\n%s" %
           (o.name, map(lambda o: o.name, obj_list)))
    exit(1)


def get_objects(si, args):
    """
    Return a dict containing the necessary objects for deployment.
    """
    # Get datacenter object.
    datacenter_list = si.content.rootFolder.childEntity
    """
    if args.datacenter_name:
        datacenter_obj = get_obj_in_list(args.datacenter_name, datacenter_list)
    else:
    """
    datacenter_obj = datacenter_list[0]

    # Get datastore object.
    datastore_list = datacenter_obj.datastoreFolder.childEntity
    """if args.datastore_name:
        datastore_obj = get_obj_in_list(args.datastore_name, datastore_list)
    elif len(datastore_list) > 0:"""
    datastore_obj = datastore_list[0]
    #else:
     #   print "No datastores found in DC (%s)." % datacenter_obj.name

    # Get cluster object.
    cluster_list = datacenter_obj.hostFolder.childEntity
    """if args.cluster_name:
        cluster_obj = get_obj_in_list(args.cluster_name, cluster_list)
    elif len(cluster_list) > 0:"""
    cluster_obj = cluster_list[0]
    #else:
    #    print "No clusters found in DC (%s)." % datacenter_obj.name

    # Generate resource pool.
    resource_pool_obj = cluster_obj.resourcePool

    return {"datacenter": datacenter_obj,
            "datastore": datastore_obj
            ,"resource pool": resource_pool_obj}


def keep_lease_alive(lease):
    """
    Keeps the lease alive while POSTing the VMDK.
    """
    while(True):
        sleep(5)
        try:
            # Choosing arbitrary percentage to keep the lease alive.
            lease.HttpNfcLeaseProgress(50)
            if (lease.state == vim.HttpNfcLease.State.done):
                return
            # If the lease is released, we get an exception.
            # Returning to kill the thread.
        except:
            return


def randomMAC():
 mac = [ 0x00, 0x0C, 0x29,
 random.randint(0x00, 0x7f),
 random.randint(0x00, 0xff),
 random.randint(0x00, 0xff) ]
 return ':'.join(map(lambda x: "%02x" % x, mac))


def get_obj(content, vimtype, name):
    """
     Get the vsphere object associated with a given text name
    """
    obj = None
    container = content.viewManager.CreateContainerView(content.rootFolder,
                                                        vimtype, True)
    for view in container.view:
        if view.name == name:
            obj = view
            break
    return obj


def deploy(settings_list):

    ovfd = get_ovf_descriptor(settings_list['ovf_path'])
    try:
        si = connect.SmartConnect(host=settings_list['host'],
                                                user=settings_list['username'],
                                                pwd=settings_list['password'],
                                                port=int(settings_list['port']))
    except:
        print "Unable to connect to %s" % settings_list['host']
        exit(1)
    objs = get_objects(si, settings_list)
    manager = si.content.ovfManager
    spec_params = vim.OvfManager.CreateImportSpecParams(diskProvisioning='thin',entityName=settings_list['vm_name'])
    import_spec = manager.CreateImportSpec(ovfd,
                                           objs["resource pool"],
                                           objs["datastore"],
                                           spec_params)
    lease = objs["resource pool"].ImportVApp(import_spec.importSpec, objs["datacenter"].vmFolder)
    while(True):
        if (lease.state == vim.HttpNfcLease.State.ready):
            # Assuming single VMDK.
            url = lease.info.deviceUrl[0].url.replace('*', settings_list['host'])
            # Spawn a dawmon thread to keep the lease active while POSTing
            # VMDK.
            keepalive_thread = Thread(target=keep_lease_alive, args=(lease,))
            keepalive_thread.start()
            # POST the VMDK to the host via curl. Requests library would work
            # too.
            curl_cmd = (
                "curl -Ss -X POST --insecure -T %s -H 'Content-Type: \
                application/x-vnd.vmware-streamVmdk' %s" %
                (settings_list['vmdk_path'], url))
            system(curl_cmd)
            #system is probably not the right method as we don't get anything back from the command. Lets use subprocess:
	    #result = subprocess.check_output(curl_cmd, stderr=subprocess.STDOUT, shell=True)
	    print "injection complete"
	    #print result
	    lease.HttpNfcLeaseComplete()
            keepalive_thread.join()
            #Stop the return and move on to the next step: break the loop and find out what id our generated machine got:
	    break
	    #return 0
        elif (lease.state == vim.HttpNfcLease.State.error):
            print "Lease error: " + lease.state.error
            exit(1)
    #Done uploading
    #Find it

    content = si.RetrieveContent()

    container = content.rootFolder  # starting point to look into
    viewType = [vim.VirtualMachine]  # object types to look for
    recursive = True  # whether we should look into it recursively
    containerView = content.viewManager.CreateContainerView(
            container, viewType, recursive)

    children = containerView.view
    for child in children:
#            print_vm_info(child)
	     if child.summary.config.name == settings_list['vm_name']:
	#	print "inloop" 
	#	print child.summary.config.name
		print settings_list['vm_name']
		print child.summary.config.uuid

		break
	#	print "loopdone"
    connect.Disconnect(si)
