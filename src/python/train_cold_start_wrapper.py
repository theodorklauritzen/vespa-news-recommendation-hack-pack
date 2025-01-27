from train_cold_start import *
from transformers import BertTokenizer, BertModel

store_file = os.path.join(data_dir, "modelParameters.pt")

def createBertEmbedding(data):
    tokenizer = BertTokenizer.from_pretrained('bert-base-uncased')
    model = BertModel.from_pretrained('google/bert_uncased_L-8_H-512_A-8')
    title = data["title"]
    abstract = data["abstract"]

    tokens = tokenizer(title, abstract, return_tensors="pt", max_length=100, truncation=True, padding=True)
    outputs = model(**tokens)

    return outputs[0][0, 0]

def prepareToCreateNewsEmbedding():
    data_dir = sys.argv[2] if len(sys.argv) > 2 else "../../mind/"

    train_news_file = os.path.join(data_dir, "train", "news.tsv")
    valid_news_file = os.path.join(data_dir, "dev", "news.tsv")
    train_impressions_file = os.path.join(data_dir, "train", "behaviors.tsv")
    valid_impressions_file = os.path.join(data_dir, "dev", "behaviors.tsv")

    data_loader = MindData(train_news_file, train_impressions_file, valid_news_file, valid_impressions_file)
    num_users = len(data_loader.users())
    num_news = len(data_loader.news())
    num_categories = len(data_loader.categories())
    num_subcategories = len(data_loader.subcategories())
    num_entities = len(data_loader.entities())

    print(data_loader.categories())
    print(data_loader.subcategories())

    sample_data = data_loader.sample_training_data(batch_size, negative_sample_size)
    for bathcNum, batch in enumerate(sample_data):
        user_ids, news_ids, category_ids, subcategory_ids, entities, labels = batch
        print(user_ids)
        print(news_ids)
        break
    # num_users = 5000
    # num_news = 28603
    # num_categories = 17
    # num_subcategories = 240
    # num_entities = 13249

    # read BERT embeddings
    # bert_embeddings = read_bert_embeddings(data_loader, train_embeddings_file, valid_embeddings_file)
    bert_embeddings = np.zeros([num_news, 512])
    bert_embeddings = torch.FloatTensor(bert_embeddings)

    # create model
    model = ContentBasedModel(num_users, num_news, num_categories, num_subcategories, num_entities, embedding_size, bert_embeddings)
    model.load_state_dict(torch.load(store_file, weights_only=True))

    def createNewsEmbedding(data):
        # Transform BERT representation to a shorter embedding
        bert_embeddings = createBertEmbedding(data)
        bert_embeddings = model.news_bert_transform(bert_embeddings)
        bert_embeddings = torch.sigmoid(bert_embeddings)

        category = data_loader.categories()[data['category']]
        subCategory = data_loader.subcategories()[data['subcategory']]

        print(category)

        # Create news content representation by concatenating BERT, category, subcategory and entities
        cat_embeddings = model.cat_embeddings(0)
        news_embeddings = model.news_embeddings(0)
        sub_cat_embeddings = model.sub_cat_embeddings(subCategory)
        entity_embeddings_1 = model.entity_embeddings(0)
        news_embedding = torch.cat((news_embeddings, bert_embeddings, cat_embeddings, sub_cat_embeddings, entity_embeddings_1), 1)
        news_embedding = model.news_content_transform(news_embedding)
        news_embedding = torch.sigmoid(news_embedding)

        return news_embedding
    
    return createNewsEmbedding

# This will run in the docker container
def main():
    set_random_seed(1)

    # read data
    data_loader = MindData(train_news_file, train_impressions_file, valid_news_file, valid_impressions_file)
    num_users = len(data_loader.users())
    num_news = len(data_loader.news())
    num_categories = len(data_loader.categories())
    num_subcategories = len(data_loader.subcategories())
    num_entities = len(data_loader.entities())

    # read BERT embeddings
    bert_embeddings = read_bert_embeddings(data_loader, train_embeddings_file, valid_embeddings_file)

    # create model
    model = ContentBasedModel(num_users, num_news, num_categories, num_subcategories, num_entities, embedding_size, bert_embeddings)

    # train model
    train_model(model, data_loader)

    torch.save(model.state_dict(), store_file)


if __name__ == "__main__":
    main()
