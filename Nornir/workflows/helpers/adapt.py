from helpers.secrets import creds
import requests
import json
from pprint import pprint


def more_data(host):
    host.username = creds[f"{host}"]["username"]
    host.password = creds[f"{host}"]["password"]
