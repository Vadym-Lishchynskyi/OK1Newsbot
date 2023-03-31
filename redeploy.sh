#!/bin/bash

# shellcheck disable=SC2164
cd /home/ubuntu/OK1Newsbot

git pull

docker stop ok1_news_bot_inst

docker rm ok1_news_bot_inst

docker build -t ok1_news_bot .

docker run -d --name ok1_news_bot_inst ok1_news_bot
