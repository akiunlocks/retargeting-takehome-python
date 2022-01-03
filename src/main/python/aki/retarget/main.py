import json
import logging as log
import os

from starlette.staticfiles import StaticFiles
log.basicConfig(level=log.INFO)
import uvicorn
from fastapi import FastAPI
from starlette.middleware.cors import CORSMiddleware

from aki.retarget.web import init_routes as init_web_routes
from aki.retarget.core import Config, load_catalog

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



log.info('initialized web endpoints')

if __name__ == '__main__':

    uvicorn.run("main:app", host='0.0.0.0', access_log=False)