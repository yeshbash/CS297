import math
import collections
import pandas as pd
import numpy as np
from matplotlib import pyplot as plt
from matplotlib import cm

from skills_ontology import TSO


def _sanchez_distance(ancestors_a, ancestors_b, a=None, b=None, verbose=True):
    a_and_b = ancestors_a & ancestors_b
    a_not_b = ancestors_a - ancestors_b
    b_not_a = ancestors_b - ancestors_a

    dissimilar_features = len(a_not_b) + len(b_not_a)
    total_features = len(a_and_b) + len(b_not_a) + len(a_not_b)

    distance = math.log2(1 + dissimilar_features / total_features)

    if verbose:
        print("Common Features : {}\nOnly in {} : {}\nOnly in {} : {}".format(len(a_and_b), a, len(a_not_b), b,
                                                                              len(b_not_a)))

    return distance


def _rodriguez_similarity(ancestors_a, ancestors_b, skill_a, skill_b, verbose=True):
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
        print("Common Features : {}\nOnly in {} : {}\nOnly in {} : {}"
              .format(len(a_and_b), skill_a, len(a_not_b), skill_b, len(b_not_a)))
        print("Alpha value : {}. Similarity : {}".format(alpha, similarity))
    return similarity


def _reduce_weighted_average(scores, distance_threshold = 1):
    result = dict()
    for skill, skill_scores in scores.items():
        weighted_sum, weight_sum, epsilon = 0, 0, 10**-8,
        filtered = [s for s in skill_scores if skill_scores[s]["distance"] <= distance_threshold]
        for s in filtered:
            weighted_sum += skill_scores[s]["similarity"] * (1-skill_scores[s]["distance"])
            weight_sum += (1-skill_scores[s]["distance"])
            result[skill] = weighted_sum / (weight_sum + epsilon)
    return result


def _reduce_mean(scores):
    if not bool(scores):
        return scores
    sum = 0
    for s in scores:
        sum += scores[s]
    return sum/len(scores)


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


class SkillSimilarity:
    def __init__(self):
        self.tso = TSO()
        self._cache = dict()

    def _check_and_retrieve_ancestors(self, skill_name):
        if skill_name not in self._cache:
            ancestors = self.tso.get_skill_ancestors(skill_name=skill_name, hops=3, include_self=True)
            self._cache[skill_name] = ancestors
        return self._cache[skill_name]

    def _filter_and_resolve_tso_skills(self, skills_coll):
        filtered_skills = list()
        for skill_name in skills_coll:
            skill = self.tso.resolve_skill(skill_name)
            if skill:
                print("Skill retrieved for {} is {}".format(skill_name, skill['uri']))
                filtered_skills.append(skill)
        return filtered_skills

    def pairwise_score(self, skillset_a, skillset_b=None, verbose=False):
        filtered_skillset_a = self._filter_and_resolve_tso_skills(skillset_a)
        if bool(skillset_b):
            filtered_skillset_b = self._filter_and_resolve_tso_skills(skillset_b)
        else:
            filtered_skillset_b = filtered_skillset_a

        if verbose:
            print("{} Job skills not found in ontology : [{}] ".format(len(skillset_a - filtered_skillset_a),
                                                                       ", ".join(skillset_a - filtered_skillset_a)))
            print("{} Resume skills not found in ontology : [{}] ".format(len(skillset_b - filtered_skillset_b),
                                                                          ", ".join(skillset_b - filtered_skillset_b)))

        distance_scores = collections.defaultdict(dict)
        similarity_scores = collections.defaultdict(dict)
        for job_skill in filtered_skillset_b:
            job_skill_ansc = self._check_and_retrieve_ancestors(job_skill['name'])
            for resume_skill in filtered_skillset_a:
                resume_skill_ansc = self._check_and_retrieve_ancestors(resume_skill['name'])
                sdist = _sanchez_distance(job_skill_ansc, resume_skill_ansc, job_skill['name'],
                                               resume_skill['name'], verbose=verbose)
                rsim = _rodriguez_similarity(job_skill_ansc, resume_skill_ansc, job_skill['name'],
                                                  resume_skill['name'], verbose=verbose)
                print("{} and {} . Similarity : {}. Distance : {}".format(job_skill['name'], resume_skill['name'],rsim, sdist))
                distance_scores[job_skill['name']][resume_skill['name']] = sdist
                similarity_scores[job_skill['name']][resume_skill['name']] = rsim
        return distance_scores, similarity_scores

    def job_resume_skill_similarity(self, similarity_scores, distance_scores):
        similarity_scores_npa = similarity_scores.values
        distance_scores_npa = distance_scores
        weighted_average_score = np.sum(similarity_scores_npa * (1-distance_scores_npa), axis=0) / np.sum((1-distance_scores_npa), 1)
        print(weighted_average_score)
        similarity = np.mean(weighted_average_score, axis=0)
        return similarity


if __name__ == "__main__":
    skills = ["Java", "Python", "C", "REST", "SOAP", "HTML", "JavaScript", " nodejs", "artificial_Neural_networks",
               "Hidden Markov Model", "TensorFlow", "scikit-learn", "MongoDB",
               "Hadoop", "Spark", "Kafka", "ElasticSearch", "Kibana", "Spring Framework", "Django",
               "Flask", "Apache_Maven", "Subversion", "GIT", "Eclipse", "Rational_ClearCase"]
    requirements = ["C", "Java", "MYSQL", "Memcached", "Apache_Hadoop", "Apache_Hive", "NoSQL"]

    resume = ["Java script"]
    jd = ["Node JS", "Spring MVC", "Maven", "Hadoop"]
    sim = SkillSimilarity()
    dist_scores, sim_scores = sim.pairwise_score(skills, requirements)
    dist_scores, sim_scores = pd.DataFrame(dist_scores), pd.DataFrame(sim_scores)
    plot_pairwise_scores(dist_scores)
    plot_pairwise_scores(sim_scores)
    #similarity = sim.job_resume_skill_similarity(sim_scores, dist_scores)
    #print(similarity)

