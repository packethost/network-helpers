from typing import Any, Dict

import pytest
from packet_bird import Bird
from tests.data import initialize

BGP_TYPES = initialize()


@pytest.mark.parametrize(
    "test_input,expected",
    [
        (BGP_TYPES[0], {4: 1, 6: 0}),
        (BGP_TYPES[1], {4: 0, 6: 1}),
        (BGP_TYPES[2], {4: 1, 6: 1}),
        (BGP_TYPES[3], {4: 2, 6: 0}),
        (BGP_TYPES[4], {4: 0, 6: 2}),
        (BGP_TYPES[5], {4: 2, 6: 2}),
    ],
)
def test_Bird(test_input: Dict[str, Any], expected: Dict[int, int]) -> None:
    bird = Bird(**test_input)
    if len(bird.bgp_neighbors) == 1:
        neighbor = bird.bgp_neighbors.pop()
        if neighbor.address_family == 4:
            assert expected[4] == len(neighbor.peer_ips)
            assert expected[6] == 0
        if neighbor.address_family == 6:
            assert expected[4] == 0
            assert expected[6] == len(neighbor.peer_ips)
    else:
        for j in range(len(bird.bgp_neighbors)):
            assert expected[bird.bgp_neighbors[j].address_family] == len(
                bird.bgp_neighbors[j].peer_ips
            )
