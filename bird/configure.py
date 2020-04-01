#!/usr/bin/env python3
import os
import sys

from packet_bird import Bird

USE_METADATA = os.getenv("USE_METADATA", "yes")
API_TOKEN = os.getenv("API_TOKEN", None)
INSTANCE_ID = os.getenv("INSTANCE_ID", None)

if __name__ == "__main__":
    if USE_METADATA == "no":
        if not API_TOKEN:
            sys.exit("Packet API token missing from environment")
        if not INSTANCE_ID:
            sys.exit("Instance ID missing from environment")

    headers = {}
    if API_TOKEN:
        headers["X-Auth-Token"] = API_TOKEN

    r = Bird.http_fetch_bgp(
        use_metadata=(USE_METADATA == "yes"), headers=headers, instance=INSTANCE_ID
    )
    print(r.config)
