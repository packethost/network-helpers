#!/usr/bin/python3
import os
import sys

from packet_bird import Bird

INSTANCE_ID = os.getenv("INSTANCE_ID", None)
API_TOKEN = os.getenv("API_TOKEN", None)
API_HOST = os.getenv("API_HOST", "api.packet.net")

if __name__ == "__main__":
    if not INSTANCE_ID:
        sys.exit("Instance ID missing from environment")
    if not API_TOKEN:
        sys.exit("Packet API token missing from environment")

    url = "https://{}/devices/{}/bgp/neighbors".format(API_HOST, INSTANCE_ID)

    r = Bird.http_fetch(url, headers={"X-Auth-Token": API_TOKEN})
    print(r.config)
