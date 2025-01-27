



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

