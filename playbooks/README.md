# Ansible Playbooks for Kentik

The following playbooks are available today for managing Kentik with Ansible:

- Updating SNMP device settings
  1. This playbook will update SNMPv3 authentication settings for the devices listing in the inventory that the playbook is ran against. The run this playbook, the user must do the following:
    - Create an inventory file with the list of devices that will be updated. The device names in this inventory must match the device names in Kentik. The device names will also need to be resolvable by DNS, if not the user will need to add the ip address to the inventory file with the device name like so: `device1 ansible_host=1.1.1.1` 
  2. The user will need to the duplicate the template_kentik_snmp_var.yml file under the vars directory and name it credentials.yml. After duplicating it, then add all the appropriate settings to the file.
  3.To the Run the playbook, type `ansible-playbook pb_update_kentik_snmp.yml -i inventory_file`
