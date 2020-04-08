import os
from typing import Any, Dict, List

from helpers import BgpNeighbor
from jinja2 import Environment, FileSystemLoader
from jinja2.exceptions import TemplateNotFound


class FRR:
    def __init__(self, family: int = 4, **kwargs: Any) -> None:
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
