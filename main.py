#!/usr/bin/env python3
import numpy as np
import pandas as pd
from fastapi import FastAPI
import uvicorn
from lib.vector import VectorFrame

app = FastAPI()
# 就業規則ベクターの読み込み
model_df = pd.read_csv("data/vkijun-embeddings.csv", usecols=[1, 3])
model_df['embedding'] = model_df['embedding'].apply(eval).apply(np.array)
model_df = VectorFrame(model_df)
print(model_df)


@app.get("/ask/{query}")
async def get_ask(query: str):
    ans = model_df.ask_regulation(query, threshold=0.7, verbose=True)
    print(model_df.get_token_length(ans), "tokens")
    obj = {"query": query, "answer": ans}
    print(obj)
    return obj


if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8889)
