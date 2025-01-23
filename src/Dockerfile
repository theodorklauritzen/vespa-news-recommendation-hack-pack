FROM python:3

WORKDIR /app

ADD https://raw.githubusercontent.com/vespa-engine/sample-apps/refs/heads/master/news/bin/download-mind.sh ./bin/download-mind.sh
RUN chmod +x ./bin/download-mind.sh
RUN ./bin/download-mind.sh demo

ADD https://raw.githubusercontent.com/vespa-engine/sample-apps/refs/heads/master/news/src/python/convert_to_vespa_format.py ./src/python/convert_to_vespa_format.py

RUN python ./src/python/convert_to_vespa_format.py mind

FROM vespaengine/vespa:latest

# because it's easier
USER root
WORKDIR /root

COPY --from=0 /app/mind /app/mind
COPY application /root/application

RUN /usr/local/bin/start-container.sh & (sleep 20 && vespa deploy /root/application && sleep 20 && vespa feed /app/mind/vespa.json) & sleep 90

EXPOSE 8080 19071 5005
