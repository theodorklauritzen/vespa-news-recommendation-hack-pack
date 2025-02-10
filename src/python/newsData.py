import random
from vespa.application import Vespa
import torch
from torch.utils.data import DataLoader, TensorDataset, RandomSampler

class NewsData:

    def __init__(self, impressions_file):

        self.app = Vespa(url = "http://localhost/", port = 8080)
        self.news_map = {}
        self.user_map = {}
        self.train_impressions = []
        self.valid_impressions = []

        self.news_content = {}

        self.__impression_file = impressions_file

    def fecthData(self):
        with self.app.syncio() as session:

            userResponse = session.query(
                yql="select user_id from user where true"
            )

            if (not userResponse.is_successful()):
                print("Could not fetch users")
                return

            newsResponse = session.query(
                yql="select news_id, title, abstract from news where true"
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
            self.news_content[news['news_id']] = {
                'title': news['title'],
                'abstract': news['abstract']
            }

        
        with open(self.__impression_file) as file:
            for line in file.readlines():
                lineId, userId, history, impressions = [ i.strip() for i in line.split(',') ]
                
                news_indicies, labels = self.find_labels(impressions.split(" "), history.split(" "))
                self.train_impressions.append({
                    'user_index': self.lookup_user_index(userId),
                    'news_indicies': news_indicies,
                    'labels': labels
                })

        print(self.train_impressions)

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

    def sampleTrainingData(self, batch_size, num_negatives, prob=1.0):

        userIndicies = []
        newsIdicies = []
        labels = []

        for impression in self.train_impressions:
            if random.random() <= prob:
                self.addImpression(impression, userIndicies, newsIdicies, labels, num_negatives)

        dataSet = TensorDataset(
            torch.LongTensor(userIndicies),
            torch.LongTensor(newsIdicies),
            torch.FloatTensor(labels)
        )
        generator = torch.Generator()
        randomSampler = RandomSampler(dataSet, generator=generator)
        return DataLoader(dataSet, batch_size=batch_size, sampler=randomSampler)

    # Convert training data, to three different lists.
    # Each row in userIndicies and NewsIndicies includes an id
    # The corresponding row in labels, label if the article was clicked on or skipped
    def addImpression(self, impression, userIndicies, newsIndicies, labels, num_negatives):
        userIndex = impression['user_index']
        positive, negative = self.findClicked(impression['news_indicies'], impression['labels'])
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
