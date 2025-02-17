import requests
from shopipy_utils.utils import get_header_for_shopify
from shopipy_utils.constants import BASE_URL


def get_all_products_url(id: int) -> str:
    return f"{BASE_URL}/products.json?since_id={id}"


def get_products_from_shopify() -> dict:
    products = []
    products_remaining = True
    last_id = 0
    while products_remaining:
        response = requests.get(get_all_products_url(last_id), headers=get_header_for_shopify())
        current_products = response.json()["products"]
        if len(current_products) == 0:
            products_remaining = False
        else:
            products += current_products
            last_id = current_products[-1]["id"]
    return products
