
import sys
from vespa.application import Vespa
import numpy as np
import os
from dotenv import load_dotenv

load_dotenv()

def readUserIdsFromFile(filename):
    fileType = filename.split(".")[-1].lower()
    splitChr = '\t' if fileType == "tsv" else ','

    userIds = []

    with open(filename, "r") as file:

        for line in file.readlines():
            data = line.split(splitChr)
            userIds.append(data[1])
    return userIds

def createRandomEmbedding():
    return np.random.uniform(-1, 1, 50).tolist()

def convertToVespaData(userIds):
    return [{
        "id": userId,
        "fields": {
            "user_id": userId,
            "embedding": createRandomEmbedding()
        }
    } for userId in userIds]

def addUsersFromFile(filename):
    userIds = readUserIdsFromFile(filename)
    data = convertToVespaData(userIds)

    print("Feeding users to Vespa...")
    app = Vespa(url = os.getenv("VESPA_URL", "http://localhost/"), port = int(os.getenv("VESPA_PORT", "8080")))
    app.feed_iterable(
        data,
        schema="user",
    )

def main():
    if (len(sys.argv) < 2):
        print("The script can either add from a file or from an argumnet")
        print("With one argument, the argument is the path to impressions contains userIds.")
        print("Or it takes two arguments: id <userID>")
        return

    if (len(sys.argv) == 2):
        addUsersFromFile(sys.argv[1])
        return

    if (sys.argv[1] != "id"):
        print("To add a userId as an argumnet, the first argument must be 'id'.")
        return

    userId = sys.argv[2]

    app = Vespa(url = os.getenv("VESPA_URL", "http://localhost/"), port = int(os.getenv("VESPA_PORT", 8080)))

    response = app.feed_data_point(
        schema="user",
        data_id=userId,
        fields={
            "user_id": userId,
            "embedding": createRandomEmbedding()
        }
    )
    if (response.is_successful()):
        print("User added!")
    else:
        print("Failed to add user")
        print(response.get_json())

if __name__ == "__main__":
    main()
