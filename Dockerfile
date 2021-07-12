FROM python:3.7-slim
MAINTAINER AI Arena <staff@aiarena.net>

USER root
WORKDIR /root/

# Update system
RUN apt-get update && apt-get upgrade --assume-yes --quiet=2
RUN apt-get install --assume-yes --no-install-recommends --no-show-upgraded \
    wget \
    unzip

# download bot and install requirements
RUN wget -O aiarena-discordbot.zip https://github.com/aiarena/aiarena-discordbot/archive/refs/heads/master.zip
RUN unzip aiarena-discordbot.zip -d /tmp/aiarena-discordbot/
RUN mv /tmp/aiarena-discordbot/aiarena-discordbot-master/ /root/aiarena-discordbot/
RUN rm -r /tmp/aiarena-discordbot/
RUN pip install -r /root/aiarena-discordbot/requirements.txt

WORKDIR /root/aiarena-discordbot/

# Run the bot
ENTRYPOINT [ "/usr/local/bin/python", "./bot.py" ]