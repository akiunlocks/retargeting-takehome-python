import logging as log
from typing import Optional

from fastapi import Header, APIRouter, Response, Cookie
from pydantic import BaseModel

def init_routes():
    router = APIRouter()

    @router.get("/visitstore/{category}")
    def visitstore(category:str, response: Response, akiutype: Optional[str] = Cookie(None)):
        if (category == 'sports'):
            response.set_cookie(key='akiutype', value='sportsfan', expires=60)
            resp_data = {'usertype':'sports fan'}
        elif (category == 'grilling'):
            response.set_cookie(key='akiutype', value='grillmaster', expires=60)
            resp_data = {'usertype': 'grill master'}
        else:
            resp_data = {'usertype': 'unknown'}

        return resp_data

    @router.get("/fetchad")
    def fetchad(akiutype: Optional[str] = Cookie(None)):
        log.info('fetching ad for user ' + str(akiutype))
        if not akiutype:
            return {'ad': 'default ad'}

        if akiutype == 'sportsfan':
            return {'ad': 'sports ad'}
        if akiutype == 'grillmaster':
            return {'ad': 'grilling ad'}

        return {'ad': 'default ad'}

    return router
