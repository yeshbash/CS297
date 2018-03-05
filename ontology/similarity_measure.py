import math
import collections

from neo4j.v1 import GraphDatabase, basic_auth
import json

from _neo4j import neo4j_client
import common_utils as utils


def sanchez_distance(a, b, ancestors_a, ancestors_b, verbose=True):
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


def rodriguez_similarity(skill_a, skill_b, ancestors_a, ancestors_b, verbose=True):
    a_and_b = ancestors_a & ancestors_b
    a_not_b = ancestors_a - ancestors_b
    b_not_a = ancestors_b - ancestors_a

    # weight factor
    epsilon = 10**-8
    alpha = len(a_not_b) / (len(a_not_b) + len(b_not_a) + epsilon)
    if len(a_not_b) > len(b_not_a):
       alpha = 1 - alpha

    similarity = math.log2(1 + len(a_and_b) / (alpha * len(a_not_b) + (1 - alpha) * len(b_not_a) + len(a_and_b)))
    if verbose:
        print("Common Features : {}\nOnly in {} : {}\nOnly in {} : {}"
              .format(len(a_and_b), skill_a, len(a_not_b), skill_b, len(b_not_a)))
        print("Alpha value : {}. Similarity : {}".format(alpha, similarity))
    return similarity


def calculate_scores(skills, requirements):
    cache = dict()
    scores = collections.defaultdict(dict)
    driver = GraphDatabase.driver("bolt://localhost:7687", auth=basic_auth("neo4j", "skillit"))
    for r in requirements:
        if r in cache: ancestors_r = cache[r]
        else:
            ancestors_r = neo4j_client.ancestors_by_name(driver=driver, source_name=r, node_type="Skill",
                                                         relationship_type="subclass", limit=3)
            cache[r] = ancestors_r
        for s in skills:
            if s in cache: ancestors_s = cache[s]
            else:
                ancestors_s = neo4j_client.ancestors_by_name(driver=driver, source_name=s, node_type="Skill",
                                                             relationship_type="subclass", limit=3)
                cache[s] = ancestors_s

            print("Processing for {} - {}".format(r,s))
            sdist = sanchez_distance(r, s, ancestors_r, ancestors_s, verbose=False)
            rsim = rodriguez_similarity(r, s, ancestors_r, ancestors_s, verbose=False)
            print("Similarity : {}. Distance : {}".format(rsim,sdist))
            scores[r][s] = {"distance": sdist, "similarity": rsim}
    return scores


def calculate_average(r, score):
    sum = 0
    weighted_sum = 0
    weight_sum = 0
    result = dict()
    filtered = [s for s in score if score[s]["distance"]!=1]
    for s in filtered:
        sum += score[s]["similarity"]
        weighted_sum += score[s]["similarity"] * (1-score[s]["distance"])
        weight_sum += (1-score[s]["distance"])

    if len(filtered) != 0:
        result["avg"] = sum / len(filtered)
        result["weighted_avg"] = weighted_sum / weight_sum
        print("Avergae score for {} : {}".format(r, result["avg"]))
        print("Weighted avergae score for {} : {}".format(r, result["weighted_avg"]))
    else:
        result = None

    return result


def resolve_skill(skill_name, tso):
    # Step 1 : clean skill name
    # Step 2 : lookup direct match for resources or categories
    # Step 3: Check if direct match exists
        # Step 3.1: return skill object
        # Step 3.2 : lookup aliases matching skill name
            # Step 3.2.1 If alias found, return the parent skill
    # Step : raise NoMatchFoundException
    if skill_name is None: return None
    cleaned_skill_name = utils.clean_skill_label(skill_name)


    pass


if __name__ == "__main__":
    skills = ["Java", "Python", "C", "REST", "SOAP", "HTML", "JavaScript", " node.js", "artificial_Neural_networks",
              "hidden_markov_models", "TensorFlow", "scikit-learn", "Oracle_Database", "MySQL", "MongoDB",
              "Apache_Hadoop", "Apache_Spark", "Apache_Kafka", "ElasticSearch", "Kibana", "Spring_Frameworks", "Django",
              "Flask", "Apache_Maven", "Subversion", "GIT", "Eclipse", "Rational_ClearCase"]
    requirements = ["C++", "Java", "C# ", "MYSQL", "Memcached", "Apache_Hadoop", "Apache_Hive", "NoSQL"]

    scores = calculate_scores(skills, requirements)
    average_score = dict()

    for r in scores:
        average = calculate_average(r, scores[r])
        if average is not None: average_score[r] = average

    print(json.dumps(scores))
    print(json.dumps(average_score))
