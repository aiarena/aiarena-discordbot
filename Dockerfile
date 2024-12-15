FROM python:3.8-slim
LABEL org.opencontainers.image.authors="staff@aiarena.net"

WORKDIR /bot/

COPY bot.sh ./
RUN chmod +x bot.sh

COPY requirements.txt ./
RUN pip install -r requirements.txt

COPY *.py ./
COPY cogs ./cogs/

ENTRYPOINT [ "/bin/bash", "-c", "./bot.sh" ]
