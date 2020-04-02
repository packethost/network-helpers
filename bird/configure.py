#!/usr/bin/env python3
import os
import sys

from packet_bird import Bird

USE_METADATA = os.getenv("USE_METADATA", "yes")
API_TOKEN = os.getenv("API_TOKEN", None)
INSTANCE_ID = os.getenv("INSTANCE_ID", None)

if __name__ == "__main__":
    if USE_METADATA != "yes":
        if not API_TOKEN:
            sys.exit("Packet API token missing from environment")
        if not INSTANCE_ID:
            sys.exit("Instance ID missing from environment")

    headers = {}
    if API_TOKEN:
        headers["X-Auth-Token"] = API_TOKEN

    bird, bird6 = Bird.http_fetch_bgp(
        use_metadata=(USE_METADATA == "yes"), headers=headers, instance=INSTANCE_ID
    )

    arg_index = sys.argv.index(__file__) + 1
    if "-6" in sys.argv[arg_index:]:
        if bird6.v6_peer_count > 0:
            print(bird6.config)
        else:
            sys.exit("BGP over IPv6 is not enabled")
    else:
        if bird.v4_peer_count > 0:
            print(bird.config)
        else:
            sys.exit("BGP over IPv4 is not enabled")
