import random
from vespa.application import Vespa
import torch
from torch.utils.data import DataLoader, TensorDataset, RandomSampler

class NewsData:#

    def __init__(self, train_impressions_file, valid_impressions_file):

        self.app = Vespa(url = "http://localhost/", port = 8080)
        self.news_map = {}
        self.user_map = {}
        self.train_impressions = []
        self.valid_impressions = []

        self.news_content = {}

        self.__train_impression_file = train_impressions_file
        self.__valid_impression_file = valid_impressions_file

        self.fecthData()

    def fecthData(self):
        with self.app.syncio() as session:

            userResponse = session.query(
                yql="select user_id from user where true",
                queryProfile="manyHits",
            )

            if (not userResponse.is_successful()):
                print("Could not fetch users")
                return

            newsResponse = session.query(
                yql="select news_id, title, abstract from news where true",
                queryProfile="manyHits",
            )

            if (not newsResponse.is_successful()):
                print("Could not fetch news")
                return
        
        userIds = [ user['fields']['user_id'] for user in userResponse.get_json()['root']['children'] ]
        self.fillDataDict(self.user_map, userIds)
        newsResponseJson = newsResponse.get_json()['root']['children']
        newsIds = [ news['fields']['news_id'] for news in newsResponseJson ]
        self.fillDataDict(self.news_map, newsIds)

        for news in newsResponseJson:
            newsObj = news['fields']
            self.news_content[newsObj['news_id']] = {
                'title': newsObj['title'] if 'title' in newsObj else '',
                'abstract': newsObj['abstract'] if 'abstract' in newsObj else ''
            }

        self.readImpressionFile(self.__train_impression_file, self.train_impressions)
        self.readImpressionFile(self.__valid_impression_file, self.valid_impressions)
    
    def readImpressionFile(self, filename, store):
        with open(filename) as file:
            fileType = filename.split('.')[-1].lower()
            splitChr = ',' if fileType == 'csv' else '\t'
            for line in file.readlines():
                lineId, userId, date, history, impressions = [ i.strip() for i in line.split(splitChr) ]
                
                news_indices, labels = self.find_labels(impressions.split(" "), history.split(" "))
                store.append({
                    'user_index': self.lookup_user_index(userId),
                    'news_indices': news_indices,
                    'labels': labels
                })

    def users(self):
        return self.user_map

    def news(self):
        return self.news_map

    def fillDataDict(self, dataDict, data):
        for i in range(len(data)):
            dataDict[data[i]] = i

    def find_labels(self, impressions, history):
        news_indices = []
        labels = []
        for impression in impressions:
            news_id, label = impression.split("-")
            if news_id not in history:  # don't add news previously clicked (in history)
                news_indices.append(self.lookup_news_index(news_id))
                labels.append(int(label))
        return news_indices, labels

    def lookup_user_index(self, user_id):
        return self.lookup_index(user_id, self.user_map)

    def lookup_news_index(self, news_id):
        return self.lookup_index(news_id, self.news_map)

    def lookup_index(self, id, map):
        if id not in map:
            map[id] = len(map)
        return map[id]

    def sample_training_data(self, batch_size, num_negatives, prob=1.0):

        userIndices = []
        newsIndices = []
        labels = []

        for impression in self.train_impressions:
            if random.random() <= prob:
                self.addImpression(impression, userIndices, newsIndices, labels, num_negatives)

        dataSet = TensorDataset(
            torch.LongTensor(userIndices),
            torch.LongTensor(newsIndices),
            torch.FloatTensor(labels)
        )
        generator = torch.Generator()
        randomSampler = RandomSampler(dataSet, generator=generator)
        return DataLoader(dataSet, batch_size=batch_size, sampler=randomSampler)

    # TODO: This need to be created to validate the results
    def sample_valid_data(self, prob=1.0, train=False):
        data = []
        impressions = self.train_impressions if train else self.valid_impressions
        for impression in impressions:
            if random.random() <= prob:
                news_indices = impression["news_indices"]
                labels = impression["labels"]
                user_index = [ impression["user_index"] ] * len(labels)
                if sum(labels) > 0 and sum(labels) != len(labels):
                    data.append([
                        torch.LongTensor(user_index),
                        torch.LongTensor(news_indices),
                        torch.FloatTensor(labels)
                    ])
        return data

    # Convert training data, to three different lists.
    # Each row in userIndicies and NewsIndicies includes an id
    # The corresponding row in labels, label if the article was clicked on or skipped
    def addImpression(self, impression, userIndicies, newsIndicies, labels, num_negatives):
        userIndex = impression['user_index']
        positive, negative = self.findClicked(impression['news_indices'], impression['labels'])
        # Positive = news that the user clicked on
        # Negative = news that the user skipped

        # TODO: Finish func
        for positive_news_index in positive:
            userIndicies.append(userIndex)
            newsIndicies.append(positive_news_index)
            labels.append(1)

            for negative_news_index in random.sample(negative, min(num_negatives, len(negative))):
                userIndicies.append(userIndex)
                newsIndicies.append(negative_news_index)
                labels.append(0)

    def findClicked(self, news_ids, labels):
        clicked = []
        skipped = []
        for news_id, label in zip(news_ids, labels):
            if label > 0:
                clicked.append(news_id)
            else:
                skipped.append(news_id)

        return clicked, skipped

    def get_news_content_tensors(self):
        num_docs = len(self.news_map)

        return torch.LongTensor(range(0, num_docs))
