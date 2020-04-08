#!/usr/bin/env bash

set -eux

# We should only start bird and bird6 if bgp over ipv4 and
# ipv6 is respectively enabled

/opt/bird/configure.py bird | tee /etc/bird/bird.conf
if [ ${PIPESTATUS[0]} == 0 ]; then
    echo >> /opt/bird/supervisord.conf
    cat << EOF >> /opt/bird/supervisord.conf
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

/opt/bird/configure.py bird6 | tee /etc/bird/bird6.conf
if [ ${PIPESTATUS[0]} == 0 ]; then
    echo >> /opt/bird/supervisord.conf
    cat << EOF >> /opt/bird/supervisord.conf
[program:bird6]
command = bird6 -c /etc/bird/bird6.conf -d
user = root
stdout_logfile = /proc/1/fd/1
sterr_logfile = /proc/1/fd/2
stdout_logfile_maxbytes = 0
stderr_logfile_maxbytes = 0
EOF
    echo >> /opt/bird/supervisord.conf
else
    rm -vf /etc/bird/bird6.conf
fi

supervisord -c /opt/bird/supervisord.conf
