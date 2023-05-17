"""トレーニングデータ作成
タイトルをキーに規約テキストを値としたKVオブジェクトを読み込み、
400トークンごとに分割してタイトルと結合したリストを返す。
"""
import json
import re
from typing import Optional

from more_itertools import chunked
import pandas as pd
import tiktoken
from openai.embeddings_utils import get_embedding

from .vector import VectorFrame

MODEL = "text-embedding-ada-002"
ENC = tiktoken.encoding_for_model(MODEL)


def get_token_length(*args: str):
    s = '\n'.join(args)
    return len(ENC.encode(s))


def load_data(strings: list[str]) -> VectorFrame:
    """listを読み込んでVectorFrameにする"""
    df = pd.DataFrame(strings, columns=["text"])
    df["length"] = df.text.apply(lambda x: get_token_length(x))
    return VectorFrame(df)


def split_tokens(title: str, text: str, max_tokens: int) -> list[str]:
    """規則タイトルと本文を結合したリストを返す"""
    # 改行を削除
    text = re.sub(r'\n|\r', '', text).strip()
    # スペース、タブ文字などをスペース１文字に変更
    text = re.sub(r'\t|\s+', ' ', text).strip()
    # トークン化
    tokens = ENC.encode(text)
    # 最大トークン数で分割
    chunks = chunked(tokens, max_tokens)
    # 規則タイトルと本文を結合
    title_text_tokens = [f"{title} {ENC.decode(c)}" for c in chunks]
    return title_text_tokens


def split_text(title_text: dict[str, str], max_tokens: int) -> list[str]:
    """規則のタイトルと本文を結合して、最大トーン数で分割する"""
    # 分割された規則テキストを格納するリスト
    training_data_split = []
    # 規則のタイトルと本文を結合して、最大トーン数で分割する
    for k, v in title_text.items():
        # 分割されたテキストをリストに追加
        training_data_split.extend(split_tokens(k, v, max_tokens))
    return training_data_split


def training(rules: VectorFrame,
             savefile: Optional[str] = None,
             **kwargs) -> Optional[VectorFrame]:
    """emmbedding して文字列をベクトル化します。
    実行にはOpenAI APIを使用します。
    トークンサイズに基づいた料金がかかるので
    実行する前に確認のプロンプトが出ます。
    実行後にsavefileへJSON形式で保存されます。
    """
    assert len(rules["text"]) > 0, "rules.text length must over 0"

    prompt = """この処理にはAPIトークンサイズに基づいた料金がかかります。
実行してもよろしいですか？ y/N"""
    if input(prompt).lower != "y":
        return

    # ベクトル化
    rules["embedding"] = rules.text.apply(
        lambda x: get_embedding(x, engine=MODEL))

    if savefile:
        # 処理データを保存
        rules.to_json(savefile, force_ascii=False, orient="records", **kwargs)
    else:
        return VectorFrame(rules)


if __name__ == "__main__":
    # training_data.jsonの読み込み
    with open("data/model_list.json", "r") as f:
        rules = json.load(f)
        # rules = {
        #     "title1": "text1",
        #     "title2": "text2",
        #     ...
        # }
        # text n は1000トークン以上の長さ

    # 400トークンごとに分割
    train_list = split_text(rules, 400)

    # stdoutへ出力
    print(train_list[:3])

    # As VectorFrame
    vf = load_data(train_list)

    # ベクトル化して結果をdata/result.jsonへ保存
    training(vf, savefile="./data/result.json")

    # Read result
    vf = VectorFrame(pd.read_json())
