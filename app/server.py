from starlette.applications import Starlette
from starlette.responses import HTMLResponse, JSONResponse, FileResponse
from starlette.staticfiles import StaticFiles
from starlette.middleware.cors import CORSMiddleware
import uvicorn, aiohttp, asyncio
from io import BytesIO

import os
import sys
from os.path import join
from pathlib import Path

from fastai import *
from fastai.text import *
import torch
import numpy as np
import pickle
# from fastai.vision import *

# Starter model
# model_file_url = 'https://www.dropbox.com/s/y4kl2gv1akv7y4i/stage-2.pth?raw=1'
# model_file_name = 'model'
# classes = ['black', 'grizzly', 'teddys']

# ULMFiT
model_file_url = 'https://drive.google.com/uc?export=download&id=14rPSDte6ODkBivm_lN2gmqXd9zM9atNs'
model_file_name = 'ULMFiT_classifier_model_cpu'
classes = ['account_blocked','application_status','apr','balance','bill_balance','bill_due']

path = Path(__file__).parent

app = Starlette()
app.add_middleware(CORSMiddleware, allow_origins=['*'], allow_headers=['X-Requested-With', 'Content-Type'])
app.mount('/static', StaticFiles(directory='app/static'))


async def download_file(url, dest):
    if dest.exists(): return
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            data = await response.read()
            with open(dest, 'wb') as f: f.write(data)

async def setup_learner():

    learn = load_learner(path, 'models/ULMFiT_classifier_model_cpu.pkl')

    return learn

loop = asyncio.get_event_loop()
tasks = [asyncio.ensure_future(setup_learner())]
learn = loop.run_until_complete(asyncio.gather(*tasks))[0]
loop.close()

@app.route('/')
def index(request):
    html = path/'view'/'index.html'
    return HTMLResponse(html.open().read())

@app.route('/analyze', methods=['POST'])
async def analyze(request):
    data = await request.form()
    img_bytes = await (data['file'].read())
    img = open_image(BytesIO(img_bytes))
    return JSONResponse({'result': str(learn.predict(img)[0])})

@app.route("/create-entry", methods=["POST"])
async def create_entry(request):
    ''' Process and analyze new entry '''
    print("Send button clicked!")
    data = await request.form()
    print(data)

    print(learn.predict("what's the apr on my capital one venture card"))
    print(learn.predict("has my mastercard application gone through the process"))

    return JSONResponse({'result': 'OK OK'})

    # html = path/'view'/'index.html'
    # return HTMLResponse(html.open().read())

if __name__ == '__main__':
    if 'serve' in sys.argv: uvicorn.run(app, host='0.0.0.0', port=8080)
