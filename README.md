# Vespa News Search and Recommendations

This is a Hack Pack for TreeHacks 2025, it shows how to do basic search and recommendations using Vespa.

## Requirements
- [Docker](https://www.docker.com/) or [Podman](https://podman.io/)
- [Vespa CLI](https://docs.vespa.ai/en/vespa-cli.html)
- [UV](https://docs.astral.sh/uv/getting-started/installation/) python package and project manager or [Python >= 3.12](https://www.python.org/)
- [Node](https://nodejs.org/en) for the frontend
- [git-lfs](https://git-lfs.com/) for pulling the dataset

# Set up locally

Clone the repo:
```bash
git clone https://github.com/theodorklauritzen/vespa-news-recommendation-hack-pack.git
```

Start a Vespa container using Docker
```bash
docker run --detach --name vespa --hostname vespa-container \
  --publish 8080:8080 --publish 19071:19071 \
  vespaengine/vespa
```

Deploy the Vespa Application
```bash
vespa config set target local
vespa status deploy --wait 300
vespa deploy src/application
```

Start the fontend
```bash
cd frontend
npm install
npm run dev
```
The frontend should now be available on [http://localhost:3000/](http://localhost:3000/).

## Feed data to Vespa

The fastes way is to feed pretrained data to Vespa. Do this by running the two following commands
```bash
vespa feed embeddings/vespa_user_embeddings.json --target http://localhost:8080
vespa feed embeddings/vespa_news_embeddings.json --target http://localhost:8080
# See sample users and recommendations in the application
```

If you want to feed and trin the model yourself, llok at the section bellow.

## Feed data with python

Setup the python enviromnet using

```bash
uv sync
source .venv/bin/activate
```
