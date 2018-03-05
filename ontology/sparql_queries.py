# Query to fetch resources with subject as input concept
resource_query = """select distinct ?resource ?resource_label where{{
    ?resource <http://purl.org/dc/terms/subject> <{}>.
    ?resource <http://www.w3.org/1999/02/22-rdf-syntax-ns#type> ?type.
    ?resource <http://www.w3.org/2000/01/rdf-schema#label> ?resource_label
    FILTER((?type = <http://dbpedia.org/ontology/Software> 
            || ?type = <http://dbpedia.org/ontology/Language>
            || ?type = <http://dbpedia.org/ontology/ProgrammingLanguage>
            || ?type = <http://dbpedia.org/class/yago/Algorithm105847438> 
            || ?type = <http://dbpedia.org/class/yago/ProgrammingLanguage106898352>)
            && LANG(?resource_label) = "en")
    }}"""

# Query to fetch sub concepts of input concept
subconcept_query = """PREFIX broader: <http://www.w3.org/2004/02/skos/core#broader>
    select distinct ?sub_concepts ?concept_label where{{
    ?sub_concepts broader: <{}>.
    ?sub_concepts <http://www.w3.org/2000/01/rdf-schema#label> ?concept_label.
    }}
"""

# Query to fetch wiki redirect resources for a base skill
wikireditect_query = """select distinct ?redirect_resource_label  where{{
    ?redirect_resource <http://dbpedia.org/ontology/wikiPageRedirects> <{base_skill}>.
    ?redirect_resource <http://www.w3.org/2000/01/rdf-schema#label> ?label_temp.
    BIND(UCASE(?label_temp) AS ?redirect_resource_label)
    }}"""
