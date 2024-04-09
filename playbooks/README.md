# Ansible Playbooks for Kentik

The following playbooks are available today for managing Kentik with Ansible:

- Updating SNMP device settings
  - This playbook will update SNMPv3 and SNMPv2 authentication settings for the devices listing in the inventory that the playbook is ran against. The run this playbook, the user must do the following:
    1. Create an inventory file with the list of devices that will be updated. The device names in this inventory must match the device names in Kentik. The device names will also need to be resolvable by DNS, if not the user will need to add the ip address to the inventory file with the device name like so: `device1 ansible_host=1.1.1.1` 
    2. The user will need to duplicate the template_kentik_snmp_var.yml file under the vars directory and name it credentials.yml. After duplicating it, then add all the appropriate settings to the file.
  - To the Run the playbook, type `ansible-playbook pb_update_kentik_snmp.yml -i inventory_file`

- Sync two address based custom dimensions
  - This playbook will take two custom dimension IDs as input. One ID is the "FROM" (the dimension to be copied) and the second ID is the "TO" (the dimension to sync/copy the FROM).
  - To use this playbook all you need are those two dimensions handy and the credential file.
    - The user will need to duplicate the template_kentik_snmp_var.yml file under the vars directory and name it credentials.yml. After duplicating it, then add all the appropriate settings to the file.
  - Limitions
    - Only values with one address to value mapping is supported.
    - Only ip address values are supported. 
    - The maximum number of populators is unknown for this playbook and may be something you run into.

- Sync Nautobot to Kentik
  - This playbook will use nautbot as an inventory source and take each of the devices from the inventory and verify that it is created in kentik and if not create it, associate it to the right site, and apply the right labels.
  - First compile a list of sites from the device inventory and ensure those sites are created in kentik. 
  - Second compile a list of de-duplicated labels and ensure that the labels are created. 
  - Third, take each device and ensure that it is created in kentik.
  - Fourth, apply labels to the device. 
  - Done
  
-- happy automating
