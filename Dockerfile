FROM alpine:latest
WORKDIR /emqtt
COPY requirements.txt ./
RUN apk add --no-cache python3 py3-pip && pip3 install -r requirements.txt
COPY runner.py ./
COPY emqtt ./emqtt
COPY tests ./tests
EXPOSE 1025
CMD ["python3", "runner.py"]
