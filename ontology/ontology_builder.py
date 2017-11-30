from SPARQLWrapper import SPARQLWrapper, JSON
from neo4j.v1 import GraphDatabase, basic_auth
import _neo4j.neo4j_client as n4jclient

# SPARQL instance
sparql = SPARQLWrapper("http://dbpedia.org/sparql")
driver = GraphDatabase.driver("bolt://localhost:7687", auth=basic_auth("neo4j", "skillit"))
# Query to fetch resources with subject as input concept
resource_query = """select distinct ?resource ?resource_label where{{
	?resource <http://purl.org/dc/terms/subject> <{}>.
    ?resource <http://www.w3.org/1999/02/22-rdf-syntax-ns#type> ?type.
    ?resource <http://xmlns.com/foaf/0.1/name> ?resource_label
    FILTER(?type = <http://dbpedia.org/ontology/Software> || ?type = <http://dbpedia.org/ontology/Language>)
}}"""

# Query to fetch sub concepts of input concept
subconcept_query = """PREFIX broader: <http://www.w3.org/2004/02/skos/core#broader>
select distinct ?sub_concepts ?concept_label where{{
    ?sub_concepts broader: <{}>.
    ?sub_concepts <http://www.w3.org/2000/01/rdf-schema#label> ?concept_label.
    }}
"""

visited = set()
processed = set()
queue = list()


def clean_label(label):

    if label is None: return None

    # remove paranthesis content
    start = label.find('(')
    end = label.find(')')
    if start != -1 and end != -1:
        result = label[:start]
        if end+1 < len(label):
            result += label[end+1:]
    else:
        result = label


    #Clearning spaces
    result = result.strip()
    result = result.replace(' ', '_')
    #print("before | after : ", label, result)
    return result


def build_ontology():
    while len(queue) > 0:
        skill = queue.pop(0)
        try:
            if skill['uri'] not in processed and skill['uri'] not in visited:
                print("Processing for ", skill['name'])
                visited.add(skill['uri'])

                # Fetching sub concepts
                sparql.setQuery(subconcept_query.format(skill['uri']))
                sparql.setReturnFormat(JSON)
                sub_concepts = sparql.query().convert()

                sub_concept_skills = [
                    {"name": clean_label(r['concept_label']['value']), "uri": r['sub_concepts']['value']} for r in
                    sub_concepts['results']['bindings']]

                # Adding sub-concepts for reccursing
                if len(sub_concept_skills) != 0:
                    queue.extend(sub_concept_skills)
                else:
                    print("not recursing for ", skill['name'])

                # Software Language resources
                sparql.setQuery(resource_query.format(skill['uri']))
                resources = sparql.query().convert()
                resource_skills = [{"name": clean_label(r['resource_label']['value']), "uri": r['resource']['value']}
                                   for r in
                                   resources['results']['bindings']]

                if len(resource_skills) >0:
                    print("Merging parent : ", skill['name'])
                    n4jclient.merge_skills(driver, [skill])
                    n4jclient.merge_skills(driver, resource_skills)
                    n4jclient.merge_relationship(driver, skill, resource_skills, "subclass")



                # #print(sub_concept_skills)
                # n4jclient.merge_skills(driver, [skill])
                # n4jclient.merge_skills(driver, sub_concept_skills)
                # n4jclient.merge_relationship(driver, skill, sub_concept_skills, "subclass")


                processed.add(skill['uri'])
            else:
                print("Skill already visited")
        except Exception as e:
            print("Failed for skill:" + skill['name'])
            print("Failure : " + str(e))

#parent_skill = {"name": "Object-oriented programming languages", "uri": "http://dbpedia.org/resource/Category:Object-oriented_programming_languages"}
#parent_skill = {"name": "Machine Learning", "uri": "http://dbpedia.org/resource/Category:Machine_learning"}
parent_skill = {"name": "Web Development", "uri": "http://dbpedia.org/resource/Category:Web_development"}

queue.append(parent_skill)
build_ontology()

