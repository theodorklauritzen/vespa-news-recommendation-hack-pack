import json
import sys
from transformers import BertTokenizer, BertModel
import torch

EXPECTED_FIELDS = ["docid", "category", "subcategory", "title", "abstract"]

BERT_EMBEDDING_SIZE = 512
EMBEDDING_SIZE = 50

def validateData(data):
    for field in EXPECTED_FIELDS:
        if field not in data.keys():
            print(f"Missing field {field} in json document")
            return False
        
        if type(data[field]) != str:
            print(f"Field {field} is not a string")
            return False
    
    return True

def createLargeEmbedding(data):
    tokenizer = BertTokenizer.from_pretrained('bert-base-uncased')
    model = BertModel.from_pretrained('google/bert_uncased_L-8_H-512_A-8')
    title = data["title"]
    abstract = data["abstract"]

    tokens = tokenizer(title, abstract, return_tensors="pt", max_length=100, truncation=True, padding=True)
    outputs = model(**tokens)
    return outputs[0].tolist()[0][0]

def storeData(data, embedding):
    with open("toVespa.json", "w") as file:
        json.dump({
            "put": "id:news:news::" + data["docid"],
            "fields": {
                "category": data["category"],
                "url": "https://www.msn.com/en-us/lifestyle/lifestyleroyals/the-brands-queen-elizabeth,-prince-charles,-and-prince-philip-swear-by/ss-AAGH0ET?ocid=chopendata",
                "abstract": data["abstract"],
                "news_id": data["docid"],
                "title": data["title"],
                "subcategory": data["subcategory"],
                "date": 20191105,
                "clicks": 0,
                "impressions": 0,
                "embedding": embedding
            }
        }, file)

def transformEmbedding(longEmbedding):
    bertTransform = torch.nn.Linear(BERT_EMBEDDING_SIZE, EMBEDDING_SIZE)
    contentTransform = torch.nn.Linear(EMBEDDING_SIZE * 5, EMBEDDING_SIZE)

    # Transform BERT representation to a shorter form
    bertEmbedding = torch.sigmoid(bertTransform(longEmbedding))





def main():
    if (len(sys.argv) < 2):
        print("Pass one argumnet, the josn-file to feed to vespa")
        return

    filename = sys.argv[1]
    with open(filename) as file:
        data = json.load(file)

    print(data)
    if not validateData(data):
        return
    embedding = createLargeEmbedding(data)

    print(f"hmm the length of the tensor: {len(embedding)}")

    storeData(data, embedding)


if __name__ == "__main__":
    main()
