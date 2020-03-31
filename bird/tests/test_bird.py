import json
import re
import sys
from pathlib import Path
from typing import Any, Dict, List, Tuple

SESSIONS_PER_TYPE: Dict[int, Dict[int, int]] = {
    1: {4: 1, 6: 0},
    2: {4: 0, 6: 1},
    3: {4: 1, 6: 1},
    4: {4: 2, 6: 0},
    5: {4: 0, 6: 2},
    6: {4: 2, 6: 2},
}


def initialize(main: bool = False) -> Tuple[Dict[int, Any], List[Any]]:
    current_dir = Path(__file__).parent.resolve()
    data_dir = current_dir.joinpath("data").resolve()
    if main:
        parent_dir = current_dir.parent.resolve()
        sys.path.insert(0, str(parent_dir))

    test_data = {}
    ip_addresses = []
    data_files = [
        str(item.resolve()) for item in Path(data_dir).glob("*.json") if item.is_file()
    ]

    for file in data_files:
        type_match = re.search(r"\/type([0-9]+)\.json$", file)
        if type_match:
            with open(file, "r") as fd:
                test_data[int(type_match.group(1))] = json.load(fd)
        elif re.search(r"\/ip_addresses\.json$", file):
            with open(file, "r") as fd:
                ip_addresses = json.load(fd)

    return (test_data, ip_addresses)


def test_Bird(main: bool = False) -> None:
    test_data, ip_addresses = initialize(main=main)

    from packet_bird import Bird

    for bgp_type, test in test_data.items():
        test["network"] = {"addresses": ip_addresses}

        # Objects of type BirdNeighbor will self-validate when their
        # constructor is fired; hence we are only checking that each Bird
        # object has the correct number of bgp sessions
        bird = Bird(**test)
        if len(bird.bgp_neighbors) == 1:
            neighbor = bird.bgp_neighbors.pop()
            if neighbor.address_family == 4:
                assert SESSIONS_PER_TYPE[bgp_type][4] == len(neighbor.peer_ips)
                assert SESSIONS_PER_TYPE[bgp_type][6] == 0
            if neighbor.address_family == 6:
                assert SESSIONS_PER_TYPE[bgp_type][4] == 0
                assert SESSIONS_PER_TYPE[bgp_type][6] == len(neighbor.peer_ips)
        else:
            for i in range(len(bird.bgp_neighbors)):
                assert SESSIONS_PER_TYPE[bgp_type][
                    bird.bgp_neighbors[i].address_family
                ] == len(bird.bgp_neighbors[i].peer_ips)


if __name__ == "__main__":
    test_Bird(main=True)
