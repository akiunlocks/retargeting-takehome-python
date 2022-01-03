import logging as log
from typing import Optional

from fastapi.responses import HTMLResponse
from fastapi import APIRouter, Request, Response, Cookie
from starlette.templating import Jinja2Templates

from aki.retarget.core import CACHE

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


    @router.get("/storecatalog/{category}", response_class=HTMLResponse)
    def show_store_catalog_category(request: Request, response: Response, category: str, akiutype: Optional[str] = Cookie(None)):
        if (category == 'sports'):
            if not akiutype:
                response.set_cookie(key='akiutype', value='sportsfan', expires=60)

        elif (category == 'grilling'):
            if not akiutype:
                response.set_cookie(key='akiutype', value='grillmaster', expires=60)

        else:
            return show_error_page(request)

        return templates.TemplateResponse(
            'catalog.html',
            {
                'request': request,
                'products': CACHE['catalog'][category]
            })


    @router.get("/fetchad")
    def fetch_ad(akiutype: Optional[str] = Cookie(None)):
        log.info('fetching ad for user ' + str(akiutype))
        if not akiutype:
            return {'ad': 'default ad'}

        if akiutype == 'sportsfan':
            return {'ad': 'sports ad'}
        if akiutype == 'grillmaster':
            return {'ad': 'grilling ad'}

        return {'ad': 'default ad'}

    return router
