
import json
import sys
from vespa.application import Vespa

from transformers import logging, BertTokenizer, BertModel
import torch

EXPECTED_FIELDS = ["news_id", "category", "url", "date", "subcategory", "title", "abstract"]

def validateData(data):
    for field in EXPECTED_FIELDS:
        if field not in data.keys():
            print(f"Missing field {field} in json document")
            return False
        
        if type(data[field]) != str:
            print(f"Field {field} is not a string")
            return False
    
    return True

def readJsonFile(filename):
    with open(filename) as file:
        data = json.load(file)
    return data

def readTSVFile(filename):
    ret = []
    with open(filename) as file:
        for line in file.readlines():

            news_data = line.split("\t")
            news_id = news_data[0]
            category = news_data[1]
            subcategory = news_data[2]
            title = news_data[3]
            abstract = news_data[4]
            url = news_data[5]

            ret.append({
                "news_id": news_id,
                "category": category,
                "subcategory": subcategory,
                "title": title,
                "abstract": abstract,
                "url": url,
                "date": "20250127"
            })

    return ret


def readFile(filename):
    fileEnding = filename.split('.')[-1].lower()
    if fileEnding == "tsv":
        return readTSVFile(filename)
    return readJsonFile(filename)

def getInputData():
    print("Fill out the fields")

    ret = {}

    for field in EXPECTED_FIELDS:
        inp = input(f"{field}: ")
        ret[field] = inp

    return ret

def convertDataToVespa(data):
    ret = []

    for datapoint in data:
        ret.append({
            "id": datapoint['news_id'],
            "fields": datapoint
        })

    return ret

# TODO: Use the class used for the mindDataset
class BertTransformer(torch.nn.Module):
    def __init__(self):
        super(BertTransformer, self).__init__()
        self.news_bert_transform = torch.nn.Linear(512, 50)

    def loadWeights(self, filename):
        state_dict = torch.load(filename)

        self.news_bert_transform.weight.copy_(state_dict['news_bert_transform.weight'])
        self.news_bert_transform.bias.copy_(state_dict['news_bert_transform.bias'])

    def forward(self, bert_embedding):
        return self.news_bert_transform(bert_embedding)


def createNewsEmbedding(data):
    # TODO: Create BERT embedding
    # Pass the bert embedding through the NN 

    tokenizer = BertTokenizer.from_pretrained('bert-base-uncased')
    model = BertModel.from_pretrained('google/bert_uncased_L-8_H-512_A-8')

    bertTransformerModel = BertTransformer()
    # bertTransformerModel.loadWeights("tmp.tbh")

    for datapoint in data:
        title = datapoint["title"]
        abstract = datapoint["abstract"]

        tokens = tokenizer(title, abstract, return_tensors="pt", max_length=100, truncation=True, padding=True)
        outputs = model(**tokens)
        embedding512 = outputs[0][0][0]
        embedding50 = bertTransformerModel.forward(embedding512)
        datapoint["embedding"] = embedding50.tolist()

    return data


def vespaCallback(response, id):
    if not response.is_successful():
        print("Failed to feed to Vespa")
        print(response.get_json())
    else:
        print("Feed successful")

def main():
    data = getInputData() if (len(sys.argv) < 2) else readFile(sys.argv[1])

    if type(data) != list:
        data = [data]

    for datapoint in data:
        if not validateData(datapoint):
            return

    data = createNewsEmbedding(data)

    dataToVespa = convertDataToVespa(data)

    app = Vespa(url = "http://localhost/", port = 8080)
    app.feed_iterable(
        dataToVespa,
        schema="news",
        callback=vespaCallback
    )

if __name__ == "__main__":
    main()

