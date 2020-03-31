import os
from json.decoder import JSONDecodeError
from typing import Any, Dict, List

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
    def http_fetch_bgp(url: str, headers: Dict[str, str] = {}, **kwargs: Any) -> Any:
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

    def __init__(self, **kwargs: Any) -> None:
        self.has_error = kwargs["has_error"] if "has_error" in kwargs else False
        self.msg = kwargs["msg"] if "msg" in kwargs else None
        self.status = kwargs["status"] if "status" in kwargs else None
        self.bgp_neighbors = (
            [BirdNeighbor(**neighbor) for neighbor in kwargs["bgp_neighbors"]]
            if "bgp_neighbors" in kwargs
            else []
        )
        try:
            self.ip_addresses = kwargs["network"]["addresses"]
        except KeyError:
            self.ip_addresses = []
        self.config = self.render_config(self.build_config(), "bird.conf.j2").strip()

    def build_config(self) -> Dict[str, Any]:
        import_count = 0
        export_count = 0
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
            "meta": {
                "import_count": import_count,
                "export_count": export_count,
                "router_id": router_id,
            },
        }

    def render_config(self, data: Dict[str, Any], filename: str) -> str:
        script_dir = os.path.dirname(__file__)
        search_dir = os.path.join(script_dir, "templates")
        loader = jinja2.FileSystemLoader(searchpath=search_dir)
        env = jinja2.Environment(loader=loader)

        try:
            template = env.get_template(filename)
        except jinja2.exceptions.TemplateNotFound:
            return "Failed to locate configuration template"

        return template.render(data=data)
