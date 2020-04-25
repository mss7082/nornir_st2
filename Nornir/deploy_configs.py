from nornir import InitNornir
from nornir.plugins.tasks import networking, text
from nornir.plugins.functions.text import print_result


def basic_configuration(task, template_name=None):
    r = task.run(
        task=text.template_file,
        name="Base Configuration",
        template=template_name,
        path=f"templates/{task.host.platform}",
    )

    task.host["config"] = r.result

    task.run(
        task=networking.napalm_configure,
        name="Loading Configuration on the device",
        replace=False,
        configuration=task.host["config"],
    )


def main():
    templ_name = input("Enter the template name:")
    platform = input("What's the target platform? :")
    nr = InitNornir(config_file="config.yaml", dry_run=True)
    matched_devices = nr.filter(platform=platform)
    result = matched_devices.run(task=basic_configuration, template_name=templ_name)
    print_result(result)


if __name__ == "__main__":
    main()
