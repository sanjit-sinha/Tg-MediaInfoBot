FROM ubuntu:20.04
COPY . .
ENV DEBIAN_FRONTEND=noninteractive
RUN apt-get update -y
RUN apt-get upgrade -y
RUN apt-get -y install wget ffmpeg
RUN wget https://mediaarea.net/repo/deb/repo-mediaarea_1.0-20_all.deb
RUN dpkg -i repo-mediaarea_1.0-20_all.deb
RUN apt-get update -y
RUN apt-get -y install mediainfo megatools python3-pip sox
RUN pip install --upgrade bs4 lxml google-api-python-client google-auth-httplib2 google-auth-oauthlib pycryptodomex pillow pyrogram tgcrypto pycryptodomex python-dotenv m3u8
RUN chmod +x start.sh
