import json
import os
import itertools as itools
class Config:
    PROJECT_HOME_DIR = None
    ASSETS_DIR = None

CACHE = {}

def load_catalog():
    catalog_file_path = os.path.join(Config.ASSETS_DIR, 'store-catalog.json')
    with open(catalog_file_path) as catalog_file:
        catalog_data = json.load(catalog_file)
        products_by_category = itools.groupby(catalog_data['products'], lambda x: x['category'])
        CACHE['catalog'] = dict([(cat, list(prod_group)) for cat, prod_group in products_by_category])
