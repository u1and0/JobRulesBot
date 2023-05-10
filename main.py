#!/usr/bin/env python3
"""
Usage:
    uvicorn main:app --host=0.0.0.0 --port=8880 --reload
"""
import json
from fastapi import FastAPI, Request
from fastapi.responses import RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
import pandas as pd
import uvicorn
from lib.vector import VectorFrame, Message
from lib.cache import Cache

cache = Cache()

VERSION = "v0.1.0"
# バックエンドの準備
app = FastAPI()
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")
# 就業規則ベクターの読み込み
model_df = pd.read_json("data/model-embeddings.json")
model_df = VectorFrame(model_df)


@app.get("/")
async def root():
    """/indexへリダイレクト"""
    return RedirectResponse("/index")


@app.get("/index")
async def index(request: Request):
    """メインページ"""
    return templates.TemplateResponse("index.html", {
        "request": request,
        "version": VERSION,
    })


@app.get("/hello")
async def hello():
    """サーバー生きているか確認"""
    return {"message": "hello job rules bot!"}


@app.get("/ask/{query}")
async def get_ask(query: str):
    regulations = model_df.search_regulation(query, threshold=0.7)
    response = regulations.ask_regulation(query)
    print(model_df.get_token_length(response), "tokens")
    regulatinos_str = '\n'.join(regulations.text)
    obj = {"query": query, "response": response, "regulation": regulatinos_str}
    print(json.dumps(obj, indent=2, ensure_ascii=False))
    return obj


@app.post("/ask")
async def post_ask(query: str, messages: list[Message]):
    regulations = cache[query]
    response = regulations.ask_regulation(query, messages)
    print(model_df.get_token_length(response), "tokens")
    regulatinos_str = '\n'.join(regulations.text)
    obj = {"query": query, "response": response, "regulation": regulatinos_str}
    print(json.dumps(obj, indent=2, ensure_ascii=False))
    return obj


if __name__ == "__main__":
    uvicorn.run("main:app")
