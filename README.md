# Vespa News Search and Recommendations

This is a Hack Pack for TreeHacks 2025, it shows how to do basic search and recommendations using Vespa.

## Requirements
- [Docker](https://www.docker.com/) or [Podman](https://podman.io/)
- [Vespa CLI](https://docs.vespa.ai/en/vespa-cli.html)
- [Python >= 3.12](https://www.python.org/)
- [Node](https://nodejs.org/en) for the frontend
- [git-lfs](https://git-lfs.com/) for pulling the dataset

# Set up locally

Clone the repo:
```
git clone https://github.com/theodorklauritzen/vespa-news-recommendation-hack-pack.git
```

## Super quick start

This will use pretrained embeddings for users and news.

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
