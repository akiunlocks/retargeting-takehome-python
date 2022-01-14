import json
import os
import itertools as itools
import sys
import uuid
from collections import defaultdict, OrderedDict, Counter
import requests
from starlette.templating import Jinja2Templates
import logging
from csv import DictReader

from aki.retarget.model import Cache, Config, Product

logging.basicConfig(stream=sys.stdout, level=logging.DEBUG)
logger = logging.getLogger()


class Services:
    CACHE = Cache
    Templates: Jinja2Templates


def generate_uuid():
    return uuid.uuid4()


def load_catalog():
    catalog_file_path = os.path.join(Config.ASSETS_DIR, 'store-catalog.json')
    with open(catalog_file_path) as catalog_file:
        catalog_data = json.load(catalog_file)
        assert 'products' in catalog_data, 'products section not found in catalog'
        products = [Product(**entry) for entry in catalog_data['products']]
        products_by_category = itools.groupby(products, lambda x: x.category)
        products_by_id = itools.groupby(products, lambda x: x.id)
        Services.CACHE.products_by_category = OrderedDict([(cat, list(prod_group)) for cat, prod_group in products_by_category])
        Services.CACHE.products_by_id = dict([(prod_id, next(iter(prod_group))) for prod_id, prod_group in products_by_id])
        logger.info('loaded catalog ' + catalog_file_path)


def load_promotions(url):
    resp = requests.get(url)
    if not resp.ok:
        return False

    rows = [line.decode('utf-8') for line in resp.iter_lines()]
    row_iter = DictReader(rows)

    for row in row_iter:
        row['src'] = row['url']
        del row['url']
        Services.CACHE.promotions_by_category[row['category']].append(Product(**row))
        Services.CACHE.promotions_by_product_id[row['id']] = Product(**row)

    logger.info('processed ' + str(len(rows)) + ' rows from promotions feed')
