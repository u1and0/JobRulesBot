import json
from getpass import getpass
from enum import Enum
from dataclasses import dataclass
from collections import UserList
import os
import numpy as np
import pandas as pd
import openai
from openai.embeddings_utils import get_embedding, cosine_similarity
import tiktoken

try:
    openai.api_key = os.environ["CHATGPT_API_KEY"]
except KeyError:
    openai.api_key = getpass("OpenAI token:")


class Role(str, Enum):
    System = "system"
    Assistant = "assistant"
    User = "user"

    def __str__(self):
        return self.name.lower()


@dataclass
class Message:
    role: Role
    content: str

    def _asdict(self):
        return {"role": str(self.role), "content": self.content}


class VectorFrame(pd.DataFrame):
    system_prompt = """あなたは就業規則に関するエキスパートです。
    以下に与える`関連規約`を参照し、質問に対して平易な日本語で答えてください。
    就業規則以外のことには答えられません。
    最後に必ず関連する規約の番号を案内してください。

    # 関連規約
    """  # 116 tokens

    def __init__(
            self,
            *args,
            model="gpt-3.5-turbo",
            model_token_limit=4096,
            max_tokens=500,
            temperature=0.2,
            system_max_tokens=2000,  # system promptは合計で2116
            user_max_tokens=1480,
            **kwargs):
        super().__init__(*args, **kwargs)
        self.model = model
        self.model_token_limit = model_token_limit
        self.max_tokens = max_tokens
        self.temperature = temperature
        self.system_max_tokens = system_max_tokens
        self.user_max_tokens = user_max_tokens
        # 各テキストのトークンの長さを取得
        self.enc = tiktoken.encoding_for_model(self.model)
        self["token_length"] = self.text.apply(
            lambda x: len(self.enc.encode(x)))

    def get_token_length(self, *args: str):
        s = '\n'.join(args)
        return len(self.enc.encode(s))

    def search_regulation(self, query: str, threshold: float, verbose=False):
        """就業規則に関する質問を与えると、関連性の高い規約を検索して返す
        トークン数がデフォルトで2000未満になるようにして返す。
        verbose=Trueでテキストと類似度を表示する。
        """
        # 質問のベクトル化
        query_vector = get_embedding(query, engine="text-embedding-ada-002")
        # 関連性を算出
        self["similarities"] = self["embedding"].apply(
            lambda x: cosine_similarity(x, query_vector))
        # 関連性順にソート
        self.sort_values("similarities", ascending=False, inplace=True)
        # 関連性の高いものだけ抽出 かつ 2000トークン以内に収まるようにフィルター
        filtered = self[(self.similarities >= threshold) &
                        (self.token_length.cumsum() <= self.system_max_tokens)]
        if verbose:
            print("related rules:", filtered)
            print("cumsum rules tokens:", filtered.token_length.sum())
        return VectorFrame(filtered)

    def ask_regulation(self,
                       query: str,
                       messages: list[Message] = [],
                       *args,
                       **kwargs) -> str:
        """usage:
          model_df.ask_regulation("質問")
        """
        user_prompt_length = self.get_token_length(query)
        assert user_prompt_length <= self.user_max_tokens,\
            f"システムプロンプトは1473トークン以下にしてください。\
            {user_prompt_length}"

        # システムプロンプトに関連規約を追加
        # list()をつけないと各行にsystem_promptが追加されてしまう
        system_prompt = "\n".join([VectorFrame.system_prompt] +
                                  list(self.text))
        system_prompt_length = self.get_token_length(system_prompt)
        limit_token = self.system_max_tokens + \
            self.get_token_length(VectorFrame.system_prompt) + 2  # 謎の2 改行？
        assert system_prompt_length <= limit_token,\
            f"システムプロンプトは{limit_token}トークン以下にしてください。\
            {system_prompt_length} >= limit_token:{limit_token}"

        # システムプロンプトと質問をプロンプトに追加
        messages.insert(0, Message(Role.System, system_prompt))
        messages.append(Message(Role.User, query))
        # プロンプトのトークン数が制限に収まるように調整
        while True:
            message_contents = (i.content for i in messages)
            all_prompt_length = self.get_token_length(*message_contents)
            if all_prompt_length <= self.model_token_limit:
                break
            messages.pop(1)  # System promptを除いて上から順に会話履歴を削除
        assert all_prompt_length <= self.model_token_limit,\
            f"全プロンプトの合計は4096トークン以下 {all_prompt_length}"

        # ChatGPTに規約を渡していい感じに日本語に直してもらう
        completion = openai.ChatCompletion.create(
            model=self.model,
            max_tokens=self.max_tokens,
            temperature=self.temperature,
            messages=[i._asdict() for i in messages],
        )
        content = completion.choices[0].message.content
        return content


if __name__ == "__main__":
    # データ読込
    model_df = pd.read_csv("data/model-embeddings.csv", usecols=[1, 2])\
        .rename({"１ モデル就業規則": "text"}, axis=1)
    # arrayとして認識させる
    model_df['embedding'] = model_df['embedding'].apply(eval).apply(np.array)
    model_df = VectorFrame(model_df)
    # 質問
    query = "年間休日は何日ですか"
    # ここからAPI Keyが必要
    # 関連規約の抽出
    regulation = model_df.search_regulation(query)
    assert len(regulation) > 1, "関連する規約がありませんでした。別のキーワードで質問してください。"
    print("関連規約のトークン長さ:", regulation.token_length.sum())
    # 関連規約に基づいたChatGPTからの回答
    response = regulation.ask_regulation(query)
    # 質問、関連規約、回答を表示
    obj = {
        "query": query,
        "regulation": "\n".join(regulation.text),
        "response": response
    }
    print(json.dumps(obj, indent=2, ensure_ascii=False))
