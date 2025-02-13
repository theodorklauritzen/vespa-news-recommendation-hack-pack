from transformers import logging, BertTokenizer, BertModel
import torch
import time

logging.set_verbosity_error()

def createBertEmbedding(data, printStats = False):
    tokenizer = BertTokenizer.from_pretrained('bert-base-uncased')
    model = BertModel.from_pretrained('google/bert_uncased_L-8_H-512_A-8')
    ret = torch.empty([len(data), 512])

    t = time.time()
    with torch.no_grad():
        for i, datapoint in enumerate(data):
            title = datapoint["title"]
            abstract = datapoint["abstract"]

            tokens = tokenizer(title, abstract, return_tensors="pt", max_length=100, truncation=True, padding=True)
            outputs = model(**tokens)
            embedding512 = outputs[0][0][0]
            ret[i] = embedding512

            if len(data) > 100 and printStats and i % (len(data)//100) == (len(data)//100 - 1):
                print("Completed {} bert-embeddings ({:.0f} %) [{:.2f} s]".format(i + 1, 100.0 *(i+1)/len(data), time.time()-t))
                t = time.time()

    return ret
