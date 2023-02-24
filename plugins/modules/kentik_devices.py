'''
This program needs to be able to manage kentik devices. Add them, Remove them, update any piece of information in the device, etc. It will leverage the
Kentik REST API to perform these functions. The module should be idempotent, meaning that if a device already exists it will return a green status. If 
it does not and needs to be added, it will return a yellow status. Simple as that. Same goes for deletion. This means that each function must first be predicated
by a gather function in the code to get all relevant information about the device if any exists. For the add function it will check to see if the device exits, etc.

The following modules will exist:
add_network_device
remove_network_device
update_network_device
'''