import logging as log
import random
from typing import Optional, List

from fastapi.responses import HTMLResponse
from fastapi import APIRouter, Request, Response, Cookie
from starlette.templating import Jinja2Templates

from aki.retarget import core
from aki.retarget.core import Services, Config

templates = Jinja2Templates(directory='/Users/alexbelyansky/eyeview/akiworkspace/retargeting-takehome-python/html')

def init_routes():
    router = APIRouter()

    @router.get("/errorpage", response_class=HTMLResponse)
    def show_error_page(request: Request):
        return templates.TemplateResponse('error.html', {'request': request})

    @router.get('/productclicked/{product_id}')
    def product_clicked(product_id: str):

        return {}

    @router.get("/storecatalog", response_class=HTMLResponse)
    def show_store_catalog(request: Request):
        return templates.TemplateResponse(
            'store-catalog.html',
            {
                'request': request,
                'grillpath': 'weber-grill.jpeg',
                'sportspath': 'bike.jpeg'
            })

    def show_error_page(request: Request, errormsg: str):
        return templates.TemplateResponse(
            'error.html',
            {
                'request': request,
                'errormsg': errormsg
            }
        )

    def show_product_ad_page(request: Request, product: dict):
        return templates.TemplateResponse(
            'adpage.html',
            {
                'request': request,
                'product': product
            }
        )

    def show_product_catalog_page(request, products: List):
        return templates.TemplateResponse(
            'catalog.html',
            {
                'request': request,
                'products': products
            })

    @router.get("/storecatalog/{category}", response_class=HTMLResponse)
    def show_store_catalog_category(request: Request, response: Response, category: str, akiuser: Optional[str] = Cookie(None)):
        if category not in Config.SUPPOTED_CATEGORIES:
            return show_error_page()

        if not akiuser:
            akiuser = core.generate_uuid()
            response.set_cookie(key='akiuser', value=akiuser, expires=300)
            Services.DB['users_by_id'][akiuser] = akiuser

        user_info = Services.DB['users_by_id'][akiuser]
        user_info.categories.add(category)
        Services.DB['users_by_id'][akiuser] = user_info

        return show_product_catalog_page(request, Services.Cache['products_by_category'][category])


    @router.get("/fetchad", response_class=HTMLResponse)
    def fetch_ad(request: Request, akiuserid: Optional[str] = Cookie(None)):
        log.info('fetching ad for user ' + str(akiuserid))
        product = Services.Cache['products_by_category']['default'][0]


        if akiuserid:
            akiuser = Services.DB['users_by_id'][akiuserid]
            if akiuser.products_clicked:
                db_products_clicked = Services.Cache['products_by_id'].keys() & akiuser.roducts_clicked
                if db_products_clicked:
                    # we have a specific product in our catalog that was clicked
                    product = Services.Cache['products_by_id'][db_products_clicked[0]]

                    return show_product_ad_page(request, product)

            if akiuser.categories:
                db_categories_visited = Services.Cache['products_by_category'].keys() & akiuser.categories
                if db_categories_visited:
                    # we have a product category that user visited
                    product = Services.Cache['products_by_category'][db_categories_visited[0]]

                    return show_product_ad_page(request, product)

        return show_product_ad_page(request, product)

    return router
