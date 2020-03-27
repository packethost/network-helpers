## Bird

Bird is an open source routing daemon for Unix-like systems. It can be used to establish bgp sessions between client instances and the packet network.

An elastic IP address can simply be announced via Bird from the instance that is currently using it, thereby making it easy to freely move the IP from one instance to another within the same project.

### Requirements

* A BGP enabled project
* An elastic IP configured on interface lo

### Example 1: Configuring Bird on Baremetal

