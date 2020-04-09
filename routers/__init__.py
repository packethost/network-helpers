from typing import Any, Dict, List, NamedTuple

BgpNeighbor = NamedTuple(
    "BgpNeighbor",
    [
        ("address_family", int),
        ("customer_as", int),
        ("customer_ip", str),
        ("md5_enabled", bool),
        ("md5_password", str),
        ("multihop", bool),
        ("peer_as", int),
        ("peer_ips", List[str]),
        ("routes_in", List[Dict[str, Any]]),
        ("routes_out", List[Dict[str, Any]]),
    ],
)


class Router:
    def __init__(self, **kwargs: Any) -> None:
        self.bgp_neighbors = []
        self.v4_peer_count = 0
        self.v6_peer_count = 0
        self.bgp_neighbors = []
        if "bgp_neighbors" in kwargs:
            for neighbor in kwargs["bgp_neighbors"]:
                self.bgp_neighbors.append(BgpNeighbor(**neighbor))
                if neighbor["address_family"] == 4:
                    self.v4_peer_count = len(neighbor["peer_ips"])
                elif neighbor["address_family"] == 6:
                    self.v6_peer_count = len(neighbor["peer_ips"])

        try:
            self.ip_addresses = kwargs["network"]["addresses"]
        except KeyError:
            self.ip_addresses = []
