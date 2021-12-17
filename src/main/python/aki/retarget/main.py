import logging as log
log.basicConfig(level=log.INFO)

import uvicorn
from fastapi import FastAPI
from starlette.middleware.cors import CORSMiddleware

from aki.retarget.web import init_routes as init_web_routes

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get('/_status')
def health_check():
    return {'app': 'retarget-takehome', 'status': 'healthy'}

@app.get('/_ready')
def ready_check():
    return health_check()

@app.get('/')
def home():
    return health_check()

app.include_router(init_web_routes(), prefix='/web')
log.info('initialized web endpoints')

if __name__ == '__main__':
    uvicorn.run("main:app", host='0.0.0.0', access_log=False)