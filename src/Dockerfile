FROM python:3

WORKDIR /app

# Download dataset
ADD https://raw.githubusercontent.com/vespa-engine/sample-apps/refs/heads/master/news/bin/download-mind.sh ./bin/download-mind.sh
RUN chmod +x ./bin/download-mind.sh
RUN ./bin/download-mind.sh demo

# Convert dataset to feed to Vespa
ADD https://raw.githubusercontent.com/vespa-engine/sample-apps/refs/heads/master/news/src/python/convert_to_vespa_format.py ./src/python/convert_to_vespa_format.py
RUN python ./src/python/convert_to_vespa_format.py mind

# Download requirements
ADD https://raw.githubusercontent.com/vespa-engine/sample-apps/refs/heads/master/news/requirements.txt ./src/python/requirements.txt
RUN python3 -m pip install -r ./src/python/requirements.txt

# Create embeddings - Based on what the users have clicked on
# ADD https://raw.githubusercontent.com/vespa-engine/sample-apps/refs/heads/master/news/src/python/train_mf.py ./src/python/train_mf.py
# RUN python3 ./src/python/train_mf.py mind 10

# Download BERT embeddings - Embeddings for the aticles based on content of the articles
ADD https://data.vespa-cloud.com/sample-apps-data/mind_news_embedding.tsv ./mind/train/news_embeddings.tsv
ADD https://data.vespa-cloud.com/sample-apps-data/mind_news_embedding_dev.tsv ./mind/dev/news_embeddings.tsv

# Train coldstart
ADD https://raw.githubusercontent.com/vespa-engine/sample-apps/refs/heads/master/news/src/python/mind_data.py ./src/python/mind_data.py
ADD https://raw.githubusercontent.com/vespa-engine/sample-apps/refs/heads/master/news/src/python/metrics.py ./src/python/metrics.py
ADD https://raw.githubusercontent.com/vespa-engine/sample-apps/refs/heads/master/news/src/python/train_cold_start.py ./src/python/train_cold_start.py
RUN python3 ./src/python/train_cold_start.py mind 10

# Convert embeddings to vespa format
ADD https://raw.githubusercontent.com/vespa-engine/sample-apps/refs/heads/master/news/src/python/convert_embeddings_to_vespa_format.py ./src/python/convert_embeddings_to_vespa_format.py
RUN python3 ./src/python/convert_embeddings_to_vespa_format.py mind

# Calculate Click Trough Rate
ADD https://raw.githubusercontent.com/vespa-engine/sample-apps/refs/heads/master/news/src/python/create_category_ctrs.py ./src/python/create_category_ctrs.py
RUN python3 ./src/python/create_category_ctrs.py mind

FROM vespaengine/vespa:latest

# because it's easier
USER root
WORKDIR /root

COPY --from=0 /app/mind /app/mind
COPY application /root/application

RUN /usr/local/bin/start-container.sh & (sleep 20 && vespa deploy /root/application --wait 60 && vespa feed /app/mind/vespa.json && vespa feed /app/mind/vespa_user_embeddings.json && vespa feed /app/mind/vespa_news_embeddings.json && vespa feed /app/mind/global_category_ctr.json && vespa feed /app/mind/news_category_ctr_update.json) & sleep 100

EXPOSE 8080 19071 5005
