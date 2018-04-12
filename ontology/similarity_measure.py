import math
import collections
import pandas as pd
from matplotlib import pyplot as plt
from matplotlib import cm

from skills_ontology import TSO


def plot_pairwise_scores(scores):
    df = pd.DataFrame(scores)
    fig = plt.figure()
    fig.set_figheight(15)
    fig.set_figwidth(15)
    ax1 = fig.add_subplot(111)
    cmap = cm.get_cmap('YlOrRd', 30)
    cax = ax1.imshow(df, interpolation='nearest', cmap=cmap)
    ax1.set_xticks(range(df.shape[0]))
    ax1.set_yticks(range(df.shape[1]))
    ax1.set_xticklabels(df.columns.values, fontsize=16, rotation='vertical')
    ax1.set_yticklabels(df.columns.values, fontsize=16)
    ax1.grid(True)
    fig.colorbar(cax, ticks=[.2, .4, .6, .8, 1])
    plt.show()


class TSOSkillSimilarity:
    def __init__(self):
        self.tso = TSO()
        self._ancestors_cache = dict()
        self._alias_cache = dict()

    def _resolve_cache(self, resource_type):
        if resource_type == "ancestors":
            cache = self._ancestors_cache
        elif resource_type == "alias":
            cache = self._alias_cache
        else:
            raise Exception("Invalid cache type")

        return cache

    def _cache_get(self, resource_key, resource_type):
        cache = self._resolve_cache(resource_type)
        resource = cache[resource_key] if resource_key in cache else None
        return resource

    def _cache_put(self, resource_key, resource, resource_type):
        cache = self._resolve_cache(resource_type)
        cache[resource_key] = resource
        return cache[resource_key]

    def _check_and_retrieve_ancestors(self, resource_name):
        resource = self._cache_get(resource_name, resource_type="ancestors")
        if not resource:
            ancestors = self.tso.get_skill_ancestors(skill_name=resource_name, hops=2, include_self=True)
            return self._cache_put(resource_name, resource_type="ancestors", resource=ancestors)
        return resource

    def _check_and_retrieve_aliases(self, resource_name):
        resource = self._cache_get(resource_name, resource_type="alias")
        if not resource:
            alias = self.tso.resolve_skill(skill_name=resource_name)
            return self._cache_put(resource_name, resource_type="alias", resource=alias)
        return resource

    def _filter_and_resolve_tso_skills(self, skills_coll):
        filtered_skills = list()
        for skill_name in skills_coll:
            skill = self._check_and_retrieve_aliases(skill_name)
            if skill:
                filtered_skills.append(skill)
        return filtered_skills

    def _sanchez_similarity(self, skill_a, skill_b, verbose=True):
        ancestors_a = self._check_and_retrieve_ancestors(skill_a)
        ancestors_b = self._check_and_retrieve_ancestors(skill_b)

        a_and_b = ancestors_a & ancestors_b
        a_not_b = ancestors_a - ancestors_b
        b_not_a = ancestors_b - ancestors_a

        dissimilar_features = len(a_not_b) + len(b_not_a)
        total_features = len(a_and_b) + len(b_not_a) + len(a_not_b)

        distance = math.log2(1 + dissimilar_features / total_features)

        if verbose:
            print("Common Features for {} and {} : {}".format(skill_a, skill_b, a_and_b))

        return 1 - distance

    def _rodriguez_similarity(self, skill_a, skill_b, verbose=True):
        ancestors_a = self._check_and_retrieve_ancestors(skill_a)
        ancestors_b = self._check_and_retrieve_ancestors(skill_b)

        a_and_b = ancestors_a & ancestors_b
        a_not_b = ancestors_a - ancestors_b
        b_not_a = ancestors_b - ancestors_a

        # weight factor
        epsilon = 10 ** -8
        alpha = len(a_not_b) / (len(a_not_b) + len(b_not_a) + epsilon)
        if len(a_not_b) > len(b_not_a):
            alpha = 1 - alpha

        similarity = math.log2(1 + len(a_and_b) / (alpha * len(a_not_b) + (1 - alpha) * len(b_not_a) + len(a_and_b)))
        if verbose:
            print("Common Features for {} and {} : {}".format(skill_a, skill_b, a_and_b))
            print("Alpha value : {}. Similarity : {}".format(alpha, similarity))
        return similarity

    def pairwise_score(self, skill_set_a, skill_set_b=None, measure='sanchez', verbose=False):

        filtered_skills_a = self._filter_and_resolve_tso_skills(skill_set_a)
        filtered_skills_b = self._filter_and_resolve_tso_skills(skill_set_b)

        scores = collections.defaultdict(dict)
        sim = self._rodriguez_similarity if measure == 'rodriguez' else self._sanchez_similarity

        for a_skill in filtered_skills_a:
            for b_skill in filtered_skills_b:
                sim_score = sim(a_skill['name'], b_skill['name'])
                scores[a_skill['name']][b_skill['name']] = sim_score
        return scores
