# Vespa News Search and Recommendations

This is a Hack Pack for TreeHacks 2025, it shows how to do basic search and recommendations using Vespa.

The recommendation system works by calculating a BERT embedding for the news. This embedding is fed through an embedding to reduce the size to 50. Each user also has an embedding. When we calculate the embeddings for the news and user we want to train the neural network and the user embeddings. We want the dotproduct between the news embedding and a user embedding to give a score on how good the user and news article matches.

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

The fastest way is to feed pretrained data to Vespa.
First make sure that the the large files are downloaded, if not run
```bash
git lfs pull
```
Then feed the pretrained data to Vespa
```bash
vespa feed embeddings/vespa_user_embeddings.json --target http://localhost:8080
vespa feed embeddings/vespa_news_embeddings.json --target http://localhost:8080
```
Users and news should now be available in the frontend.

If you want to feed and train the model yourself, look at the section bellow.

## Download the dataset

To be able to feed the data yourself, download the dataset by running this command.
```bash
./src/sh/download_mind.sh demo
```
The dataset should now be stored in a folder called `mind`.

## Feed and manipulate data with python

Setup the python environment using

```bash
uv sync
source .venv/bin/activate
```

### Add users

```bash
python src/python/addUser.py id <user_id>
```
Or by finding user id's from the dataset
```bash
python src/python/addUser.py mind/train/behaviors.tsv
```

New users will start with a random embedding. To give recommendations we need to calculate a new embedding for all users.

### Add news

To add a simple news article run the following command, without any file with news.
```bash
python src/python/addNews.py embeddings/news_bert_transform.pt [file_with_news]
```

To upload news from the data set use the file `mind/train/news.tsv`.

### Calculate new recommendations

