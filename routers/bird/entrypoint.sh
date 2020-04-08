#!/usr/bin/env bash

set -eux

# We should only start bird and bird6 if bgp over ipv4 and
# ipv6 is respectively enabled

/opt/routers/configure.py bird | tee /etc/bird/bird.conf
if [ ${PIPESTATUS[0]} == 0 ]; then
    echo >> /opt/routers/supervisord.conf
    cat << EOF >> /opt/routers/supervisord.conf
[program:bird]
command = bird -c /etc/bird/bird.conf -d
user = root
stdout_logfile = /proc/1/fd/1
sterr_logfile = /proc/1/fd/2
stdout_logfile_maxbytes = 0
stderr_logfile_maxbytes = 0
EOF
else
    rm -vf /etc/bird/bird.conf
fi

/opt/routers/configure.py bird6 | tee /etc/bird/bird6.conf
if [ ${PIPESTATUS[0]} == 0 ]; then
    echo >> /opt/routers/supervisord.conf
    cat << EOF >> /opt/routers/supervisord.conf
[program:bird6]
command = bird6 -c /etc/bird/bird6.conf -d
user = root
stdout_logfile = /proc/1/fd/1
sterr_logfile = /proc/1/fd/2
stdout_logfile_maxbytes = 0
stderr_logfile_maxbytes = 0
EOF
    echo >> /opt/routers/supervisord.conf
else
    rm -vf /etc/bird/bird6.conf
fi

supervisord -c /opt/routers/supervisord.conf
