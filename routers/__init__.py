from typing import Any, Dict, List, NamedTuple, Optional, Tuple

import jmespath

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
        self.bgp_neighbors: List[BgpNeighbor] = []
        self.v4_peer_count = 0
        self.v6_peer_count = 0
        self.bgp_neighbors = []
        self.bgp_neighbor_dicts = []
        if "bgp_neighbors" in kwargs:
            self.bgp_neighbor_dicts = kwargs["bgp_neighbors"]
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

        try:
            self.ipv4_multi_hop = bool(
                jmespath.search(
                    "[?address_family == `4`].multihop | [0]", self.bgp_neighbor_dicts
                )
            )
            self.ipv6_multi_hop = bool(
                jmespath.search(
                    "[?address_family == `6`].multihop | [0]", self.bgp_neighbor_dicts
                )
            )
        except Exception as e:
            raise LookupError(
                "Unable to parse multihop attribute from bgp_neighbors: {}.".format(
                    e
                )
            )

    @property
    def router_id(self) -> Optional[str]:
        router_id = None
        for address in self.ip_addresses:
            if (
                address["address_family"] == 4
                and not address["public"]
                and address["management"]
            ):
                router_id = address["address"]
                break

        return router_id

    @property
    def multi_hop_gateway(self) -> Tuple[Optional[str], Optional[str]]:
        try:
            ipv4_next_hop = jmespath.search(
                "[?address_family == `4` && public && management].gateway | [0]",
                self.ip_addresses,
            )
            ipv6_next_hop = jmespath.search(
                "[?address_family == `6` && public && management].gateway | [0]",
                self.ip_addresses,
            )
        except Exception as e:
            raise LookupError(
                "Unable to parse static route next hop(s) from instance ip_addresses: {}.".format(
                    e
                )
            )

        return (ipv4_next_hop, ipv6_next_hop)
