from typing import Any, Dict

import pytest
from routers.frr import FRR
from routers.frr.tests.data import INVALID_RESPONSES
from routers.test_data import initialize

VALID_RESPONSES = initialize()


@pytest.mark.parametrize(
    "test_input,expected,test_type",
    [
        (VALID_RESPONSES[0], {4: 1, 6: 0}, "valid"),
        (VALID_RESPONSES[1], {4: 0, 6: 1}, "valid"),
        (VALID_RESPONSES[2], {4: 1, 6: 1}, "valid"),
        (VALID_RESPONSES[3], {4: 2, 6: 0}, "valid"),
        (VALID_RESPONSES[4], {4: 0, 6: 2}, "valid"),
        (VALID_RESPONSES[5], {4: 2, 6: 2}, "valid"),
        (INVALID_RESPONSES[0], TypeError, "invalid"),  # Non-json response
        (INVALID_RESPONSES[1], ValueError, "invalid"),  # Json response without bgp data
        (
            INVALID_RESPONSES[2],
            TypeError,
            "invalid",
        ),  # Json response with missing fields in bgp_neighbors
        (
            INVALID_RESPONSES[3],
            ValueError,
            "invalid",
        ),  # Json response with no peering sessions in bgp_neighbors
        (
            INVALID_RESPONSES[4],
            LookupError,
            "invalid",
        ),  # Json response with multihop peering sessions but no usable management ip
    ],
)
def test_FRR(test_input: Dict[str, Any], expected: Any, test_type: int) -> None:
    if test_type == "valid":
        frr = FRR(**test_input)
        if len(frr.bgp_neighbors) == 1:
            neighbor = frr.bgp_neighbors.pop()
            if neighbor.address_family == 4:
                assert expected[4] == len(neighbor.peer_ips)
                assert expected[6] == 0
            if neighbor.address_family == 6:
                assert expected[4] == 0
                assert expected[6] == len(neighbor.peer_ips)
        else:
            for j in range(len(frr.bgp_neighbors)):
                assert expected[frr.bgp_neighbors[j].address_family] == len(
                    frr.bgp_neighbors[j].peer_ips
                )
    else:
        try:
            frr = FRR(**test_input)
            assert False
        except Exception as e:
            assert type(e) == expected
