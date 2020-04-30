#!/home/gns3/workspace/Nornir/.venv/bin/python

from secrets import creds
from nornir import InitNornir
from pprint import pprint
from nornir.plugins.tasks import networking, text
from nornir.plugins.functions.text import print_result
from nornir.core.filter import F

def adapt_user_password(host):
    host.username = creds[f"{host}"]["username"]
    host.password = creds[f"{host}"]["password"]


# Netbox


# CLI

if __name__ == "__main__":
        nr = InitNornir(config_file="../config.yaml")
        # pprint(nr.inventory.get_inventory_dict()["hosts"])
        juniper = nr.filter(platform="junos")
        result = juniper.run(task=networking.napalm_cli, commands=["show interface terse"])
        print_result(result)

