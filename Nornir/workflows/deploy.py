#!/home/gns3/workspace/Nornir/.venv/bin/python

from nornir import InitNornir
from pprint import pprint
from nornir.plugins.tasks import networking, text
from nornir.plugins.functions.text import print_result
from nornir.core.filter import F
from nornir.plugins.tasks.version_control import gitlab
import logging





def main():
        # template = "ntp.j2"
        nr = InitNornir(config_file="../config.yaml")
        # pprint(nr.inventory.get_inventory_dict()["hosts"])
        juniper = nr.filter(platform="junos")
        pprint(juniper.inventory.get_hosts_dict())
        # rgit = juniper.run(task=get_template, template=template)
        # print_result(rgit)
        # rconfig = juniper.run(task=push_config, template=template)
        # print_result(rconfig)
        

def get_template(task, template):
    print("Getting template from gitlab")
    r = task.run(
        task=gitlab, 
        action="get", 
        url="http://gitlab.mss.com", 
        token="yfP7ecnFpzRXDUsxzyg4", 
        repository="Nornir_Templates", 
        ref="master", 
        filename=template,
        # filename=f"{task.host.platform}/{template}", 
        destination="/tmp/hosts", 
        severity_level=logging.DEBUG
        )
    print_result(r)
    


def push_config(task, template):
    print("Render and Push config")
    result = task.run(
        task=text.template_file,
        name="Generate config from template",
        template="hosts",
        path="/tmp",
        severity_level=logging.DEBUG
    )
    task.host["config"] = result.result


    # Deploy that configuration to the device using NAPALM
    task.run(task=networking.napalm_configure,
             name="Loading Configuration on the device",
             replace=False,
             dry_run=True,
             configuration=task.host["config"],
             severity_level=logging.DEBUG
             )

main()