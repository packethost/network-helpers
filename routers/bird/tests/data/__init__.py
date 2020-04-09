from typing import Any, List

INVALID_RESPONSES: List[Any] = [
    "<html>404 Error</html>",
    {"errors": ["Not found"]},
    {
        "bgp_neighbors": [
            {
                "md5_enabled": True,
                "md5_password": "ValidPassword123",
                "multihop": True,
                "peer_as": 65530,
                "peer_ips": [
                    "fc00:0000:0000:0000:0000:0000:0000:000e",
                    "fc00:0000:0000:0000:0000:0000:0000:000f",
                ],
                "routes_in": [
                    {"exact": False, "route": "2604:1380:1:7400::/56"},
                    {"exact": False, "route": "2604:1380:4111:2300::/56"},
                ],
                "routes_out": [],
            }
        ]
    },
    {
        "bgp_neighbors": [
            {
                "address_family": 4,
                "customer_as": 65000,
                "customer_ip": "10.99.182.129",
                "md5_enabled": True,
                "md5_password": "ValidPassword123",
                "multihop": False,
                "peer_as": 65530,
                "peer_ips": [],
                "routes_in": [
                    {"exact": False, "route": "10.1.0.0/31"},
                    {"exact": False, "route": "10.2.0.0/29"},
                ],
                "routes_out": [],
            },
            {
                "address_family": 6,
                "customer_as": 65000,
                "customer_ip": "2604:1380:4111:2300::1",
                "md5_enabled": True,
                "md5_password": "ValidPassword123",
                "multihop": False,
                "peer_as": 65530,
                "peer_ips": [],
                "routes_in": [
                    {"exact": False, "route": "2604:1380:1:7400::/56"},
                    {"exact": False, "route": "2604:1380:4111:2300::/56"},
                ],
                "routes_out": [],
            },
        ]
    },
]
