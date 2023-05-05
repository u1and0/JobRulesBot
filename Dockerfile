# 就業規則に関するユーザーの疑問にチャット形式で回答する
# usage:
#   docker run -it --rm -v `pwd`/data:/work/data -p 8880:8880 u1and0/pid_classify

# Python build container
# python:alpine はnumpy, scipy, pandasのビルドに1hかかるので使用しない
# ubuntuならビルドに1分
FROM python:3.11.0-slim-bullseye as builder
WORKDIR /opt/app
RUN apt-get update &&\
    apt-get upgrade -y &&\
    apt-get install -y libfreetype6-dev \
                        libatlas-base-dev \
                        liblapack-dev
# For update image, rewrite below
#   -COPY requirements.lock /opt/app
#   +COPY requirements.txt /opt/app
COPY requirements.txt /opt/app
# Then execute `docker exec -it container_name pip freeze > requirements.lock`
RUN pip install --upgrade -r requirements.txt

# TypeScript build container
FROM node:18-alpine3.15 AS tsbuilder
COPY ./static /tmp/static
WORKDIR /tmp/static
RUN npm install -D typescript ts-node ts-node-dev
RUN npx tsc || exit 0  # Ignore TypeScript build error

# 実行コンテナ
FROM python:3.11.0-slim-bullseye as runner
WORKDIR /work
COPY --from=builder /usr/local/lib/python3.11/site-packages /usr/local/lib/python3.11/site-packages
COPY --from=tsbuilder /tmp/static/main.js /work/static/main.js

RUN useradd -r chatbot
COPY main.py /work
COPY lib/vector.py /work/lib/vector.py
COPY templates/index.html /work/templates/index.html
COPY static/icons8-chatbot.png /work/static/icons8-chatbot.png
RUN chmod -R +x /work/main.py

USER chatbot
ENV PYTHONPATH="/work"
EXPOSE 8889
CMD ["python", "main.py"]

LABEL maintainer="u1and0 <e01.ando60@gmail.com>" \
      description="就業規則に関するユーザーの疑問にチャット形式で回答する" \
      version="u1and0/JobRulesBot:v0.1.0"
