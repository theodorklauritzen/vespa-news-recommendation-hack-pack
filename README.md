



´docker run --rm -it --publish 8080:8080 --publish 19071:19071 --name vespaNews test´

'docker cp vespaNews:/app/mind ./mind'


# Finished Demo

Just download the Docker image here: asdf asdf asdf ad

Run the web server

# Set up locally

## Download the dataset

Run the command `./sample-apps/news/bin/download-mind.sh demo`

## Download python requirements

Downlod the python requirements
`pip install -r ./sample-apps/news/requirements.txt`

## Start a new vespa container

`docker run --detach --publish 8080:8080 --publish 19071:19071 --name vespa vespaengine/vespa`

## Download vespa cli

[Vespa CLI](https://docs.vespa.ai/en/vespa-cli.html)


## Deploy the application

`vespa deploy src/application`

# Super quick start

```bash
uv sync
source .venv/bin/activate
cd src/application
vespa config set target local
docker run --detach --name vespa --hostname vespa-container \
  --publish 8080:8080 --publish 19071:19071 \
  vespaengine/vespa
vespa status deploy --wait 300 # Check if deployment api is ready
vespa deploy
cd ../..
vespa feed embeddings/vespa_user_embeddings.json --target http://localhost:8080
vespa feed embeddings/vespa_news_embeddings.json --target http://localhost:8080
cd frontend
npm install
npm run dev
# See sample users and recommendations in the application
```

## Training
