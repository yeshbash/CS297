import csv
import collections
import math
import json
from elasticsearch import Elasticsearch
from elasticsearch_dsl import Search, Q

muti_match_query = """{\"query\" : {\"bool\":{\"must\": [{{multi_match}}]}]}}"""

match_query = """{\"query\" : {{{match}}}}"""

match_format = """{\"match\":{{{key}}:{{value}}}}}"""


def process_and_index_job_data(file_path, es, contains_header=True):
    with open(file_path, "r", encoding='utf-8') as fp:
        data_file = csv.reader(fp)
        for line in data_file:
            try:
                if contains_header:
                    # Ignore header line
                    contains_header = False
                jobContent = dict()
                jobContent['id'] = line[11].strip()
                jobContent['description'] = line[3].strip()
                jobContent['skills'] = line[10].strip()
                try:
                    es_resp = es.index(index='job', doc_type='jobContent', id=jobContent['id'], body=jobContent)
                    if not es_resp['result'] in ['created', 'updated']:
                        print("[Error] Indexing failed for :" + jobContent['id'])
                except Exception as e:
                    print("[Error] Indexing failed for : {}. Reason : {}".format(jobContent['id'], str(e)))
            except Exception as e:
                print("Exception while processing {} - {}. Continuing".format(line, str(e)))


def _multi_match_query(predicate_key, predicate_values):
    match = ""
    for i, v in enumerate(predicate_values):
        if i: match += ","
        match += match_format.format(key=predicate_key, value=v)
    query = muti_match_query.format(multi_match=match)
    print(query)
    return query


def count_jobs_by_skill(values, es):
    search = Search(using=es, index='job', doc_type='jobContent')
    search_query = Q("match", description=values)
    if isinstance(values, list):
        search_query = Q('bool', must=[Q('match', description=x) for x in values])

    return search.query(search_query).count()

def pmi(skill_a, skill_b, n, es):
    count_a = count_jobs_by_skill(skill_a, es)
    count_b = count_jobs_by_skill(skill_b, es)
    count_a_b = count_jobs_by_skill([skill_b, skill_a], es)

    p_a = count_a/n
    p_b = count_b/n
    p_a_b = count_a_b/n

    return math.log(p_a_b/(p_a*p_b))


def paiwise_pmi(skills):
    es = Elasticsearch()
    pmi_scores = collections.defaultdict(dict)
    for s1 in skills:
        for s2 in skills:
            if s1 not in pmi_scores or s2 not in pmi_scores[s1]:
                score = pmi(s1, s2, 22004, es)
                pmi_scores[s1][s2] = pmi_scores[s2][s1] = score

    return pmi_scores


if __name__== '__main__':
    scores = paiwise_pmi(["java","c++","C#","CSS","PHP","Bash","Javascript","Python","Ruby","SQL"])
    print(scores)
    with open('C:\Data\SJSU\Fall17\CS297\CS297\ontology\\results\pmi_result.json','w') as f:
        f.write(json.dumps(scores))