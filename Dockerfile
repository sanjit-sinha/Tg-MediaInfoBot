FROM ubuntu:latest
ENV LANG en_US.utf8
ENV LC_ALL en_US.UTF-8
ENV LANGUAGE en_US:en
ENV TZ=Asia/Kolkata \
    DEBIAN_FRONTEND=noninteractive

WORKDIR /usr/src/app
RUN chmod 777 /usr/src/app && \
    apt-get update -y && apt-get upgrade -y && \
    apt-get install -y git python3 python3-pip locales ffmpeg && apt-get install -y mediainfo && \
    apt-get install libsox-fmt-mp3 \    
    apt-get upgrade -y

COPY requirements.txt .
RUN pip3 install --no-cache-dir -r requirements.txt && \
    apt-get -qq purge git && apt-get -y autoremove && apt-get -y autoclean
RUN locale-gen en_US.UTF-8

COPY . .
CMD ["python3" "-m" "TelegramBot"]
