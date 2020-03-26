#!/usr/bin/env bash

set -eux

/opt/bird/configure.py | tee /etc/bird/bird.conf && \
    bird -c /etc/bird/bird.conf -d
