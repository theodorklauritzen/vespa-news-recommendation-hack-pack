
import json
import sys
from vespa.application import Vespa

import train_cold_start_wrapper

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

def createNewsEmbedding(data):
    createNewsEmbedding = train_cold_start_wrapper.prepareToCreateNewsEmbedding()

    for datapoint in data:
        datapoint['embedding'] = createNewsEmbedding(datapoint)

    return data


def vespaCallback(response, id):
    if not response.is_successful():
        print("Failed to feed to Vespa")
        print(response.get_json())
    else:
        print("Feed successful")

def main():
    data = getInputData() if (len(sys.argv) < 2) else readJsonFile(sys.argv[1])

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

