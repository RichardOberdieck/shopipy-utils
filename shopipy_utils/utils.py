import os


def get_header_for_shopify():
    return {"Content-Type": "application/json", "X-Shopify-Access-Token": os.environ["SHOPIFY_ACCESS_TOKEN"]}
