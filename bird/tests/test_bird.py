import inspect
import json
import os
import re
import sys
from os import listdir
from os.path import isfile, join
from typing import Dict, List

SESSIONS_PER_TYPE: Dict[int, int] = {
    1: {4: 1, 6: 0},
    2: {4: 0, 6: 1},
    3: {4: 1, 6: 1},
    4: {4: 2, 6: 0},
    5: {4: 0, 6: 2},
    6: {4: 2, 6: 2},
}


def initialize() -> List[str]:
    currentdir = os.path.dirname(
        os.path.abspath(inspect.getfile(inspect.currentframe()))
    )
    parentdir = os.path.dirname(currentdir)
    sys.path.insert(0, parentdir)

    data_path = join(currentdir, "data")

    test_data = {}
    ip_addresses = []
    for file in listdir(data_path):
        absolute_filename = join(data_path, file)
        if isfile(absolute_filename):
            type_match = re.search(r"\/type([0-9]+)\.json$", absolute_filename)
            if type_match:
                with open(absolute_filename, "r") as fd:
                    test_data[int(type_match.group(1))] = json.load(fd)
            elif re.search(r"\/ip_addresses\.json$", absolute_filename):
                with open(absolute_filename, "r") as fd:
                    ip_addresses = json.load(fd)

    return (test_data, ip_addresses)


def test_Bird() -> None:
    test_data, ip_addresses = initialize()

    from packet_bird import Bird

    for bgp_type, test in test_data.items():
        test["network"] = {"addresses": ip_addresses}
        bird = Bird(**test)

        # Objects of type BirdNeighbor will self-validate when their
        # constructor is fired; hence we are only checking that each Bird
        # object has the correct number of bgp sessions
        for neighbor in bird.bgp_neighbors:
            assert (
                len(neighbor.peer_ips)
                == SESSIONS_PER_TYPE[bgp_type][neighbor.address_family]
            )


if __name__ == "__main__":
    test_Bird()
