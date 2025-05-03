import requests
from shopipy_utils.utils import get_header_for_shopify
from shopipy_utils.constants import BASE_URL
from pydantic import BaseModel
from time import sleep
from json import dumps


def get_all_products_url(id: int) -> str:
    return f"{BASE_URL}/products.json?since_id={id}"


def get_products_from_shopify() -> dict:
    products = []
    products_remaining = True
    last_id = 0
    while products_remaining:
        response = requests.get(get_all_products_url(last_id), headers=get_header_for_shopify(), verify=False)
        sleep(1)
        current_products = response.json()["products"]
        if len(current_products) == 0:
            products_remaining = False
        else:
            products += current_products
            last_id = current_products[-1]["id"]
    return products


class Rating(BaseModel):
    rating: float
    rating_count: int

    def get_rating_dict(self):
        return {
            "metafield": {
                "namespace": "reviews",
                "key": "rating",
                "value": dumps({"value": self.rating, "scale_min": 1.0, "scale_max": 5.0}),
                "type": "rating",
            }
        }

    def get_rating_count_dict(self):
        return {
            "metafield": {
                "namespace": "reviews",
                "key": "rating_count",
                "value": f"{self.rating_count}",
                "type": "number_integer",
            }
        }


class Product(BaseModel):
    id: str
    title: str
    tags: str
    untappd_link: str = ""
    rating: Rating | None = None

    def update_raupdate_rating_in_shopifyting(self) -> None:
        rating_dict = self.define_rating_dict()
        self.send_post_request(rating_dict)

        rating_count_dict = self.define_rating_count_dict()
        self.send_post_request(rating_count_dict)
        sleep(1)  # To respect rate limit

    def update_tags_in_shopify(self) -> None:
        list_of_tags = self.tags.split(", ")
        tags_without_rating_classification = ", ".join([t for t in list_of_tags if t != "4+"])

        if self.rating.rating >= 4:
            updated_tags = tags_without_rating_classification + ", 4+"
        else:
            updated_tags = tags_without_rating_classification

        data = {"product": {"id": self.id, "tags": updated_tags}}

        sleep(1)  # To respect rate limit

        requests.put(self.get_product_url(), headers=get_header_for_shopify(), json=data)

    def get_metafields_url(self):
        return f"{BASE_URL}/products/{self.id}/metafields.json"

    def get_product_url(self):
        return f"{BASE_URL}/products/{self.id}.json"

    def send_post_request(self, data: dict[str, dict]) -> None:
        response = requests.post(self.get_metafields_url(), headers=get_header_for_shopify(), json=data)
        if response.status_code != 201:
            raise ValueError(f"Status code {response.status_code} not 201")
