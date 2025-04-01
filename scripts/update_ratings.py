from time import sleep
import click
import requests
from bs4 import BeautifulSoup

from shopipy_utils.constants import BASE_URL
from shopipy_utils.products import Rating, get_products_from_shopify
from shopipy_utils.utils import send_post_request, send_put_request


@click.command()
def update_ratings():
    products = get_products_from_shopify()

    for product in products:
        if "untappd_" not in product["tags"]:
            continue
        rating = get_untappd_rating(product["tags"])
        update_rating_in_shopify(product["id"], rating)

        sleep(1)  # For rate-limit purposes
        update_tags_in_shopify(product["id"], product["tags"], rating.rating)


def get_untappd_rating(tags: str) -> Rating:
    url = get_untappd_url_from_tag(tags)
    beer_tag = get_beer_specific_tag(url)
    return get_rating_info_from_tag(beer_tag)


def get_untappd_url_from_tag(tags: str) -> str:
    list_of_tags = tags.split(", ")
    component = [tag for tag in list_of_tags if "untappd_" in tag][0].strip("untappd_")
    return f"https://untappd.com/b/{component}"


def get_beer_specific_tag(url):
    headers = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.95 Safari/537.36"
    }
    response = requests.get(url, headers=headers)
    soup = BeautifulSoup(response.content, "html.parser")
    return soup.find("div", class_="details")


def get_rating_info_from_tag(beer_tag) -> Rating:
    rating = float(beer_tag.find("div", class_="caps").get("data-rating"))
    rating_text = beer_tag.find("p", class_="raters").text
    rating_text_list = rating_text.split()
    rating_count = int(rating_text_list[0].replace(",", ""))
    return Rating(rating=rating, rating_count=rating_count)


def update_rating_in_shopify(id: str, rating: Rating) -> None:
    url = f"{BASE_URL}/products/{id}/metafields.json"
    send_post_request(url, rating.get_rating_dict())
    send_post_request(url, rating.get_rating_count_dict())
    sleep(1)  # To respect rate limit


def update_tags_in_shopify(id: str, tags: str, rating: float) -> None:
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
