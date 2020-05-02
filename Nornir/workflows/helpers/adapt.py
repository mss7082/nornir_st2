from helpers.secrets import creds
import requests
import json
from pprint import pprint


def more_data(host):
    host.username = creds[f"{host}"]["username"]
    host.password = creds[f"{host}"]["password"]
    host["interfaces"] = _get_interfaces_IP()




def _get_interfaces_IP():
  interfaces = {}
  interface_list = []
  result_list = []
  url = "https://192.168.122.151/api/ipam/ip-addresses?device=r1"

  payload = {}
  headers = {
    'Authorization': 'Token 144de785b9a868ae7cc2d62a55841273cd28182e'
  }

  response = requests.request("GET", url, headers=headers, data = payload, verify=False)

  decoded_response = json.loads(response.text.encode("utf8"))
  for result in decoded_response["results"]:
    interface = result["interface"]["name"]
    if interface not in interface_list:
      interface_list.append(result["interface"]["name"])
    interface_data = result["address"], result["interface"]["name"], result["family"]["label"]
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

