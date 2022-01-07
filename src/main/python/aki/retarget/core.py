import json
import os
import itertools as itools
import sys
import uuid
from collections import defaultdict, OrderedDict, Counter
from dataclasses import dataclass

import requests
from sqlitedict import SqliteDict
from starlette.templating import Jinja2Templates
import logging
from csv import DictReader
logging.basicConfig(stream=sys.stdout, level=logging.DEBUG)

logger = logging.getLogger()

class Config:
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

    @property
    def has_local_asset(self):
        return not self.src.startswith('http')

class User:
    def __init__(self):
        self.categories = set()
        self.products_clicked = set()
        self.product_advertised = defaultdict(int)

class Cache:
    user = defaultdict(User)
    products_by_category: OrderedDict = OrderedDict()
    products_by_id: dict = {}
    promotions_by_category: dict = defaultdict(list)
    promotions_by_product_id: OrderedDict = OrderedDict()


class Services:
    CACHE = Cache
    DB: dict = {} # assuming in memory storage for this exercise
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
        Services.CACHE.promotions_by_category[row['product_category']].append(row)
        Services.CACHE.promotions_by_product_id[row['product_id']] = row

    logger.info('processed ' + str(len(rows)) + ' rows from promotions feed')
