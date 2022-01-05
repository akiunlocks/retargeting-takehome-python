import json
import os
import itertools as itools
import uuid
from sqlitedict import SqliteDict
class Config:
    PROJECT_HOME_DIR = None
    ASSETS_DIR = None
    SUPPOTED_CATEGORIES = ['sports','grilling']

class Services:
    Cache: dict
    DB: SqliteDict

class User:
    def __init__(self):
        self.categories = set()
        self.products_clicked = set()

def generate_uuid():
    return uuid.uuid4()

def load_catalog():
    catalog_file_path = os.path.join(Config.ASSETS_DIR, 'store-catalog.json')
    with open(catalog_file_path) as catalog_file:
        catalog_data = json.load(catalog_file)
        products_by_category = itools.groupby(catalog_data['products'], lambda x: x['category'])
        products_by_id = itools.groupby(catalog_data['products'], lambda x: x['id'])
        Services.CACHE['products_by_category'] = dict([(cat, list(prod_group)) for cat, prod_group in products_by_category])
        Services.CACHE['products_by_id'] = dict([(prod_id, list(prod_group)) for prod_id, prod_group in products_by_id])