# Steps
# Check that the username is not already configured on the device.
# Push the config with username and
# Check that the username is now configured


from nornir import InitNornir
from nornir.plugins.tasks import networking, text
from nornir.plugins.functions.text import print_result
from nornir.core.filter import F


def add_new_user(task):
    r = task.run(
        task=text.template_file,
        name="Update local Users",
        template="system.j2",
        path=f"templates/{task.host.platform}",
    )

    task.host["config"] = r.result

    task.run(
        task=networking.napalm_configure,
        name="Loading config to the device",
        dry_run=True,
        configuration=task.host["config"],
    )


def check_users_not_configured(task,):
    task.run(task=networking.napalm_validate, src="../validators/validate_users.yaml")


def main():
    nr = InitNornir(config_file="config.yaml")
    srx_devices = nr.filter(F(platform="junos"))

    result = srx_devices.run(task=add_new_user)
