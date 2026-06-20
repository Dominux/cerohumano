FROM ollama/ollama:0.30.10-rc1

RUN apt update && apt install -y curl git-lfs

WORKDIR /app

COPY ./run.sh ./
COPY ./modelfiles ./modelfiles

ENTRYPOINT [ "sh" ]
CMD [ "./run.sh" ]
