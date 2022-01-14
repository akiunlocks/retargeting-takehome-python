from collections import defaultdict, OrderedDict
from dataclasses import dataclass
from typing import Iterable


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
        return list(filter(lambda x: self.products_advertised[x.id] < Config.FREQ_CAP_LIMIT, products))


class Cache:
    users = defaultdict(User)
    products_by_category: OrderedDict = OrderedDict()
    products_by_id: dict = {}
    promotions_by_category: dict = defaultdict(list)
    promotions_by_product_id: OrderedDict = OrderedDict()
