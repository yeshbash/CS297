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
    FILTER(?type = <http://dbpedia.org/ontology/Software> 
    || ?type = <http://dbpedia.org/ontology/Language>
    || ?type = <http://dbpedia.org/ontology/ProgrammingLanguage>)
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


def get_sub_concepts(skill):
    sub_concept_skills = []

    sparql.setQuery(subconcept_query.format(skill['uri']))
    sparql.setReturnFormat(JSON)
    sub_concepts = sparql.query().convert()

    for r in sub_concepts['results']['bindings']:
        sub_concept_skills.append({
            "skill": {
                "name": clean_label(r['concept_label']['value']),
                "uri": r['sub_concepts']['value'],
                "type": "category"
            },
            "parent": skill
        })

    return sub_concept_skills


def get_resources(skill):
    resource_skills = list()
    sparql.setQuery(resource_query.format(skill['uri']))
    sparql.setReturnFormat(JSON)
    resources = sparql.query().convert()
    for r in resources['results']['bindings']:
        resource_skills.append({
                                "name": clean_label(r['resource_label']['value']),
                                "uri": r['resource']['value'],
                                "type": "resource"
                            })
    return resource_skills


def build_ontology():
    while len(queue) > 0:
        print("Queue Len :", len(queue))
        skill, parent = queue.pop(0).values()
        try:
            if skill['uri'] not in processed and skill['uri'] not in visited:
                print("Processing for ", skill['name'])
                visited.add(skill['uri'])

                # Software/Language resources for skill
                resource_skills = get_resources(skill)
                if len(resource_skills) > 0:
                    # Step 1 : Merge current skill
                    n4jclient.merge_skills(driver, skill)

                    # Step 2 : Merge relationship between current skill and parent
                    if parent is not None:
                        n4jclient.merge_skills(driver, parent)
                        n4jclient.merge_relationship(driver, parent, [skill], "subclass")
                        print("{} and {} relationship merged".format(parent["name"], skill["name"]))

                    # Step 3 : Merge resource skills and relationship with current skill

                    print("[RESOURCES] : {} resources found for {}. Merging into ontology".format(len(resource_skills),
                                                                                                  skill['name']))
                    n4jclient.merge_skills(driver, resource_skills)
                    n4jclient.merge_relationship(driver, skill, resource_skills, "subclass")

                    # Step 4 Fetch Sub-concepts for skill
                    sub_concept_skills = get_sub_concepts(skill)
                    if len(sub_concept_skills) != 0:
                        print("[CATEGORIES] : {} sub-concepts found for {}. Adding for recursion.".format(len(sub_concept_skills), skill['name']))
                        queue.extend(sub_concept_skills)
                    else:
                        print("[CATEGORIES] : No sub-concepts found for {}. Not recursing".format(skill['name']))
                else:
                    print("No technical resources found for {}. Not pursuing.".format(skill['name']))
                processed.add(skill['uri'])
            else:
                print("Skill already visited")
        except Exception as e:
            print("Failed for skill:" + skill['name'])
            print("Failure : " + str(e))

#parent_skill = {"name": "Object-oriented programming languages", "uri": "http://dbpedia.org/resource/Category:Object-oriented_programming_languages"}
#parent_skill = {"name": "Machine Learning", "uri": "http://dbpedia.org/resource/Category:Machine_learning"}
parent_skill = {"skill" : {"name": "Computer Programming", "uri": "http://dbpedia.org/resource/Category:Computer_programming", "type":"category"}, "parent" : None}

queue.append(parent_skill)
build_ontology()

