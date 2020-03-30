#!/usr/bin/env python3
import os
import sys

from packet_bird import Bird

HELPER_URL = os.getenv("HELPER_URL", "https://metadata.packet.net/metadata")
API_TOKEN = os.getenv("API_TOKEN", None)

if __name__ == "__main__":
    if HELPER_URL != "https://metadata.packet.net/metadata" and not API_TOKEN:
        sys.exit("Packet API token missing from environment")

    headers = {}
    if API_TOKEN:
        headers["X-Auth-Token"] = API_TOKEN

    r = Bird.http_fetch(HELPER_URL, headers=headers)
    print(r.config)
