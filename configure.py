#!/usr/bin/env python3
import argparse
import os
import sys

from routers.bird import Bird
from routers.helpers import fetch_bgp

USE_METADATA = os.getenv("USE_METADATA", "yes")
API_TOKEN = os.getenv("API_TOKEN", None)
INSTANCE_ID = os.getenv("INSTANCE_ID", None)

if __name__ == "__main__":  # noqa: C901
    if USE_METADATA != "yes":
        if not API_TOKEN:
            sys.exit("Packet API token missing from environment")
        if not INSTANCE_ID:
            sys.exit("Instance ID missing from environment")

    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-r",
        "--router",
        help="the routing daemon to be configured",
        action="store",
        type=str,
        choices=["bird", "bird6", "frr"],
        required=True,
    )
    args = parser.parse_args()

    headers = {}
    if API_TOKEN:
        headers["X-Auth-Token"] = API_TOKEN

    bgp = fetch_bgp(
        use_metadata=(USE_METADATA == "yes"), headers=headers, instance=INSTANCE_ID
    )

    if args.router == "bird":
        bird = Bird(**bgp)
        if bird.v4_peer_count > 0:
            print(bird.config)
        else:
            sys.exit("BGP over IPv4 is not enabled")
    elif args.router == "bird6":
        bird6 = Bird(family=6, **bgp)
        if bird6.v6_peer_count > 0:
            print(bird6.config)
        else:
            sys.exit("BGP over IPv6 is not enabled")
    elif args.router == "frr":
        raise NotImplementedError
    else:
        sys.exit("Unrecognized routing daemon specified")
