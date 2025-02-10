# from transformers import BertTokenizer, BertModel
# from vespa.application import Vespa

import sys
from newsData import NewsData

def main():
    data_loader = NewsData(sys.argv[1])

    data_loader.fecthData()

    dataSet = data_loader.sampleTrainingData(10, 10)
    print(dataSet)

if __name__ == "__main__":
    main()

