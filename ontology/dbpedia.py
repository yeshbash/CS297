from urllib import parse

from sparql_queries import *
import common_utils as utils
from config import *

from SPARQLWrapper import SPARQLWrapper, JSON

sparql = SPARQLWrapper("http://dbpedia.org/sparql")


def get_sub_concepts(skill):
    sub_concept_skills = []
    sparql.setQuery(subconcept_query.format(parse.unquote(skill['uri'])))
    sparql.setReturnFormat(JSON)
    sub_concepts = sparql.query().convert()

    for r in sub_concepts['results']['bindings']:
        sub_concept_skills.append({
            "skill": {
                "name": utils.clean_skill_label(r['concept_label']['value']),
                "uri": parse.quote(r['sub_concepts']['value']),
                "type": CATEGORY_TYPE
            },
            "parent": skill
        })

    return sub_concept_skills


def get_resources(skill):
    resource_skills = list()
    sparql.setQuery(resource_query.format(parse.unquote(skill['uri'])))
    sparql.setReturnFormat(JSON)
    resources = sparql.query().convert()
    for r in resources['results']['bindings']:
        resource_skills.append({
                                "name": utils.clean_skill_label(r['resource_label']['value']),
                                "uri": parse.quote(r['resource']['value']),
                                "type": RESOURCE_TYPE
                            })
    return resource_skills


def get_aliases(skill):
    aliases = list()
    sparql.setQuery(wikireditect_query.format(base_skill=parse.unquote(skill['uri'])))
    sparql.setReturnFormat(JSON)
    redirects = sparql.query().convert()
    for r in redirects['results']['bindings']:
        aliases.append({
            "name": utils.clean_skill_label(r['redirect_resource_label']['value'])
        })
    return aliases
