import json
import re


def n4j_dict_format(query):
    s_query = "{{{}}}"
    kv_pairs = ""
    key_val = "{}:'{}'"
    for k,v in query.items():
        try:
            kv_pairs = kv_pairs + "," + key_val.format(k, v)
        except Exception as e:
            pass
    s_query = s_query.format(kv_pairs[1:])
    return s_query


def filter_dict(dic, _filter):
    result = dict()
    for k,v in dic.items():
        if k in _filter:
            result[k] = v
    return result


def merge_skills(driver, skills):
    merge_query = "MERGE (s:Skill {})"

    if not isinstance(skills, list):
        skills = [skills]

    with driver.session() as session:
        with session.begin_transaction() as tx:
            for skill in skills:
                value = n4j_dict_format(skill)
                q = merge_query.format(value)
                result = tx.run(q)
                #print("Merged :", q)


def merge_relationship(driver, parent, children, relationship):
    merge_query = "MATCH (parent:Skill {}), (child:Skill{})" \
              "MERGE  (child)-[:{}]->(parent)"

    if not isinstance(children, list):
        children = [children]

    with driver.session() as session:
        with session.begin_transaction() as tx:
            parent_quey = n4j_dict_format(parent)
            for child in children:
                child_query = n4j_dict_format(child)
                q = merge_query.format(parent_quey, child_query, relationship)
                result = tx.run(q)
                #print("Merged ", q)


def ancestors_by_name(driver, node_type, relationship_type, source_name, include_self=True, limit=5):
    ancestor_query = "MATCH (p:{node_type})<-[:{relationship_type}*..{limit}]-(c:{node_type}) " \
                     "WHERE c.name =~'(?i){source_name}' RETURN p.name as name"
    if not isinstance(limit, int):
        limit = '*'

    ancestor_query = ancestor_query.format(node_type=node_type, relationship_type=relationship_type,
                                           limit=limit, source_name=source_name)

    print(ancestor_query)
    with driver.session() as session:
        with session.begin_transaction() as tx:
            res = tx.run(ancestor_query)
            ancestors = [a['name'] for a in res.records()]
            if include_self:
                ancestors.append(source_name)
    return set(ancestors)

