import sys
from typing import Optional, List
import logging
logging.basicConfig(stream=sys.stdout, level=logging.DEBUG)
logger = logging.getLogger()

from fastapi.responses import HTMLResponse
from fastapi import APIRouter, Request, Response, Cookie

from aki.retarget import core
from aki.retarget.core import Services, Config, User, Product


def init_routes():
    router = APIRouter()

    @router.get("/errorpage", response_class=HTMLResponse)
    def show_error_page(request: Request):
        return Services.Templates.TemplateResponse('error.html', {'request': request})

    @router.get('/productclicked/{product_id}')
    def product_clicked(product_id: str,  akiuserid: Optional[str] = Cookie(None)):
        Services.DB['users_by_id'][akiuserid].products_clicked.add(product_id)
        logger.info('product ' + product_id + ' added for user ' + akiuserid)
        return {}

    @router.get("/storecatalog", response_class=HTMLResponse)
    def show_store_catalog(request: Request):
        return Services.Templates.TemplateResponse(
            'store-catalog.html',
            {
                'request': request,
                'grillpath': 'weber-grill.jpeg',
                'sportspath': 'bike.jpeg'
            })

    def show_error_page(request: Request, errormsg: str):
        return Services.Templates.TemplateResponse(
            'error.html',
            {
                'request': request,
                'errormsg': errormsg
            }
        )

    def show_product_ad_page(request: Request, product: Product, userid: str = "default"):
        Services.CACHE.user[str].product_advertised[product.id] += 1
        return Services.Templates.TemplateResponse(
            'adpage.html',
            {
                'request': request,
                'product': product
            }
        )

    def show_product_catalog_page(request: Request, products: List):
        return Services.Templates.TemplateResponse(
            'catalog.html',
            {
                'request': request,
                'products': products
            })

    @router.get("/storecatalog/{category}", response_class=HTMLResponse)
    def show_store_catalog_category(request: Request, category: str, akiuserid: Optional[str] = Cookie(None)):
        if category not in Config.SUPPOTED_CATEGORIES:
            return show_error_page()

        response = show_product_catalog_page(request, Services.CACHE.products_by_category[category])
        if not akiuserid:
            akiuserid = core.generate_uuid()
            response.set_cookie(key='akiuserid', value=akiuserid)

        user_info = Services.DB['users_by_id'][akiuserid]
        user_info.categories.add(category)
        logger.info(f'category {category} added for user {akiuserid}')

        return response


    @router.get("/quoteoftheday", response_class=HTMLResponse)
    def fetch_ad(request: Request, akiuserid: Optional[str] = Cookie(None)):
        logger.info('fetching ad for user ' + str(akiuserid))
        product = Services.CACHE.products_by_category['default'][0]
        product['product_url'] = '/assets/' + product['filename']

        if akiuserid:
            akiuser = Services.DB['users_by_id'][akiuserid]
            if akiuser.products_clicked:
                db_products_clicked = Services.CACHE.promotions_by_product_id.keys() & akiuser.products_clicked

                if db_products_clicked:
                    # we have a specific product in our catalog that was clicked
                    chosen_product_id = next(iter(db_products_clicked))
                    product = Services.CACHE.promotions_by_product_id[chosen_product_id]

                    return show_product_ad_page(request, product)

            if akiuser.categories:
                catalog_categories = set(Services.CACHE.promotions_by_category.keys())
                db_categories_visited = catalog_categories & akiuser.categories
                if db_categories_visited:
                    # we have a product category that user visited
                    chosen_category = next(iter(db_categories_visited))
                    product = next(iter(Services.CACHE.promotions_by_category[chosen_category]))

                    return show_product_ad_page(request, product)

        return show_product_ad_page(request, product)

    return router
