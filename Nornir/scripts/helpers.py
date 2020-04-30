#!/home/gns3/workspace/Nornir/.venv/bin/python

from secrets import creds
from nornir import InitNornir
from pprint import pprint

# Tranform Functions


def adapt_user_password(host):
    host.username = creds[f"{host}"]["username"]
    host.password = creds[f"{host}"]["password"]


# Netbox


# CLI

if __name__ == "__main__":
        nr = InitNornir(config_file="../config.yaml")
        pprint(nr.inventory.get_inventory_dict())
