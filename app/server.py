from starlette.applications import Starlette
from starlette.responses import HTMLResponse, JSONResponse, FileResponse
from starlette.staticfiles import StaticFiles
from starlette.middleware.cors import CORSMiddleware
from starlette.routing import Route, Mount
from starlette.templating import Jinja2Templates
import uvicorn
import aiohttp
import asyncio
from io import BytesIO

import sys
from os.path import join
from pathlib import Path

from fastai import *
from fastai.text import *
import torch
import numpy as np
import pickle

templates = Jinja2Templates(directory='app/templates')

path = Path(__file__).parent


async def homepage(request):
    ''' Home page '''

    return templates.TemplateResponse('index.html', {'request': request})


async def chat_window(request):
    ''' Chat window '''
    return templates.TemplateResponse('chat.html', {'request': request})

routes = [
    Route('/', endpoint=homepage),
    Route('/chat', endpoint=chat_window),
    Mount('/static', StaticFiles(directory='app/static'), name='static')
]

# ULMFiT
model_file_name = 'ULMFiT_classifier_model_cpu'
classes = ['account_blocked','application_status','apr','balance','bill_balance','bill_due','card_declined','credit_limit','credit_limit_change','credit_score','damaged_card','direct_deposit','exchange_rate','expiration_date','freeze_account','improve_credit_score','insurance','insurance_change','interest_rate','international_fees','min_payment','new_card','oos','order_checks','pay_bill','pin_change','redeem_rewards','replacement_card_duration','report_fraud','report_lost_card','rewards_balance','rollover_401k','taxes','transactions','transfer']

async def setup_learner():
    ''' Load model '''
    learn = load_learner(path, 'models/ULMFiT_classifier_model_cpu.pkl')

    return learn

loop = asyncio.get_event_loop()
tasks = [asyncio.ensure_future(setup_learner())]
learn = loop.run_until_complete(asyncio.gather(*tasks))[0]
loop.close()


app = Starlette(debug=True, routes=routes)
app.add_middleware(CORSMiddleware, allow_origins=[
                   '*'], allow_headers=['X-Requested-With', 'Content-Type'])


@app.route("/create-entry", methods=["POST"])
async def create_entry(request):
    ''' Process and analyze new message entry '''
    print("Send button clicked!")

    data = await request.json()
    message = data['message']

    x = learn.predict(message)
    y = str(x[0])
    print(y)

    return JSONResponse({'result': 'I have identified your question to be in the category: ' + y})

if __name__ == '__main__':
    if 'serve' in sys.argv:
        uvicorn.run(app, host='0.0.0.0', port=8080)
