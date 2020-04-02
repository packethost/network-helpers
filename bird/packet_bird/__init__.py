import os
from json.decoder import JSONDecodeError
from typing import Any, Dict, List, Optional

import requests
from jinja2 import Environment, FileSystemLoader
from jinja2.exceptions import TemplateNotFound


class BirdNeighbor:
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
        for field in BirdNeighbor.REQUIRED_FIELDS:
            if field not in self.__dict__:
                return False

        return True


class Bird:
    @staticmethod
    def http_fetch_ip_addresses(
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

    @staticmethod
    def http_fetch_bgp(
        use_metadata: bool = True,
        headers: Dict[str, str] = {},
        instance: Optional[str] = None,
    ) -> Any:
        url = "https://metadata.packet.net/metadata"
        ip_addresses = []
        if not use_metadata:
            if not instance:
                raise ValueError(
                    "Instance ID must be specified when not using metadata"
                )
            url = "https://api.packet.net/devices/{}/bgp/neighbors".format(instance)
            ip_addresses = Bird.http_fetch_ip_addresses(
                headers=headers, instance=instance
            )

        response = requests.get(url, headers=headers)

        try:
            response_payload = response.json()
            if not use_metadata:
                response_payload["network"] = {"addresses": ip_addresses}
            return (Bird(**response_payload), Bird(family=6, **response_payload))
        except JSONDecodeError as e:
            raise JSONDecodeError(
                "Unable to decode API/metadata response for {}. {}".format(url, e.msg),
                e.doc,
                e.pos,
            )

    def __init__(self, family: int = 4, **kwargs: Any) -> None:
        self.bgp_neighbors = []
        self.v4_peer_count = 0
        self.v6_peer_count = 0
        if "bgp_neighbors" in kwargs:
            for neighbor in kwargs["bgp_neighbors"]:
                self.bgp_neighbors.append(BirdNeighbor(**neighbor))
                if neighbor["address_family"] == 4:
                    self.v4_peer_count = len(neighbor["peer_ips"])
                elif neighbor["address_family"] == 6:
                    self.v6_peer_count = len(neighbor["peer_ips"])

        self.bgp_neighbors = (
            [BirdNeighbor(**neighbor) for neighbor in kwargs["bgp_neighbors"]]
            if "bgp_neighbors" in kwargs
            else []
        )
        try:
            self.ip_addresses = kwargs["network"]["addresses"]
        except KeyError:
            self.ip_addresses = []
        self.config = self.render_config(
            self.build_config(family), "bird.conf.j2"
        ).strip()

    def build_config(self, family: int) -> Dict[str, Any]:
        router_id = None
        for address in self.ip_addresses:
            if (
                address["address_family"] == 4
                and not address["public"]
                and address["management"]
            ):
                router_id = address["address"]
                break

        if not router_id:
            raise LookupError("Unable to determine router id")

        return {
            "bgp_neighbors": [neighbor.__dict__ for neighbor in self.bgp_neighbors],
            "meta": {"router_id": router_id, "family": family},
        }

    def render_config(self, data: Dict[str, Any], filename: str) -> str:
        script_dir = os.path.dirname(__file__)
        search_dir = os.path.join(script_dir, "templates")
        loader = FileSystemLoader(searchpath=search_dir)
        env = Environment(loader=loader)

        try:
            template = env.get_template(filename)
        except TemplateNotFound as e:
            raise TemplateNotFound(
                "Failed to locate bird's configuration template {}.".format(e.message)
            )

        return template.render(data=data)
