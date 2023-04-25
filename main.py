#!/usr/bin/env python3
import json
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
    related_rules = model_df.regulation_search(query,
                                               threshold=0.7,
                                               verbose=True)
    related_rules_str = '\n'.join(related_rules.text)
    resp = related_rules.ask_regulation(query)
    print(model_df.get_token_length(resp), "tokens")
    obj = {
        "query": query,
        "response": resp,
        "related_rules": related_rules_str
    }
    print(json.dumps(obj, indent=2, ensure_ascii=False))
    return obj


if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8889)
