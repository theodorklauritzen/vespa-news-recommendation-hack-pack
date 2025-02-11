import os
import json
import sys
import time
from vespa.application import Vespa

from createBertEmbedding import createBertEmbedding
import torch


EXPECTED_FIELDS = ["news_id", "category", "url", "date", "subcategory", "title", "abstract"]
BATCH_SIZE = 500

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

def createNewsEmbedding(data, bertTransformerModel, printStats = True):

    if (bertTransformerModel.in_features != 512 or bertTransformerModel.out_features != 50):
        print("The model needs to have 512 in_features and 50 out_features.")
        exit(1)

    bertEmbeddings = createBertEmbedding(data, printStats)

    t = time.time()
    for i, datapoint in enumerate(data):
        embedding512 = bertEmbeddings[i]
        embedding50 = bertTransformerModel.forward(embedding512)
        datapoint["embedding"] = embedding50.tolist()

        if len(data) > 100 and printStats and i % (len(data)//100) == (len(data)//100 - 1):
            print("Completed {} embeddings convertion ({:.0f} %) [{:.2f} s]".format(i + 1, 100.0 *(i+1)/len(data), time.time()-t))
            t = time.time()

    return data


def vespaCallback(response, id):
    if not response.is_successful():
        print("Failed to feed to Vespa")
        print(response.get_json())

def processsBatch(data, model):
    data = createNewsEmbedding(data, model, False)

    dataToVespa = convertDataToVespa(data)

    app = Vespa(url = "http://localhost/", port = 8080)
    app.feed_iterable(
        dataToVespa,
        schema="news",
        callback=vespaCallback
    )

def main():
    if (len(sys.argv) < 2):
        print("Usage: <nn_model_file> [file_with_news]")
        return
    data = getInputData() if (len(sys.argv) < 3) else readFile(sys.argv[2])

    if type(data) != list:
        data = [data]

    for datapoint in data:
        if not validateData(datapoint):
            return

    bertTransformerModel = torch.load(sys.argv[1], weights_only=False)
    bertTransformerModel.eval()

    i = 0
    t = time.time()
    print("Processing data in batches...")
    while i < len(data):
        processsBatch(data[i:min(i + BATCH_SIZE, len(data))], bertTransformerModel)
        i += BATCH_SIZE

        if (len(data) > BATCH_SIZE):
            print(f"Uploaded {i}/{len(data)} ({(i / len(data) * 100):.2f}%) in {time.time() - t:.2f}s")

if __name__ == "__main__":
    main()

