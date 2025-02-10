#! /usr/bin/env python3
# Copyright Vespa.ai. Licensed under the terms of the Apache 2.0 license. See LICENSE in the project root.

import os
import io
import sys
import csv
import json
import random
import numpy as np
from datetime import datetime as dt
from collections import defaultdict


data_dir = sys.argv[1] if len(sys.argv) > 1 else "./mind"
embedding_dir = sys.argv[2] if len(sys.argv) > 2 else "./embeddings"

doc_type = "news"

user_embeddings_file = os.path.join(embedding_dir, "user_embeddings.tsv")
news_embeddings_file = os.path.join(embedding_dir, "news_embeddings.tsv")
user_embeddings_vespa = os.path.join(embedding_dir, "vespa_user_embeddings.json")
news_embeddings_vespa = os.path.join(embedding_dir, "vespa_news_embeddings.json")

train_news_file = os.path.join(data_dir, "train", "news.tsv")
dev_news_file = os.path.join(data_dir, "dev", "news.tsv")
train_impressions_file = os.path.join(data_dir, "train", "behaviors.tsv")
dev_impressions_file = os.path.join(data_dir, "dev", "behaviors.tsv")


def read_embeddings(file_name):
    if not os.path.exists(file_name):
        print("{} not found.".format(file_name))
        sys.exit(1)
    print("Reading embeddings data from " + file_name)
    embeddings = {}
    with io.open(file_name, "r", encoding="utf-8") as f:
        for line in f:
            id, vector = line.split("\t")
            embeddings[id] = np.array(vector.split(","), dtype=np.float32)
    return embeddings


def convert_user_embeddings():
    user_embeddings = read_embeddings(user_embeddings_file)
    with open(user_embeddings_vespa, "w") as out:
        out.write("[\n")
        for i, (user_id, embedding) in enumerate(user_embeddings.items()):
            if i > 0:
                out.write(",\n")
            embedding_str = ",".join(["%.6f" % v for v in embedding])
            out.write('{"put": "id:user:user::%s", ' % user_id +
                      '"fields": {"user_id":"%s", ' % user_id +
                      '"embedding": {"values": [%s]} }}' % embedding_str)
        out.write("\n]\n")


def convert_news_embeddings(click_map):
    news_embeddings = read_embeddings(news_embeddings_file)
    with open(news_embeddings_vespa, "w") as out:
        out.write("[\n")
        for i, (news_id, embedding) in enumerate(news_embeddings.items()):
            if i > 0:
                out.write(",\n")
            embedding_str = ",".join(["%.6f" % v for v in embedding])
            out.write('{"update": "id:news:news::%s", ' % news_id +
                      '"fields": {"embedding": {"assign": { "values": [%s]} }}}' % embedding_str)
        out.write("\n]\n")

def read_impressions_file(file_name, click_map):
    if not os.path.exists(file_name):
        print("{} not found.".format(file_name))
        sys.exit(1)
    print("Reading impressions data from " + file_name)

    with io.open(file_name, "r", encoding="utf-8") as f:
        field_list = ["id", "user_id", "timestamp", "history", "impressions"]
        reader = csv.DictReader(f, delimiter="\t", fieldnames=field_list)
        for line in reader:
            for impression in line["impressions"].split(" "):
                news_id, label = impression.split("-")
                click_map[news_id]["impressions"] += 1
                if label == "1":
                    click_map[news_id]["clicks"] += 1

def get_news_embeddings():
    news_embeddings = read_embeddings(news_embeddings_file)
    news_id_to_vespa_embedding = {}
    for news_id, embedding in news_embeddings.items():
        embedding_str = {"values": ["%.6f" % v for v in embedding]}
        news_id_to_vespa_embedding[news_id] = embedding_str
    return news_id_to_vespa_embedding

def convert_file(output, file_name, docids, click_map):
    if not os.path.exists(file_name):
        print("{} not found.".format(file_name))
        sys.exit(1)
    print("Reading news data from " + file_name)

    news_id_to_vespa_embedding = get_news_embeddings()

    with io.open(file_name, "r", encoding="utf-8") as f:

        field_list = ["news_id", "category", "subcategory", "title", "abstract", "url", "title_entities", "abstract_entities"]
        include_fields = set(field_list[0:6])

        reader = csv.DictReader(f, delimiter="\t", fieldnames=field_list)
        for line in reader:
            if line["news_id"] in docids:
                continue
            if len(docids) > 0:
                output.write(",\n")
            docid = line["news_id"]
            docids.add(docid)

            clicks = click_map[docid]["clicks"]
            impressions = click_map[docid]["impressions"]

            doc = {"put": f"id:{doc_type}:{doc_type}::{docid}", "fields" : {} }
            for field in include_fields:
                doc["fields"][field] = line[field]
            doc["fields"]["date"] = generate_random_date()  # data set does not include a publish date
            doc["fields"]["clicks"] = clicks
            doc["fields"]["impressions"] = impressions
            if docid in news_id_to_vespa_embedding:
                doc["fields"]["embedding"] = news_id_to_vespa_embedding[docid]
            else:
                print(f"Warning: no embedding found for {docid}")
            json.dump(doc, output)

def generate_random_date():
    random_date = dt.fromtimestamp(random.randint(1572562800, 1573686000))
    return int(dt.strftime(random_date, "%Y%m%d"))



def main():
    click_map = defaultdict(lambda: {"clicks":0,"impressions":0})
    read_impressions_file(train_impressions_file, click_map)
    read_impressions_file(dev_impressions_file, click_map)

    convert_user_embeddings()
    with open(news_embeddings_vespa, "w") as out:
        out.write("[\n")
        docids = set()
        convert_file(out, train_news_file, docids, click_map)
        convert_file(out, dev_news_file, docids, click_map)
        out.write("\n]\n")
        print("{} documents".format(len(docids)))



if __name__ == "__main__":
    main()
