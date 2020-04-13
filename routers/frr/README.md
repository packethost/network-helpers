## FRR

Similar to Bird, FRR is a routing daemon for Linux. It can be used to announce an elastic IP address via BGP from the instance that is currently using it.

### Requirements

* A BGP enabled project and instance
* An elastic IP configured on interface lo

The former can be accomplished via the Packet client portal while the latter can be done via the following two commands (this applies to Ubuntu; network configuration will typically vary by distro):

```bash
echo 'auto lo:0
  iface lo:0 inet static
  address 10.99.182.254
  netmask 255.255.255.255' >> /etc/network/interfaces
```

In the above command, you will replace `10.99.182.254` with your own elastic IP. Then simply bring up interface `lo:0`:

```bash
ifup lo:0
```

### Configuration

#### Method 1: FRR on Baremetal

First install system dependencies. On Ubuntu 18.04 this looks like:

```bash
apt -y update && apt -y install python3.6 python3-pip git libpcre3-dev apt-transport-https ca-certificates curl wget logrotate libc-ares2 libjson-c3 vim systemd procps libreadline7 gnupg2 lsb-release apt-utils
```

Add FRR's apt signing key and configure the FRR repo:

```bash
curl -s https://deb.frrouting.org/frr/keys.asc | apt-key add - && \
    echo deb https://deb.frrouting.org/frr $(lsb_release -s -c) frr-stable | tee -a /etc/apt/sources.list.d/frr.list
```

Now install FRR:

```bash
apt -y update && apt -y install frr frr-pythontools
```

Once installed, we need to enable BGP wiithin FRR's configuration:

```bash
sed -i "s/^bgpd=no/bgpd=yes/" /etc/frr/daemons
```

Now we need to clone the network-helpers repo and install python dependencies:

```bash
cd /opt
git clone https://github.com/packethost/network-helpers.git
cd network-helpers
pip3 install -e .
```

And then apply the FRR configuration using our instance's metadata:

```
./configure.py -r frr | tee /etc/frr/frr.conf 
frr defaults traditional
log syslog informational
ipv6 forwarding
service integrated-vtysh-config
!
!
router bgp 65000
 bgp ebgp-requires-policy
 neighbor V4 peer-group
 neighbor V4 remote-as 65530
 neighbor V4 password somepassword
 neighbor 10.99.182.128 peer-group V4
 neighbor V6 peer-group
 neighbor V6 remote-as 65530
 neighbor V6 password somepassword
 neighbor 2604:1380:1:5f00:: peer-group V6
 !
 address-family ipv4 unicast
  redistribute connected
  neighbor V4 route-map IMPORT in
  neighbor V4 route-map EXPORT out
 exit-address-family
 !
 address-family ipv6 unicast
  redistribute connected
  neighbor V6 activate
  neighbor V6 route-map IMPORT in
  neighbor V6 route-map EXPORT out
 exit-address-family
 !
route-map EXPORT deny 100
!
route-map EXPORT permit 1
 match interface lo
!
route-map IMPORT deny 1
!
line vty
!
```

Lastly, we'll restart FRR:

```bash
systemctl restart frr
```

And then verify our bgp session is up and our desired prefix is being advertised:

```
vtysh

Hello, this is FRRouting (version 7.3).
Copyright 1996-2005 Kunihiro Ishiguro, et al.
# 
```
```
# show bgp summary 

IPv4 Unicast Summary:
BGP router identifier 10.99.182.254, local AS number 65000 vrf-id 0
BGP table version 3
RIB entries 5, using 920 bytes of memory
Peers 2, using 41 KiB of memory
Peer groups 2, using 128 bytes of memory

Neighbor           V         AS MsgRcvd MsgSent   TblVer  InQ OutQ  Up/Down State/PfxRcd
10.99.182.128      4      65530       6       7        0    0    0 00:01:17            0
2604:1380:1:5f00:: 4      65530       7       9        0    0    0 00:01:17 NoNeg

Total number of neighbors 2

IPv6 Unicast Summary:
BGP router identifier 10.99.182.254, local AS number 65000 vrf-id 0
BGP table version 1
RIB entries 1, using 184 bytes of memory
Peers 1, using 20 KiB of memory
Peer groups 2, using 128 bytes of memory

Neighbor           V         AS MsgRcvd MsgSent   TblVer  InQ OutQ  Up/Down State/PfxRcd
2604:1380:1:5f00:: 4      65530       7       9        0    0    0 00:01:17            0

Total number of neighbors 1
```
```
# show ip bgp neighbors 10.99.182.128 advertised-routes
BGP table version is 3, local router ID is 10.99.182.254, vrf id 0
Default local pref 100, local AS 65000
Status codes:  s suppressed, d damped, h history, * valid, > best, = multipath,
               i internal, r RIB-failure, S Stale, R Removed
Nexthop codes: @NNN nexthop's vrf id, < announce-nh-self
Origin codes:  i - IGP, e - EGP, ? - incomplete

   Network          Next Hop            Metric LocPrf Weight Path
*> 10.99.182.254/32 0.0.0.0                  0         32768 ?

Total number of prefixes 1
```

#### Method 2: FRR via Docker

Using your OS's package management utility, install docker, docker-compose and git if not already installed. On Ubuntu 18.04 this looks like:

```bash
apt -y update && apt -y install docker docker-compose git
systemctl enable docker && systemctl start docker
```

Clone the repo:

```bash
cd /opt
git clone https://github.com/packethost/network-helpers.git
```

Build the image:

```bash
cd network-helpers
docker build -f routers/frr/Dockerfile -t local/frr:latest .
```

Up the container:

```bash
cd routers/frr
docker-compose up -d
```

To verify that FRR is configured and up, we can review the container logs:

```
docker logs $(docker ps | awk '$2 == "local/frr:latest" {print $1}')
+ /opt/bgp/configure.py -r frr
+ tee /etc/frr/frr.conf
frr defaults traditional
log syslog informational
ipv6 forwarding
service integrated-vtysh-config
!
!
router bgp 65000
 bgp ebgp-requires-policy
 neighbor V4 peer-group
 neighbor V4 remote-as 65530
 neighbor V4 password somepassword
 neighbor 10.99.182.128 peer-group V4
 neighbor V6 peer-group
 neighbor V6 remote-as 65530
 neighbor V6 password somepassword
 neighbor 2604:1380:1:5f00:: peer-group V6
 !
 address-family ipv4 unicast
  redistribute connected
  neighbor V4 route-map IMPORT in
  neighbor V4 route-map EXPORT out
 exit-address-family
 !
 address-family ipv6 unicast
  redistribute connected
  neighbor V6 activate
  neighbor V6 route-map IMPORT in
  neighbor V6 route-map EXPORT out
 exit-address-family
 !
route-map EXPORT deny 100
!
route-map EXPORT permit 1
 match interface lo
!
route-map IMPORT deny 1
!
line vty
!
+ '[' 0 '!=' 0 ']'
+ /etc/init.d/frr start
Started watchfrr.
+ exec sleep 10000d
```

Lastly, we need to verify that our bgp sessions are established, and the desired prefixes are being exported. FRR has a Cisco-like cli (vtysh) that we can use:

```bash
docker exec -it $(docker ps | awk '$2 == "local/frr:latest" {print $1}') vtysh
frr#
```

Then to check out sessions:

```
frr# show bgp summary 

IPv4 Unicast Summary:
BGP router identifier 172.17.0.1, local AS number 65000 vrf-id 0
BGP table version 3
RIB entries 5, using 920 bytes of memory
Peers 2, using 41 KiB of memory
Peer groups 2, using 128 bytes of memory

Neighbor           V         AS MsgRcvd MsgSent   TblVer  InQ OutQ  Up/Down State/PfxRcd
10.99.182.128      4      65530      37      35        0    0    0 00:15:23            0
2604:1380:1:5f00:: 4      65530      37      34        0    0    0 00:15:23 NoNeg

Total number of neighbors 2

IPv6 Unicast Summary:
BGP router identifier 172.17.0.1, local AS number 65000 vrf-id 0
BGP table version 1
RIB entries 1, using 184 bytes of memory
Peers 1, using 20 KiB of memory
Peer groups 2, using 128 bytes of memory

Neighbor           V         AS MsgRcvd MsgSent   TblVer  InQ OutQ  Up/Down State/PfxRcd
2604:1380:1:5f00:: 4      65530      37      34        0    0    0 00:15:23            0

Total number of neighbors 1
```

And finally to verify that our prefix bound to interface lo is being exported:

```
frr# show ip bgp neighbors 10.99.182.128 advertised-routes 
BGP table version is 3, local router ID is 172.17.0.1, vrf id 0
Default local pref 100, local AS 65000
Status codes:  s suppressed, d damped, h history, * valid, > best, = multipath,
               i internal, r RIB-failure, S Stale, R Removed
Nexthop codes: @NNN nexthop's vrf id, < announce-nh-self
Origin codes:  i - IGP, e - EGP, ? - incomplete

   Network          Next Hop            Metric LocPrf Weight Path
*> 10.99.182.254/32 0.0.0.0                  0         32768 ?

Total number of prefixes 1
```
