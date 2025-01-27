from transformers import BertTokenizer, BertModel
from vespa.application import Vespa
import train_cold_start_wrapper


def createBERTEmbedding(title, abstract):
    tokenizer = BertTokenizer.from_pretrained('bert-base-uncased')
    model = BertModel.from_pretrained('google/bert_uncased_L-8_H-512_A-8')

    tokens = tokenizer(title, abstract, return_tensors="pt", max_length=100, truncation=True, padding=True)
    outputs = model(**tokens)
    return outputs[0].tolist()[0][0]

def createNewsEmbedding(data):
    bertEmbedding = createBERTEmbedding(data['title'], data['abstract'])


def main():

    # app = Vespa(url = "http://localhost/", port = 8080)
    #
    # with app.syncio() as session:
    #     newsResponse = session.query(
    #         yql="select * from news where true"
    #     )
    #
    # if (not newsResponse.is_successful()):
    #     print("Could not fecth news")
    #     return
    # 
    # with app.syncio() as session:
    #     userResponse = session.query(
    #         yql="select * from user where true"
    #     )
    #
    # if (not userResponse.is_successful()):
    #     print("Could not fetch users")
    #     return
    # 
    # print(newsResponse.get_json())
    # print(userResponse.get_json())

    train_cold_start_wrapper.createNewsEmbedding()


if __name__ == "__main__":
    main()

