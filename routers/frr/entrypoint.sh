#!/usr/bin/env bash

set -eux

/opt/bgp/configure.py -r frr | tee /etc/frr/frr.conf
if [ ${PIPESTATUS[0]} == 0 ]; then
    echo >> /opt/bgp/routers/frr/supervisord.conf
    cat << EOF >> /opt/bgp/routers/frr/supervisord.conf
[program:frr]
command = frr -c /etc/frr/frr.conf -d
user = root
stdout_logfile = /proc/1/fd/1
sterr_logfile = /proc/1/fd/2
stdout_logfile_maxbytes = 0
stderr_logfile_maxbytes = 0
EOF
    echo >> /opt/bgp/routers/frr/supervisord.conf
else
    rm -vf /etc/frr/frr.conf
fi

supervisord -c /opt/bgp/routers/frr/supervisord.conf
