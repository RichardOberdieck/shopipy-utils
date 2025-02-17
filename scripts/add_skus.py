import requests

from shopipy_utils.constants import BASE_URL
from shopipy_utils.products import get_products_from_shopify
from shopipy_utils.utils import get_header_for_shopify


products = get_products_from_shopify()
for product in products:
    for variant in product["variants"]:
        id = variant["id"]
        response = requests.put(
            f"{BASE_URL}/variants/{id}.json", json={"variant": {"id": id, "sku": id}}, headers=get_header_for_shopify()
        )
