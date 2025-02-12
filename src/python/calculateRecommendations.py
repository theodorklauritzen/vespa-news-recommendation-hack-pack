import json
import sys
from newsData import NewsData
from train_cold_start import ContentBasedModel, train_model, embedding_size, set_random_seed
from createBertEmbedding import createBertEmbedding
from vespa.application import Vespa
import torch

def vespaCallback(response, id):
    if not response.is_successful():
        print("Failed to feed to Vespa")
        print(response.get_json())
        print(id)

def convertToVespaFormat(idToIndexMap, embeddings):
    ret = []

    for id, index in idToIndexMap.items():
        ret.append({
            "id": id,
            "fields": {
                "embedding": embeddings[index].tolist()
            }
        })

    return ret

def updateEmbeddings(data_loader, model):
    app = Vespa(url = "http://localhost/", port = 8080)

    user_map = data_loader.users()
    news_map = data_loader.news()
    users = torch.LongTensor(range(len(user_map)))
    news = data_loader.get_news_content_tensors()
    user_embeddings = model.get_user_embeddings(users)
    news_embeddings = model.get_news_embeddings(news)

    app.feed_iterable(
        convertToVespaFormat(news_map, news_embeddings),
        schema="news",
        operation_type="update",
        callback=vespaCallback
    )

    app.feed_iterable(
        convertToVespaFormat(user_map, user_embeddings),
        schema="user",
        operation_type="update",
        callback=vespaCallback
    )

def main():
    if (len(sys.argv) != 4):
        print("Usage: <train_impression_file> <valid_impression_file> <output_model_weights>")
        exit(1)

    set_random_seed(1)

    # read data
    print("Fetching data...")
    data_loader = NewsData(sys.argv[1], sys.argv[2])
    num_users = len(data_loader.users())
    num_news = len(data_loader.news())

    print("Number of users:", num_users)
    print("Number of news:", num_news)

    print("Creating BERT embeddings")

    # create BERT embeddings
    bert_embeddings = createBertEmbedding(data_loader.news_content.values(), True)

    # create model
    model = ContentBasedModel(num_users, num_news, embedding_size, bert_embeddings)
    # model.load_weights()

    # train model
    train_model(model, data_loader, False)

    model.save_weights(sys.argv[3])

    print("Uploading embeddings to Vespa...")
    updateEmbeddings(data_loader, model)

if __name__ == "__main__":
    main()

