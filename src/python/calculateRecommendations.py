# from transformers import BertTokenizer, BertModel
# from vespa.application import Vespa

import sys
from newsData import NewsData
from train_cold_start import ContentBasedModel, train_model, embedding_size, set_random_seed
from createBertEmbedding import createBertEmbedding

def main():
    set_random_seed(1)

    # read data
    data_loader = NewsData(sys.argv[1])
    num_users = len(data_loader.users())
    num_news = len(data_loader.news())

    # create BERT embeddings
    bert_embeddings = createBertEmbedding(data_loader.news_content.values())

    # create model
    model = ContentBasedModel(num_users, num_news, embedding_size, bert_embeddings)
    # model.load_weights()

    # train model
    train_model(model, data_loader, False)

    model.save_weights("linearLayer.pt")

if __name__ == "__main__":
    main()

