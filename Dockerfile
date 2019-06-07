FROM alpine:latest
WORKDIR /emqtt
COPY runner.py requirements.txt ./
COPY emqtt ./emqtt
COPY tests ./tests
RUN apk add --no-cache python3 && pip3 install -r requirements.txt
EXPOSE 1025
CMD ["python3", "runner.py"]
