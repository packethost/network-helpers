from typing import Any, Dict, List


class BgpNeighbor:
    REQUIRED_FIELDS = (
        "address_family",
        "customer_as",
        "customer_ip",
        "md5_enabled",
        "md5_password",
        "multihop",
        "peer_as",
        "peer_ips",
        "routes_in",
        "routes_out",
    )

    address_family: int
    customer_as: int
    customer_ip: str
    md5_enabled: bool
    md5_password: str
    multihop: bool
    peer_as: int
    peer_ips: List[str]
    routes_in: List[Dict[str, Any]]
    routes_out: List[Dict[str, Any]]

    def __init__(self, **kwargs: Any) -> None:
        self.__dict__.update(kwargs)
        if not self.validate():
            raise LookupError("Failed to validate bgp neighbor")

    def validate(self) -> bool:
        for field in BgpNeighbor.REQUIRED_FIELDS:
            if field not in self.__dict__:
                return False

        return True


class Router:
    def __init__(self, family: int = 4, **kwargs: Any) -> None:
        self.family = family
        self.bgp_neighbors = []
        self.v4_peer_count = 0
        self.v6_peer_count = 0
        if "bgp_neighbors" in kwargs:
            for neighbor in kwargs["bgp_neighbors"]:
                self.bgp_neighbors.append(BgpNeighbor(**neighbor))
                if neighbor["address_family"] == 4:
                    self.v4_peer_count = len(neighbor["peer_ips"])
                elif neighbor["address_family"] == 6:
                    self.v6_peer_count = len(neighbor["peer_ips"])

        self.bgp_neighbors = (
            [BgpNeighbor(**neighbor) for neighbor in kwargs["bgp_neighbors"]]
            if "bgp_neighbors" in kwargs
            else []
        )
        try:
            self.ip_addresses = kwargs["network"]["addresses"]
        except KeyError:
            self.ip_addresses = []
