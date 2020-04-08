from json.decoder import JSONDecodeError
from typing import Any, Dict, List, Optional

import requests


def fetch_ip_addresses(
    headers: Dict[str, str] = {}, instance: Optional[str] = None
) -> Any:
    url = "https://api.packet.net/devices/{}".format(instance)
    response = requests.get(url, headers=headers)
    try:
        response_payload = response.json()
        if "ip_addresses" not in response_payload:
            return []
        else:
            return response_payload["ip_addresses"]
    except JSONDecodeError as e:
        raise JSONDecodeError(
            "Unable to decode API/metadata response for {}. {}".format(url, e.msg),
            e.doc,
            e.pos,
        )


def fetch_bgp(
    use_metadata: bool = True,
    headers: Dict[str, str] = {},
    instance: Optional[str] = None,
) -> Any:
    url = "https://metadata.packet.net/metadata"
    ip_addresses = []
    if not use_metadata:
        if not instance:
            raise ValueError("Instance ID must be specified when not using metadata")
        url = "https://api.packet.net/devices/{}/bgp/neighbors".format(instance)
        ip_addresses = fetch_ip_addresses(headers=headers, instance=instance)

    response = requests.get(url, headers=headers)

    try:
        response_payload = response.json()
        if not use_metadata:
            response_payload["network"] = {"addresses": ip_addresses}
        return response_payload
    except JSONDecodeError as e:
        raise JSONDecodeError(
            "Unable to decode API/metadata response for {}. {}".format(url, e.msg),
            e.doc,
            e.pos,
        )


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
