#!/usr/bin/python

# Copyright: (c) 2018, Terry Jones <terry.jones@example.org>
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)
from __future__ import (absolute_import, division, print_function)
__metaclass__ = type

DOCUMENTATION = r'''
---
module: kentik_device

short_description: This is a module that will perform idempoent operations on kentik device management

# If this is part of a collection, you need to use semantic versioning,
# i.e. the version is of the form "2.5.0" and not "2.4".
version_added: "1.0.0"

description: The module will gather the current list of devices from Kentik and create the device if it is not in the list. 

options:
    device_name:
        description: The name of the device.
        required: true
        type: str
    device_description:
        description: The device description.
        required: false
        type: str
    device_subtype:
        description: The device subtype.
        choices: router, host-nprobe-dns-www, aws-subnet, azure_subnet, cisco_asa, gcp-subnet, istio_beta, open_nms, paloalto, silverpeak
        required: true
        type: str
        default: "router"
    cdn_attr:
        description: If this is a DNS server, you can contribute its queries to Kentik's CDN attribution database. 
        Valid values: "None" or "Y" or "N". ** cdn_attr is required when the device subtype's parent type is "host-nprobe-dns-www"
        required: false
        default: "none"
    device_sample_rate:
        description: The rate at which the device is sampling flows.
        required: true
        type: int
        default: 1
    plan_id:
        description: The ID of the plan to which this device is assigned.
        required: true
        type: int
    site_id:
        description: The ID of the site (if any) to which this device is assigned.
        required: false
        type: str
    sending_ips:
        description: IP addresses from which the device is sending flow.
        required: true
        type: list
    minimize_snmp:
        description: IP addresses from which the device is sending flow.
        required: false
        type: bool
        default: False
    device_snmp_ip:
        description: IP address from which the device is listening on snmp.
        required: false
        type: str
    device_snmp_community:
        description: The SNMP community to use when polling the device.
        required: false
        type: str
    device_snmp_v3_conf:
        username:
            description: The user name to use to authenticate via SNMP v3. 
            required: false
            type: str
        authentication_protocol:
            description: The auth protocol to use via SNMP v3.
            choices: "NoAuth" or "MD5" or "SHA"
            required: false
            type: str
        authentication_passphrase:
            description: AuthenticationPassphrase - the passphrase to use for SNMP v3.
            required: false
            type: str
        privacy_protocol:
            description: PrivacyProtocol - the privacy protocol to use to authenticate via SNMP v3.
            choices: "NoPriv" or "DES" or "AES"
            required: false
            type: str
        privacy_passphrase:
            description: PrivacyPassphrase - the passphrase to use for SNMP v3 privacy protocol.
            required: false
            type: str
    device_bgp_type:
        description: BGP (device_bgp_type) - Device bgp type. 
        Valid values: "none" (use generic IP/ASN mapping), "device" (peer with the device itself), "other_device" (share routing table of existing peered device).
        required: true
        type: str
        default: none
    device_bgp_neighbor_ip:
        description: Your IPv4 peering address.
        required: false
        type: str
    device_bgp_neighbor_ip6:
        description: Your IPv6 peering address.
        required: false
        type: str
    device_bgp_neighbor_asn:
        description: The valid AS number (ASN) of the autonomous system that this device belongs to.
        required: false
        type: str
    device_bgp_password:
        description: Optional BGP MD5 password.
        required: false
        type: str
    use_bgp_device_id:
        description: The ID of the device whose BGP table should be shared with this device.
        required: false
        type: int
    device_bgp_flowspec:
        description: Toggle BGP Flowspec Compatibility for device.
        required: false
        type: bool




# Specify this value according to your collection
# in format of namespace.collection.doc_fragment_name
# extends_documentation_fragment:
#     - my_namespace.my_collection.my_doc_fragment_name

author:
    - Ethan Angele (@kentikethan)
'''

EXAMPLES = r'''
# Pass in a message
- name: Create a device
  kentik_device:
    name: edge_la1_001
    description: Edge router 1 in la data center
    sampleRate: 10
    type: router
    planId: 12345
    siteId: 12345
    flowSendingIp: 192.168.0.1
    snmpVersion: v2c
    snmpIp: 192.168.0.1
    snmpCommunity: myPreciousCommunity
    bgpType: device
    bgpNeighborIp: 192.168.0.1
    bgpNeighborAsn: 65001
    deviceBgpPassword: myPreciousPassword
    deviceBgpFlowspec: True


# fail the module
- name: Test failure of the module
  kentik_device:
    name: just_the_name_nothing_else_fail
'''

RETURN = r'''
# These are examples of possible return values, and in general should use other names for return values.
original_message:
    description: The original name param that was passed in.
    type: str
    returned: always
    sample: 'hello world'
message:
    description: The output message that the test module generates.
    type: str
    returned: always
    sample: 'goodbye'
'''

from ansible.module_utils.basic import AnsibleModule
from ansible.module_utils._text import to_text
import requests
import json
import os
from kentik_site import (
    gatherSites,
    compareSite
)
from kentik_label import (
    gatherLabels
)

def buildLabels(base_url,api_version,auth,module):
    api_version = "v202210"
    current_labels = gatherLabels(base_url,api_version,auth,module)
    label_ids = []
    for label in module.params['labels']:
        if label in current_labels:
            label_ids.append(current_labels[label])
        elif label == "":
            continue
        else:
            module.fail_json(msg=f"Label {label} does not exist.")
    return label_ids

def buildPayload(base_url, api_version, auth, module):
    payload = module.params
    del payload['email']
    del payload['token']
    del[payload['state']]
    payload['title'] = module.params['site_name']
    del[payload['site_name']]
    site_list = gatherSites(base_url,"/site/v202211",auth,module)
    site_id = compareSite(site_list, module)
    payload['site_id'] = int(site_id)
    plan_dict = gatherPlans(auth,module)
    plan_id = comparePlan(plan_dict,module)
    payload['plan_id'] = int(plan_id)
    del[payload['plan_name']]
    del[payload['labels']]
    del[payload['title']]
    return payload

def gatherPlans(auth,module):
    url = "https://api.kentik.com/api/v5/plans"
    payload = {}
    headers = auth
    try:
        response = requests.request("GET", url, headers=headers, data=payload)
        if response.status_code == 200:
            plan_data = response.json()
        else:
            module.fail_json(function='gatherPlans',msg=response.text)
    except ConnectionError as exc:
        module.fail_json(msg=to_text(exc))
    plan_dict = {}
    for plan in plan_data['plans']:
        plan_dict[plan['name']] = plan['id']
    return plan_dict

def comparePlan(plan_dict, module):
    plan=module.params["plan_name"]
    if plan in plan_dict:
        print("Plan exists")
        return plan_dict[plan]
    else:
        print("Plan does not exists")
        module.fail_json(msg=f"Plan {plan} does not exist.")

def gatherDevices(base_url,api_version,auth,module):
    url = f"{base_url}/device/{api_version}/device"
    payload = {}
    headers = auth

    try:
        response = requests.request("GET", url, headers=headers, data=payload)
        device_data = response.json()
    except ConnectionError as exc:
        module.fail_json(msg=to_text(exc))
    device_dict = {}
    for device in device_data['devices']:
        device_dict[device['deviceName']] = device['id']
    return device_dict

def compareDevice(device_list, module):
    device=module.params["device_name"]
    if device in device_list:
        print('Device exists')
        return device_list[device]
    else:
        print("Device does not exists")
        return False

def compareLabels(base_url,api_version,auth,module,device_id,labels):
    url = f"{base_url}/device/{api_version}/device/{device_id}"
    payload = {}
    headers = auth
    try:
        response = requests.request("GET", url, headers=headers, data=payload)
        if response.status_code == 200:
            device_data = response.json()
            device_labels = []
            for device_label in device_data['device']['labels']:
                device_labels.append(device_label["id"])
            if labels == device_labels:
                return False
            else:
                return labels
        else:
            module.fail_json(msg=response.text)
    except ConnectionError as exc:
        module.fail_json(function='compareLables',msg=to_text(exc))
    
def deleteDevice(base_url,api_version,auth,device_id,module):
    print("Deleting Site...")
    url = f"{base_url}/device/{api_version}/device/{device_id}"
    payload = {}
    headers = auth
    try:
        response = requests.request("DELETE", url, headers=headers, data=payload)
        if response.status_code == 200:
            return
        else:
            module.fail_json(msg=response.text)
    except ConnectionError as exc:
        module.fail_json(msg=to_text(exc))

def createDevice(base_url,api_version,auth,module,device_object):
    print("Creating Device...")
    url = f"{base_url}/device/{api_version}/device"
    payload = json.dumps({
        "device": device_object
        })
    headers = auth
    try:
        response = requests.request("POST", url, headers=headers, data=payload)
        if response.status_code == 200:
            device_data = response.json()
            return device_data['device']['id']
        else:
            module.fail_json(function="createDevice",stats_code=response.status_code,msg=response.text)
    except ConnectionError as exc:
        module.fail_json(function='createDevice',msg=to_text(exc))

def updateDeviceLabels(base_url,api_version,auth,module,device_id,labels):
    print("Updating Device Labels...")
    url = f"{base_url}/device/{api_version}/device/{device_id}/labels"
    headers = auth
    labels_list = []
    for label in labels:
        label_dict = {"id": int(label)}
        labels_list.append(label_dict)
    payload = json.dumps({
        "id": device_id,
        "labels": labels_list
    })
    try:
        response = requests.request("PUT", url, headers=headers, data=payload)
        if response.status_code == 200:
            device_data = response.json()
        else:
            module.fail_json(function='updateDeviceLabels',msg=response.text)
    except ConnectionError as exc:
        module.fail_json(function='updateDeviceLabels',msg=to_text(exc))

def main():
    base_url = "https://grpc.api.kentik.com"
    api_version = "v202308beta1"
    argument_spec = dict(
        device_name=dict(type='str', required=True),
        device_description=dict(type='str', required=False, default='Added by Ansible'),
        device_subtype=dict(type='str', required=False, default='router',choices=['router', 'host-nprobe-dns-www', 'aws-subnet', 'azure_subnet', 'cisco_asa', 'gcp-subnet', 'istio_beta', 'open_nms', 'paloalto',' silverpeak']),
        cdn_attr=dict(type='str', required=False, choices=['y','n']),
        device_sample_rate=dict(type='int', required=False, default=1),
        plan_name=dict(type='str', required=True),
        site_name=dict(type='str', required=False),
        sending_ips=dict(type='list', required=True),
        minimize_snmp=dict(type='bool', required=False, default=False),
        device_snmp_ip=dict(type='str', required=False),
        device_snmp_community=dict(type='str', required=False),
        device_snmp_v3_conf=dict(type='dict', required=False),
        device_bgp_type=dict(type='str', required=False, choices=['none','device','other_device'], default='none'),
        device_bgp_neighbor_ip=dict(type='str', required=False),
        device_bgp_neighbor_ip6=dict(type='str', required=False),
        device_bgp_neighbor_asn=dict(type='str', required=False),
        device_bgp_password=dict(type='str', required=False, no_log=True),
        use_bgp_device_id=dict(type='int', required=False),
        device_bgp_flowspec=dict(type='bool', required=False),
        nms=dict(type='dict', required=False),
        labels=dict(type='list',required=False),
        email=dict(type='str', required=False, default=os.environ['KENTIK_EMAIL']),
        token=dict(type='str', no_log=True, required=False, default=os.environ['KENTIK_TOKEN']),
        state=dict(default="present", choices=["present", "absent"])
    )
    module = AnsibleModule(
        argument_spec=argument_spec,
    )
    result = {"changed": False}
    warnings = list()
    state = module.params['state']
    auth = {
        'X-CH-Auth-Email': module.params['email'], 
        'X-CH-Auth-API-Token': module.params['token'], 
        'Content-Type': 'application/json'
        }
    if module.params['labels']:
        print("Labels found")
        labels = buildLabels(base_url, api_version, auth, module)
    else:
        print("No Labels found")
        labels = False
    device_object = buildPayload(base_url, api_version, auth, module)
    result = {"changed": False}
    device_list = gatherDevices(base_url,api_version,auth,module)
    device_id = compareDevice(device_list, module)

    if device_id:
        labels = compareLabels(base_url,api_version,auth,module,device_id,labels)
        if state == "present":
            result["changed"] = False
        elif state == "absent":
            deleteDevice(base_url,api_version,auth,device_id,module)
            result["changed"] = True
    else:
        if state == "present":
            device_id = createDevice(base_url,api_version,auth,module,device_object)
            result["changed"] = True
            result['device_id'] = device_id
        elif state == "absent":
            result["changed"] = False
    if labels and len(labels) > 0:
        updateDeviceLabels(base_url,api_version,auth,module,device_id,labels)
        result["changed"] = True
        
    module.exit_json(**result)

if __name__ == '__main__':
    main()