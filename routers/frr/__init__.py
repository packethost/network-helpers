import os
from typing import Any, Dict, List

from jinja2 import Environment, FileSystemLoader
from jinja2.exceptions import TemplateNotFound
from routers import Router


class FRR(Router):
    def __init__(self, **kwargs: Any) -> None:
        super().__init__(**kwargs)
        if not self.bgp_neighbors:
            raise ValueError("At least one bgp neighbor is required")
        self.config = self.render_config(self.build_config(), "frr.conf.j2").strip()

    def build_config(self) -> Dict[str, Any]:
        ipv4_next_hop, ipv6_next_hop = self.multi_hop_gateway()

        if self.ipv4_multi_hop and not ipv4_next_hop:
            raise LookupError("Unable to determine IPv4 next hop for multihop peer")
        if self.ipv6_multi_hop and not ipv6_next_hop:
            raise LookupError("Unable to determine IPv6 next hop for multihop peer")

        bgp_neighbors_per_asn: Dict[int, List[Any]] = {}
        for neighbor in self.bgp_neighbors:
            if not neighbor.peer_ips:
                raise ValueError("At least one peer ip per bgp group is required")
            if neighbor.customer_as not in bgp_neighbors_per_asn:
                bgp_neighbors_per_asn[neighbor.customer_as] = []
            bgp_neighbors_per_asn[neighbor.customer_as].append(neighbor._asdict())

        return {
            "bgp_neighbors": bgp_neighbors_per_asn,
            "meta": {"ipv4_next_hop": ipv4_next_hop, "ipv6_next_hop": ipv6_next_hop},
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
                "Failed to locate frr's configuration template {}.".format(e.message)
            )

        return template.render(data=data)
