#!/usr/bin/env bash

set -ux

/opt/bgp/configure.py -r frr | tee /etc/frr/frr.conf

[ ${PIPESTATUS[0]} != 0 ] && exit ${PIPESTATUS[0]}

/etc/init.d/frr start
exec sleep 10000d
