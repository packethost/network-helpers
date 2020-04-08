import os
from typing import Any, Dict, List

from jinja2 import Environment, FileSystemLoader
from jinja2.exceptions import TemplateNotFound
from routers import Router


class FRR(Router):
    def __init__(self, family: int = 4, **kwargs: Any) -> None:
        super().__init__(family=family, **kwargs)
        self.config = self.render_config(
            self.build_config(self.family), "frr.conf.j2"
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

        bgp_neighbors_per_asn = {}
        for neighbor in self.bgp_neighbors:
            if neighbor.customer_as not in bgp_neighbors_per_asn:
                bgp_neighbors_per_asn[neighbor.customer_as] = []
            bgp_neighbors_per_asn[neighbor.customer_as].append(neighbor.__dict__)

        return {
            "bgp_neighbors": bgp_neighbors_per_asn,
            "meta": {"router_id": router_id, "family": self.family},
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
