from transformers import BertTokenizer, BertModel
import torch

def createBertEmbedding(data):
    tokenizer = BertTokenizer.from_pretrained('bert-base-uncased')
    model = BertModel.from_pretrained('google/bert_uncased_L-8_H-512_A-8')
    ret = torch.empty([len(data), 512])

    for i, datapoint in enumerate(data):
        title = datapoint["title"]
        abstract = datapoint["abstract"]

        tokens = tokenizer(title, abstract, return_tensors="pt", max_length=100, truncation=True, padding=True)
        outputs = model(**tokens)
        embedding512 = outputs[0][0][0]
        ret[i] = embedding512

    return ret
