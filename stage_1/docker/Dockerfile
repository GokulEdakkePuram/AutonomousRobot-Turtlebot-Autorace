#This is a sample Image
FROM ubuntu:22.04
COPY src/ /iki_workspace/stage_1
RUN apt-get update
RUN apt-get install -y git
RUN apt update
RUN apt install -y htop bmon vim
CMD ["echo","Image created"]
