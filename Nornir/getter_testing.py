#!/home/gns3/workspace/Nornir/.venv/bin/python

from nornir import InitNornir
from nornir.plugins.tasks import networking, text
from nornir.plugins.functions.text import print_result
from nornir.core.filter import F


def main():
    nr = InitNornir(config_file="config.yaml")
    devices = nr.filter(F(platform="junos"))

    result = devices.run(task=networking.napalm_get, getters=["config"])
    # result = devices.run(task=networking.napalm_cli, commands=["show version"])
    print_result(result)


if __name__ == "__main__":
    main()
