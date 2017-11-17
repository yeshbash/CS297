import nltk
import utils
import random
import math

def default_feature(word):
    features = dict()
    if word is not None and word!= "":
        features['first_letter'] = word[0]
        features['wc'] = len(word.split(" "))
        features['char_len'] = len(word)
    return features


class DegreeClassifier:
    def __init__(self, features_detector=default_feature):
        self.model = None
        self.features_detector = features_detector
        self.accuracy = 0

    def train(self, train_data, train_split=0.85):
        # Splitting training and testing
        random.shuffle(train_data)
        split_len = math.floor(len(train_data)*train_split)
        train_split, test_split = train_data[:split_len], train_data[split_len:]

        feature_set = [(self.features_detector(data), label) for (data,label) in train_split]
        self.model = nltk.NaiveBayesClassifier.train(feature_set)
        self.accuracy = nltk.classify.accuracy(self.model,[(self.features_detector(data), label) for (data,label) in test_split])

        return self

    def classify(self, test_data):
        if self.model is not None:
            feature_data = [(self.features_detector(t[0])) for t in test_data]
            return self.model.classify_many(feature_data)
        return

# if __name__ == '__main__':
#     degree_labelled = utils.load_object("D:\SJSU\Fall17\CS297\Impl`\parser\degree_labelled")
#     random.shuffle(degree_labelled)
#     model = DegreeClassifier()
#     classification = model.train(degree_labelled[:50]).classify(degree_labelled[50:])
#     print(model.accuracy)
#     for actual, c in zip(degree_labelled[50:], classification):
#         print(actual[0] + " ---" + c)
#
#     utils.save_object(model, "D:\SJSU\Fall17\CS297\Impl`\parser\degree_classifier_model")
