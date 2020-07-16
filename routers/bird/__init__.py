import os
from typing import Any, Dict

from jinja2 import Environment, FileSystemLoader
from jinja2.exceptions import TemplateNotFound
from routers import Router


class Bird(Router):
    def __init__(self, family: int = 4, **kwargs: Any) -> None:
        super().__init__(**kwargs)
        self.family = family
        self.config = self.render_config(self.build_config(), "bird.conf.j2").strip()

    def build_config(self) -> Dict[str, Any]:
        if not self.router_id:
            raise LookupError("Unable to determine router id")

        ipv4_next_hop, ipv6_next_hop = self.multi_hop_gateway

        if self.ipv4_multi_hop and not ipv4_next_hop:
            raise LookupError("Unable to determine IPv4 next hop for multihop peer")
        if self.ipv6_multi_hop and not ipv6_next_hop:
            raise LookupError("Unable to determine IPv6 next hop for multihop peer")

        return {
            "bgp_neighbors": [neighbor._asdict() for neighbor in self.bgp_neighbors],
            "meta": {
                "router_id": self.router_id,
                "family": self.family,
                "ipv4_next_hop": ipv4_next_hop if self.ipv4_multi_hop else None,
                "ipv6_next_hop": ipv6_next_hop if self.ipv6_multi_hop else None,
            },
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
