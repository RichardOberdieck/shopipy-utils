from time import sleep
import requests
import click

from shopipy_utils.constants import BASE_URL
from shopipy_utils.products import get_products_from_shopify
from shopipy_utils.utils import get_header_for_shopify


@click.command()
def update_skus():
    products = get_products_from_shopify()
    failed_counter = 0
    for product in products:
        for variant in product["variants"]:
            id = variant["id"]
            response = requests.put(
                f"{BASE_URL}/variants/{id}.json",
                json={"variant": {"id": id, "sku": id}},
                headers=get_header_for_shopify(),
            )
            sleep(1)
            if response.status_code != 200:
                failed_counter += 1
                print(f'Problem with {product['id']}')

    if failed_counter > 0:
        raise ValueError(f"There were {failed_counter} issues")


if __name__ == "__main__":
    update_skus()
