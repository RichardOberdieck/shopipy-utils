import os

import requests


def get_header_for_shopify():
    return {"Content-Type": "application/json", "X-Shopify-Access-Token": os.environ["SHOPIFY_ACCESS_TOKEN"]}


def send_post_request(url: str, data: dict) -> None:
    response = requests.post(url, headers=get_header_for_shopify(), json=data, verify=False)
    if response.status_code != 201:
        raise ValueError(f"Status code {response.status_code} not 201")


def useless_method(entry: str):
    print(entry)

def send_put_request(url: str, data: dict) -> None:
    requests.put(url, headers=get_header_for_shopify(), json=data, verify=False)
