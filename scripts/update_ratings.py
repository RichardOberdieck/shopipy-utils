from time import sleep
import click

from shopipy_utils.constants import BASE_URL
from shopipy_utils.products import Rating, get_products_from_shopify
from shopipy_utils.utils import send_post_request, send_put_request


@click.command()
def update_ratings():
    products = get_products_from_shopify()

    for product in products:
        if "untappd_link" not in product["tags"]:
            continue
        rating = get_rating_from_untappd(product["untappd_link"])
        update_rating_in_shopify(product["id"], rating)

        sleep(1)  # For rate-limit purposes
        update_tags_in_shopify(product["id"], product["tags"], rating)


def get_rating_from_untappd() -> Rating:
    pass


def update_rating_in_shopify(id: str, rating: Rating) -> None:
    url = f"{BASE_URL}/products/{id}/metafields.json"
    send_post_request(url, rating.get_rating_dict())
    send_post_request(url, rating.get_rating_count_dict())
    sleep(1)  # To respect rate limit


def update_tags_in_shopify(id: str, tags: str, rating: Rating) -> None:
    list_of_tags = tags.split(", ")
    tags_without_rating_classification = ", ".join([t for t in list_of_tags if t != "4+"])

    if rating >= 4:
        updated_tags = tags_without_rating_classification + ", 4+"
    else:
        updated_tags = tags_without_rating_classification

    data = {"product": {"id": id, "tags": updated_tags}}

    sleep(1)  # To respect rate limit

    send_put_request(f"{BASE_URL}/products/{id}.json", data)


if __name__ == "__main__":
    update_ratings()
