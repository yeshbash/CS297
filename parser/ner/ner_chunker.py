from collections import Iterable
from nltk.tag import ClassifierBasedTagger
from nltk.chunk import ChunkParserI


class NamedEntityChunker(ChunkParserI):
    def __init__(self, train_sents, feature_fn, **kwargs):
        assert isinstance(train_sents, Iterable)

        self.feature_detector = feature_fn
        self.tagger = ClassifierBasedTagger(
            train=train_sents,
            feature_detector=feature_fn,
            **kwargs)

    def parse(self, tagged_sent):
        chunks = self.tagger.tag(tagged_sent)

        # Transform the result from [((w1, t1), iob1), ...]
        # to the preferred list of triplets format [(w1, t1, iob1), ...]
        iob_triplets = [(w, t, c) for ((w, t), c) in chunks]

        # Transform the list of triplets to nltk.Tree format
        return iob_triplets