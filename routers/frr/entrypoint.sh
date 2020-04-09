#!/usr/bin/env bash

set -ux

/opt/bgp/configure.py -r frr | tee /etc/frr/frr.conf

if [ ${PIPESTATUS[0]} != 0 ]; then
    rm -vf /etc/frr/frr.conf
    exit(1)
fi

supervisord -c /opt/bgp/routers/frr/supervisord.conf
