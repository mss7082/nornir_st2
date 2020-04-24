from nornir import InitNornir
from nornir.plugins.tasks import networking, text
from nornir.plugins.functions.text import print_result, print_title


nr = InitNornir(config_file="config.yaml", dry_run=True)

srx_devices = nr.filter(platform="junos")
ios_devices = nr.filter(platform="ios")


def basic_configuration(task):
    r = task.run(task=text.template_file,
                 name="Base Configuration",
                 template="base.j2", path=f"templates/{task.host.platform}")

    task.host["config"] = r.result

    task.run(task=networking.napalm_configure, name="Loading Configuration on the device",
             replace=False, configuration=task.host["config"])


print_title("Playbook to configuration the network")
result = ios_devices.run(task=basic_configuration)
print(result.failed)
print(result.failed_hosts)
