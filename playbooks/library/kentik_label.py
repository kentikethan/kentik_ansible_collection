#!/usr/bin/python

# Copyright: (c) 2018, Terry Jones <terry.jones@example.org>
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)
from __future__ import (absolute_import, division, print_function)
__metaclass__ = type

DOCUMENTATION = r'''
---
module: kentik_label

short_description: This is a module that will perform idempoent operations on kentik label management. 

# If this is part of a collection, you need to use semantic versioning,
# i.e. the version is of the form "2.5.0" and not "2.4".
version_added: "1.0.0"

description: The module will gather the current list of sites from Kentik and create the site if it is not in the list. 

options:
    name:
        description: The name or title of the label.
        required: true
        type: str
    color:
        description: The hexidecimal color code to be applied to the label. Default is a gray color. 
        required: true
        default: \#007090
        type: str
    email:
        description: Email to authenticate to Kentik: KENTIK_EMAIL environment var by default. 
        required: true
        type: str
        default: KENTIK_EMAIL
    token:
        description: The token to authenticate to Kentik: KENTIK_TOKEN envirnment var by default.
        required: true
        type: str
        default: KENTIK_TOKEN
    region:
        description: The reqion that your Kentik portal is located in. 
        required: false
        type: str
        default: US
        choices:
            - US
            - EU

# Specify this value according to your collection
# in format of namespace.collection.doc_fragment_name
# extends_documentation_fragment:
#     - my_namespace.my_collection.my_doc_fragment_name

author:
    - Ethan Angele (@kentikethan)
'''

EXAMPLES = r'''
# Pass in a message
- name: Create a Label
  kentik_label:
    name: ACCESS_SWITCH
    color: \#007090
    state: present

- name: Delete a Label
    kentik_label:
    name: ACCESS_SWITCH
    state: absent
    region: EU

# fail the module
- name: Test failure of the module
  kentik_label:
    name: fail me because wront state
    state: create
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

def buildPayload(module):
    payload = module.params
    del payload['email']
    del payload['token']
    del[payload['state']]
    del [payload["region"]]
    return payload

def gatherLabels(base_url,api_version,auth,module):
    url = f"{base_url}/label/{api_version}/labels"
    payload = {}
    headers = auth
    try:
        response = requests.request("GET", url, headers=headers, data=payload)
        if response.status_code == 200:
            label_data = response.json()
        else:
            module.fail_json(msg=f"gatherLabels: {response.text}")
    except ConnectionError as exc:
        module.fail_json(msg=to_text(exc))
    label_dict = {}
    for label in label_data['labels']:
        label_dict[label['name']] = label['id']
    return label_dict

def compareLabel(label_list, module):
    label=module.params["name"]
    if label in label_list:
        print(f"Label {label} exists")
        return label_list[label]
    else:
        print(f"Label does not exists...")
        return False

def deleteLabel(base_url,api_version,auth,module,label_id):
    print("Deleting Site...")
    url = f"{base_url}/label/{api_version}/labels/{label_id}"
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

def createLabel(base_url,api_version,auth,module,site_object):
    print("Creating Label...")
    url = f"{base_url}/label/{api_version}/labels"

    payload = json.dumps({
        "label": site_object
        })
    headers = auth
    try:
        response = requests.request("POST", url, headers=headers, data=payload)
        label_data = response.json()
        if response.status_code == 200:
             return label_data['label']['id']
        else:
            module.fail_json(msg=response.text)
    except ConnectionError as exc:
        module.fail_json(msg=to_text(exc))

def main():
    argument_spec = dict(
        name=dict(type='str', required=True),
        color=dict(type='str', required=False, default="#007090"),
        email=dict(type='str', required=False, default=os.environ['KENTIK_EMAIL']),
        token=dict(type='str', no_log=True, required=False, default=os.environ['KENTIK_TOKEN']),
        region=dict(type="str", default="US", choices=["US", "EU"]),
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
    if module.params["region"] == "EU":
        base_url = "https://grpc.api.kentik.eu"
    else:
        base_url = "https://grpc.api.kentik.com"
    api_version = "v202210"
    site_object = buildPayload(module)
    result = {"changed": False}
    warnings = list()
    label_list = gatherLabels(base_url,api_version,auth,module)
    label_exists = compareLabel(label_list, module)

    if label_exists:
        if state == "present":
            result["changed"] = False
            result["label_id"] = label_exists
        elif state == "absent":
            label_id = deleteLabel(base_url,api_version,auth,module,label_exists)
            result["changed"] = True
    else:
        if state == "present":
            label_id = createLabel(base_url,api_version,auth,module,site_object)
            result["changed"] = True
            result["label_id"] = label_id
        elif state == "absent":
            result["changed"] = False
    module.exit_json(**result)

if __name__ == '__main__':
    main()