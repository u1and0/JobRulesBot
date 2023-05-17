#!/usr/bin/env python3
"""
Usage:
    uvicorn main:app --host=0.0.0.0 --port=8880 --reload
"""
import json
from collections import namedtuple
from fastapi import FastAPI, Request
from fastapi.responses import RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
import pandas as pd
import uvicorn
from lib import VectorFrame, Message, Role
from lib import LRUDict

VERSION = "v0.1.0"
# バックエンドの準備
app = FastAPI()
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")
# 就業規則ベクターの読み込み
model_df = pd.read_json("data/model-embeddings.json")
model_df = VectorFrame(model_df)
# 質問と回答のキャッシュ
ResponseCache = namedtuple("ResponseCache", ["vector_frame", "response"])
cache: LRUDict[str, ResponseCache] = LRUDict(10)


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
    """first question"""
    if query in cache:
        # キャッシュから過去の回答を取得
        regulations, response = cache[query]
        print("INFO:    Get content from cache.")
    else:
        # 関連規約の抽出
        regulations = model_df.search_regulation(query, threshold=0.7)
        # 回答の取得
        response = regulations.ask_regulation(query)
        # 回答を保存
        cache[query] = ResponseCache(regulations, response)
        print("INFO:    Use OPENAI API {} tokens".format(
            model_df.get_token_length(response)))
    messages: list[Message] = [
        Message(Role.User, query),
        Message(Role.Assistant, response),
    ]
    obj = {
        "regulation": '\n'.join(regulations.text),
        "messages": [i._asdict() for i in messages]
    }
    print(json.dumps(obj, indent=2, ensure_ascii=False))
    return obj


@app.post("/ask")
async def post_ask(query: str, messages: list[Message]):
    """follow up question"""
    # キャッシュから質問と回答を取得
    # responseはmessagesの中に入っているから_で省略
    regulations, _ = cache[query]
    # 回答の取得
    response = regulations.ask_regulation(query, messages)
    print(model_df.get_token_length(response), "tokens")
    # 回答を追加
    messages.append(Message(Role.User, query))
    messages.append(Message(Role.Assistant, response))
    obj = {
        "regulation": '\n'.join(regulations.text),
        "messages": [i._asdict() for i in messages]
    }
    print(json.dumps(obj, indent=2, ensure_ascii=False))
    return obj


if __name__ == "__main__":
    uvicorn.run("main:app")
