import logging as log
from typing import Optional

from fastapi.responses import HTMLResponse
from fastapi import APIRouter, Request, Response, Cookie
from starlette.templating import Jinja2Templates

templates = Jinja2Templates(directory='/Users/alexbelyansky/eyeview/akiworkspace/retargeting-takehome-python/html')

cache = {}

def init_routes():
    router = APIRouter()

    @router.get("/errorpage", response_class=HTMLResponse)
    def show_error_page(request: Request):
        return templates.TemplateResponse('error.html', {'request': request})

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
    def show_store_catalog_category(category:str, request: Request, response: Response, akiutype: Optional[str] = Cookie(None)):
        if (category == 'sports'):
            if not akiutype:
                response.set_cookie(key='akiutype', value='sportsfan', expires=60)
            return templates.TemplateResponse(
                'sports.html',
                {
                    'request': Request,

                }
            )
        elif (category == 'grilling'):
            if not akiutype:
                response.set_cookie(key='akiutype', value='grillmaster', expires=60)
            return show_store_catalog(request)
        else:
            return show_error_page(request)


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
