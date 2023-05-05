# Features
質問に応じた就業規則を抽出し、それに関連してChatGPTに答えさせます。

```
あなたは就業規則に関するエキスパートです。
以下に与える`関連規約`を参照し、質問に対して平易な日本語で答えてください。
就業規則以外のことには答えられません。
最後に必ず関連する規約の番号を案内してください。

# 関連規約
{ここに質問に関連した規約を入れて質問します。}
```

# Usage

```
$ python main.py
```

` http://localhost:8891/index `へアクセスして質問事項を入力し、検索を押すと回答を得られます。
  あるいは
` curl -fsSL http://localhost:8891/ask/{KEYWORD} `の{KEYWORD}に質問事項を入力して実行すると、回答と関連規約をJSONで得られます。


# Installation

```
$ git clone https://github.com/u1and0/JobRulesBot
$ cd JobRulesBot
$ pip install -r requirements.txt
```

# Optional
自身のAPIキーを入力してください。

```
$ export OPENAI_API_KEY='sk-XXXXXXX'
  # または
$ python main.py
OpenAI token: sk-XXXXXX
```


# Requirements
* fastapi
* jinja2
* numpy
* openai
* pandas
* tiktoken
* uvicorn


使用しておりませんが、依存性のため必要とされます。

* matplotlib
* plotly
* scikit-learn


see more
[【業務効率化】ChatGPTを用した就業規則の自動回答システムの開発](https://qiita.com/u1and0/items/593781e4a20388a83238)


# LICENCE
This project is licensed under the MIT License. See the [LICENSE](https://raw.githubusercontent.com/u1and0/JobRulesBot/main/LICENSE) file for more details.
