import nltk
from nltk.tokenize import RegexpTokenizer
import pickle
import string
from nltk.stem.snowball import SnowballStemmer
from ner.ner_chunker import NamedEntityChunker
import utils
import collections
from classifiers.degree_classifier import *

ne_map = {
    "0": "O",
    "1": "DEGREE",
    "2": "MAJOR",
    "3": "UNIVERSITY",
    "4": "SCHOOL",
    "5": "TIMESTART",
    "6": "TIMEEND",
}

def ner_features(tokens, index, history):
    """
    `tokens`  = a POS-tagged sentence [(w1, t1), ...]
    `index`   = the index of the token we want to extract features for
    `history` = the previous predicted IOB tags
    """

    # init the stemmer
    stemmer = SnowballStemmer('english')
    #print tokens

    # Pad the sequence with placeholders
    tokens = [('[START2]', '[START2]'), ('[START1]', '[START1]')] + list(tokens) + [('[END1]', '[END1]'),
                                                                                    ('[END2]', '[END2]')]
    history = ['[START2]', '[START1]'] + list(history)

    # shift the index with 2, to accommodate the padding
    index += 2

    word, pos = tokens[index]
    prevword, prevpos = tokens[index - 1]
    prevprevword, prevprevpos = tokens[index - 2]
    nextword, nextpos = tokens[index + 1]
    nextnextword, nextnextpos = tokens[index + 2]
    previob = history[index - 1]
    contains_dash = '-' in word
    contains_dot = '.' in word
    allascii = all([True for c in word if c in string.ascii_lowercase])

    allcaps = word == word.capitalize()
    capitalized = word[0] in string.ascii_uppercase

    prevallcaps = prevword == prevword.capitalize()
    prevcapitalized = prevword[0] in string.ascii_uppercase

    nextallcaps = prevword == prevword.capitalize()
    nextcapitalized = prevword[0] in string.ascii_uppercase

    return {
        'word': word,
        'lemma': stemmer.stem(word),
        'pos': pos,
        'all-ascii': allascii,
        'all-num': word.isdigit(),

        'next-word': nextword,
        'next-lemma': stemmer.stem(nextword),
        'next-pos': nextpos,

        'next-next-word': nextnextword,
        'nextnextpos': nextnextpos,


        'prev-word': prevword,
        'prev-lemma': stemmer.stem(prevword),
        'prev-pos': prevpos,
        'prev-pos-num': prevword.isdigit(),

        'prev-prev-word': prevprevword,
        'prev-prev-pos': prevprevpos,

        'prev-iob': previob,

        'contains-dash': contains_dash,
        'contains-dot': contains_dot,

        'all-caps': allcaps,
        'capitalized': capitalized,

        'prev-all-caps': prevallcaps,
        'prev-capitalized': prevcapitalized,

        'next-all-caps': nextallcaps,
        'next-capitalized': nextcapitalized,
    }


def load_data(source):
    with open(source, "rb") as f:
        labelled_sentences = pickle.load(f)

    formatted_data = list()
    for l in labelled_sentences:
        formatted_data.append([((i[0], i[1]), i[2]) for i in l])

    return formatted_data


def build_chunker(data):
    chunker = NamedEntityChunker(data, feature_fn=ner_features)
    return chunker


def group_iob_tags(iob_tagged):
    result = collections.defaultdict(str)
    for data, pos, ne in iob_tagged:
        if "-" in  ne: ne = ne.split("-")[1]
        result[ne] += data+ " "
    return result

test_sentences = ["M.S in Psychology Engineering, Arizona State University 08/2017 - 05/2019",
                  "B.E in Computer Science, Anna University 08/2012 - 04/2016",
                  "Master of Science (MS). in Chemical Engineering, San Jose State University.Aug 16 - May 18",
                  "Masters in Computer Science Arizona State University, Tempe. Jan 2014 - Dec 2015",
                  "Bachelors in Computer Science Anna University, India. Sep 2009 - May 2013"]


if __name__ == "__main__":
    tokenizer = RegexpTokenizer(r'\w+')
    # train_data = load_data("D:\SJSU\Fall17\CS297\Impl`\parser\iob_tagged.txt")
    # chunker = build_chunker(train_data)
    # utils.save_object(chunker, "D:\SJSU\Fall17\CS297\Impl`\parser\\ner_chunker")

    """
    #score = chunker.evaluate([conlltags2tree([(w, t, iob) for (w, t), iob in iobs]) for iobs in train_data[30:]])
    scoring = collections.defaultdict(int)
    scoring_total = collections.defaultdict(int)
    true, total = 0, 0

    for t in train_data[:15]:
        original_str = " ".join([x[0][0] for x in t])
        print original_str
        parse_result = chunker.parse(nltk.pos_tag(tokenizer.tokenize(original_str)))
        total += len(parse_result)
        for r in zip(parse_result,t):
            scoring_total[r[0][2]] += 1
            if r[0][2] == r[1][1]:
                scoring[r[0][2]] +=1
                true+=1

    print "Overall accuracy : " + str(true/(total*1.0))
    print "Tag-wise accuracy"
    for k in scoring:
        print "Accuracy of " + k + " : " + str(scoring[k]/(scoring_total[k]*1.0))
    """
    chunker = utils.load_object("D:\SJSU\Fall17\CS297\Impl`\parser\\ner_chunker")
    degree_labelled = list()
    degree_classifier = utils.load_object("D:\SJSU\Fall17\CS297\Impl`\parser\degree_classifier_model")

    with open("D:\SJSU\Fall17\CS297\Impl`\parser\education_data.txt", "r") as d:
        for line in d:
            print(line)
            pos_tagged = nltk.pos_tag(tokenizer.tokenize(line))
            entities = group_iob_tags(chunker.parse(pos_tagged))
            print("Degree : {}. Major: {}".format(entities['DEGREE'], entities['MAJOR']))
            print("Degree type :" + degree_classifier.classify([entities['DEGREE']])[0])
            #label = str(input("Label for : " + entities['DEGREE']))
            #degree_labelled.append((entities['DEGREE'], label))
    #utils.save_object(degree_labelled, "degree_labelled")
