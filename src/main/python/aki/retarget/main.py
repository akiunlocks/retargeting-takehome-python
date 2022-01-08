import json
import logging as log
import os
import threading
import time
from collections import defaultdict
import schedule
import functools
from starlette.staticfiles import StaticFiles
from starlette.templating import Jinja2Templates

from aki.retarget import core

log.basicConfig(level=log.INFO)
import uvicorn
from fastapi import FastAPI
from starlette.middleware.cors import CORSMiddleware

from aki.retarget.web import init_routes as init_web_routes
from aki.retarget.core import Config, load_catalog, Services, User

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

Config.PROJECT_HOME_DIR = os.environ.get('AKI_PROJECT_DIR', os.getcwd())
Config.ASSETS_DIR = os.path.join(Config.PROJECT_HOME_DIR, 'assets')

assert os.path.exists(Config.ASSETS_DIR), f'project home not set - assets path {Config.ASSETS_DIR} not found'

Services.Templates = Jinja2Templates(directory='%s/html' % Config.PROJECT_HOME_DIR)
app.mount('/assets', StaticFiles(directory=('%s/assets' % Config.PROJECT_HOME_DIR)), name='assets')
app.include_router(init_web_routes(), prefix='/web')

@app.get('/_status')
def health_check():
    return {'app': 'retarget-takehome', 'status': 'healthy'}

@app.get('/_ready')
def ready_check():
    return health_check()

@app.get('/')
def home():
    return health_check()

@app.on_event("startup")
async def startup_event():
    load_catalog()

def run_scheduler():
    while True:
        schedule.run_pending()
        time.sleep(1)

log.info('initialized web endpoints')

if __name__ == '__main__':
    prom_load_fn = functools.partial(core.load_promotions, Config.PROMOTIONS_FEED_URL)
    prom_load_fn()
    # schedule promotions feed download
    # schedule.every(1).minutes.do(prom_load_fn)
    # threading.Thread(target=run_scheduler, name="scheduler", daemon=True).start()

    uvicorn.run("main:app", host='0.0.0.0', access_log=False)