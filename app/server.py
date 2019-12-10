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
    # await download_file(model_file_url, path/'models'/f'{model_file_name}.pkl')

    loaded_model = load_learner(path, '/notebooks/storage/ULMFiT_classifier_model_cpu.pkl')
    loaded_model.predict("tell me my hsbc card credit limit")

    # Data setup (not needed)
    # data_lm = TextDataBunch.from_csv(path, 'notebooks/storage/Final_Intent_Dataset.csv')
    # data_lm.save('tmp_lm')
    # data_lm = TextLMDataBunch.load(path, '/tmp_lm', bs=32)
    #
    # data_clas = (TextList.from_csv(path, 'notebooks/storage/Final_Intent_Dataset.csv', cols='text')
    #             .split_from_df(col=2)
    #             .label_from_df(cols=0)
    #             .databunch())
    # data_clas = TextClasDataBunch.from_csv(path, 'notebooks/storage/Final_Intent_Dataset.csv', vocab=data_lm.vocab, bs=32)
    # data_clas.save('tmp_clas')
    # learn = language_model_learner(data_lm, AWD_LSTM, drop_mult=0.3)
    # data_clas.vocab.itos = data_lm.vocab.itos
    # learn = text_classifier_learner(data_clas, arch=AWD_LSTM, drop_mult=0.5)
    # learn.load(model_file_name)
    # learn.load_encoder('LM_fine_tuned_encoder')

    # Starter model (Image Classifier)
    # data_bunch = ImageDataBunch.single_from_classes(path, classes,
    #     ds_tfms=get_transforms(), size=224).normalize(imagenet_stats)
    # learn = cnn_learner(data_bunch, models.resnet34, pretrained=False)
    # learn.load(model_file_name)

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

    return JSONResponse({'result': 'OK OK'})

    # html = path/'view'/'index.html'
    # return HTMLResponse(html.open().read())

if __name__ == '__main__':
    if 'serve' in sys.argv: uvicorn.run(app, host='0.0.0.0', port=8080)
