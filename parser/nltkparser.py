import nltk
from nltk.tokenize import RegexpTokenizer
import pickle
import string
from nltk.stem.snowball import SnowballStemmer
from ner.ner_chunker import NamedEntityChunker


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


def build_chunker(data, model_destination):
    chunker = NamedEntityChunker(data, feature_detector=ner_features)
    with open(model_destination,"wb") as f:
        pickle.dump(chunker,f)
        print("model saved to "+model_destination)
    return chunker


def load_chunker(model_location):
    with open(model_location,"rb") as f:
        chunker = pickle.load(f)
        print("model loaded from "+model_location)
    return chunker


ne_map = {
    "0": "O",
    "1": "DEGREE",
    "2": "MAJOR",
    "3": "UNIVERSITY",
    "4": "SCHOOL",
    "5": "TIMESTART",
    "6": "TIMEEND",

}

test_sentences = ["M.S in Psychology Engineering, Arizona State University 08/2017 - 05/2019",
                  "B.E in Computer Science, Anna University 08/2012 - 04/2016",
                  "Master of Science (MS). in Chemical Engineering, San Jose State University.Aug 16 - May 18",
                  "Masters in Computer Science Arizona State University, Tempe. Jan 2014 - Dec 2015",
                  "Bachelors in Computer Science Anna University, India. Sep 2009 - May 2013"]


if __name__ == "__main__":
    tokenizer = RegexpTokenizer(r'\w+')
    train_data = load_data("D:\SJSU\Fall17\CS297\Impl`\parser\iob_tagged.txt")
    #chunker = build_chunker(train_data[15:], "D:\SJSU\Fall17\CS297\Impl`\parser\\ner_chunker")

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
    chunker = load_chunker("D:\SJSU\Fall17\CS297\Impl`\parser\\ner_chunker")

    for t in test_sentences:
        tagged = chunker.parse(nltk.pos_tag(tokenizer.tokenize(t)))
        degree, major = "",""
        for tag in tagged:
            if "DEGREE" in tag[2]:
                degree += tag[0] + " "
            elif "MAJOR" in tag[2]:
                major += tag[0] + " "
        print("Major : {}. Degree : {}".format(major, degree))
