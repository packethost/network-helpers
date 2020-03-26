import json
import os
import pprint
import re
from json.decoder import JSONDecodeError
from typing import Any, Dict

import jinja2
import requests


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

    def __init__(self, **kwargs) -> None:
        self.__dict__.update(kwargs)
        if not self.validate():
            raise LookupError("Failed to validate bgp neighbor")

    def validate(self):
        for field in BirdNeighbor.REQUIRED_FIELDS:
            if field not in self.__dict__:
                return False

        return True


class Bird:
    @staticmethod
    def http_fetch(url, headers: Dict[str, str] = {}, **kwargs) -> Dict[str, Any]:
        response = requests.get(url, headers=headers, params=kwargs)
        try:
            response_payload = response.json()
            return Bird(
                **response_payload,
                has_error=False,
                msg=None,
                status=response.status_code
            )
        except JSONDecodeError as e:
            return Bird(
                has_error=True,
                msg="Unable to decode response from server: {}".format(e),
                status=response.status_code,
            )

    def __init__(self, **kwargs) -> None:
        self.has_error = kwargs["has_error"] if "has_error" in kwargs else False
        self.msg = kwargs["msg"] if "msg" in kwargs else None
        self.status = kwargs["status"] if "status" in kwargs else None
        self.bgp_neighbors = (
            [BirdNeighbor(**neighbor) for neighbor in kwargs["bgp_neighbors"]]
            if "bgp_neighbors" in kwargs.keys()
            else []
        )
        self.config = self.render_config(self.build_config(), "bird.conf.j2").strip()

    def build_config(self):
        import_count = 0
        export_count = 0
        router_id = None
        for neighbor in self.bgp_neighbors:
            import_count += len(neighbor.routes_in)
            export_count += len(neighbor.routes_out)
            if neighbor.address_family == 4:
                router_id = neighbor.customer_ip

        if not router_id:
            raise LookupError("Unable to determine router id")

        return {
            "bgp_neighbors": [neighbor.__dict__ for neighbor in self.bgp_neighbors],
            "meta": {
                "import_count": import_count,
                "export_count": export_count,
                "router_id": router_id,
            },
        }

    def render_config(self, data, filename):
        script_dir = os.path.dirname(__file__)
        search_dir = os.path.join(script_dir, "templates")
        loader = jinja2.FileSystemLoader(searchpath=search_dir)
        env = jinja2.Environment(loader=loader)

        try:
            template = env.get_template(filename)
        except jinja2.exceptions.TemplateNotFound as e:
            return "Failed to locate configuration template"

        return template.render(data=data)
