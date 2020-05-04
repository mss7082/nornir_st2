import os
from pprint import pprint
from typing import Any, Dict, List, Optional, Union

from nornir.core.deserializer.inventory import Inventory, HostsDict


import requests


class NBExInventory(Inventory):
    def __init__(
        self,
        nb_url: Optional[str] = None,
        nb_token: Optional[str] = None,
        use_slugs: bool = True,
        ssl_verify: Union[bool, str] = True,
        flatten_custom_fields: bool = True,
        filter_parameters: Optional[Dict[str, Any]] = None,
        **kwargs: Any,
    ) -> None:
        """

    Netbox Extended Plugin

    nb_url: Netbox url, defaults to http://localhost:8080.
    You can also use env variable NB_URL
    nb_token: Netbox token. You can also use env variable NB_TOKEN
    use_slugs: Whether to use slugs or not
    ssl_verify: Enable/disable certificate validation or provide path to CA bundle file
    flatten_custom_fields: Whether to assign custom fields directly to the host or not
    filter_parameters: Key-value pairs to filter down host

    """
        filter_parameters = filter_parameters or {}
        nb_url = nb_url or os.environ.get("NB_URL", "http://localhost:8080")
        nb_token = nb_token or os.environ.get(
            "NB_TOKEN", "jkdbfgjklsbdfugbsodiufbgsldfjbsdf"
        )

        session = requests.Session()
        session.headers.update({"Authorization": f"Token {nb_token}"})
        session.verify = ssl_verify

        # Fetch all deviced from Netbox
        # Netbox's API uses Pagination, Fetch until no next

        url = f"{nb_url}/api/dcim/devices/?limit=0"
        ip_url = f"{nb_url}/api/ipam/ip-addresses?device_id="
        nb_devices: List[Dict[str, Any]] = []

        while url:
            r = session.get(url, params=filter_parameters)

            if not r.status_code == 200:
                raise ValueError(
                    f"Failed to get the devices from Netbox instance {nb_url}"
                )

            resp = r.json()
            nb_devices.extend(resp.get("results"))

            url = resp.get("next")

        hosts = {}
        for d in nb_devices:
            host: HostsDict = {"data": {}}

            # Add the value for IP address
            if d.get("primary_ip", {}):
                host["hostname"] = d["primary_ip"]["address"].split("/")[0]

            # Add the values that dont have an option for 'slug'
            host["data"]["serial"] = d["serial"]
            host["data"]["vendor"] = d["device_type"]["manufacturer"]["name"]
            host["data"]["asset_tag"] = d["asset_tag"]

            if flatten_custom_fields:
                for cf, value in d["custom_fields"].items():
                    host["data"][cf] = value
            else:
                host["data"]["custom_fields"] = d["custom_fields"]

            # Add values that have an option for 'slug'
            if use_slugs:
                host["data"]["site"] = d["site"]["slug"]
                host["data"]["role"] = d["device_role"]["slug"]
                host["data"]["model"] = d["device_type"]["slug"]

                # Attempt to add 'platform' based of value in slug
                host["platform"] = d["platform"]["slug"] if d["platform"] else None
            else:
                host["data"]["site"] = d["site"]["name"]
                host["data"]["role"] = d["device_role"]
                host["platform"] = d["platform"]

            # Get the IP addresses assigned to the interfaces of the host
            host["data"]["interfaces"] = self._get_interfaces_IP(
                nb_url, ssl_verify, nb_token, d["id"]
            )

            # Assign temporary dict to outer Dict
            # Netbos allows devices to be unnamed, but the Nornir model doesn't.
            # If a device is unnamed, set the name to the id of the device in netbox
            hosts[d.get("name") or d.get("id")] = host

        super().__init__(hosts=hosts, groups={}, defaults={}, **kwargs)

    def _get_interfaces_IP(self, nb_url, ssl_verify, nb_token, host_id):
        interfaces = {}
        interface_list = []
        result_list = []
        ip_results: List[Dict[str, Any]] = []
        ip_url = f"{nb_url}/api/ipam/ip-addresses?device_id={host_id}"

        session = requests.Session()
        session.headers.update({"Authorization": f"Token {nb_token}"})
        session.verify = ssl_verify

        while ip_url:
            r = session.get(ip_url)

            if not r.status_code == 200:
                raise ValueError(
                    f"Failed to get the IP addresses from Netbox instance {nb_url}"
                )

            resp = r.json()
            ip_results.extend(resp.get("results"))

            ip_url = resp.get("next")

        for result in ip_results:
            interface = result["interface"]["name"]
            if interface not in interface_list:
                interface_list.append(interface)
            interface_data = (
                result["address"],
                result["family"]["label"],
                interface,
            )
            result_list.append(interface_data)

        for intf in interface_list:
            interfaces[intf] = {
                "IPv4": [],
                "IPv6": [],
            }
            for element in result_list:
                if intf in element:
                    if "IPv4" in element:
                        interfaces[intf]["IPv4"].append(element[0])
                    else:
                        interfaces[intf]["IPv6"].append(element[0])
        return interfaces
