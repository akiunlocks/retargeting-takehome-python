import json
import os
import itertools as itools
import sys
import uuid
from collections import defaultdict, OrderedDict, Counter
from dataclasses import dataclass
from typing import List, Iterable

import requests
from sqlitedict import SqliteDict
from starlette.templating import Jinja2Templates
import logging
from csv import DictReader
logging.basicConfig(stream=sys.stdout, level=logging.DEBUG)

logger = logging.getLogger()

class Config:
    FREQ_CAP_LIMIT = 1
    PROJECT_HOME_DIR = None
    ASSETS_DIR = None
    SUPPOTED_CATEGORIES = ['sports','grilling']
    PROMOTIONS_FEED_URL = 'https://aki-public.s3-us-west-2.amazonaws.com/take-home/promotions/promoted_products.csv'

@dataclass
class Product:
    id: str
    name: str
    src: str
    category: str

    promotion_to_product = {
        'product_id' : 'id',
        'product_name' : 'name',
        'product_category' : 'category',
        'product_url' : 'src'
    }

    @property
    def has_local_asset(self):
        return not self.src.startswith('http')

    @classmethod
    def from_promotion(cls, prom_data: dict):
        traslated_data = {}
        for prom_name, prod_name in cls.promotion_to_product.items():
            traslated_data[prod_name] = prom_data[prom_name].strip()

        return cls(**traslated_data)

class User:
    def __init__(self):
        self.categories = set()
        self.products_clicked = set()
        self.products_advertised = defaultdict(int)

    def get_non_freq_capped_products(self, products: Iterable[Product]):
        return list(filter(lambda x: self.products_advertised[x.id] <= Config.FREQ_CAP_LIMIT, products))


class Cache:
    users = defaultdict(User)
    products_by_category: OrderedDict = OrderedDict()
    products_by_id: dict = {}
    promotions_by_category: dict = defaultdict(list)
    promotions_by_product_id: OrderedDict = OrderedDict()


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
        Services.CACHE.promotions_by_category[row['product_category']].append(Product.from_promotion(row))
        Services.CACHE.promotions_by_product_id[row['product_id']] = Product.from_promotion(row)

    logger.info('processed ' + str(len(rows)) + ' rows from promotions feed')
