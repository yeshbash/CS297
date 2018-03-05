import os
from multiprocessing import Process, Pipe

from config import *
import dbpedia
from skills_ontology import TSO


def process_info():
    info_text = "{module_name}-{process_id}"
    return info_text.format(module_name=__name__, process_id=os.getpid())


def alias_processor(conn):
    process_str = process_info()
    tso = TSO()
    while conn.poll(PIPE_POOL_TIMEOUT):
        # Step 4: Fetching resource aliases and merging to ontology
        try:
            resource_skills = conn.recv()
            for resource in resource_skills:
                resource_aliases = dbpedia.get_aliases(resource)
                tso.merge_skill_aliases(base_skill=resource, aliases=resource_aliases)
                print("[{}] | {} aliases found for {}".format(process_str, len(resource_aliases), resource['name']))
        except Exception as e:
            print(process_str + str(e))
    print(process_str + " exiting")


def build_ontology(queue, tso):
    """
    Build the skills ontology by crawling from the base set of Concept skills
    Defers the addition of a concept skill to ensure it has at least one resource associated
    Maintains the parent reference to achieve deferred merge
    :return:
    """
    process_str = process_info()
    resource_processor_conn, alias_processor_conn = Pipe()
    p_alias_processors = Process(target=alias_processor, args=(alias_processor_conn,))
    p_alias_processors.start()

    visited = set()
    processed = set()

    while len(queue) > 0:
        print("Queue Len :", len(queue))
        skill, parent = queue.pop(0).values()
        try:
            if skill['uri'] not in processed and skill['uri'] not in visited:
                print("[{}] | Processing for {}".format(process_str, skill['name']))
                visited.add(skill['uri'])

                resource_skills = dbpedia.get_resources(skill)
                if len(resource_skills) > 0:
                    # Step 1:  Merge current skill to TSO ontology.
                    # If parent exist, merge parent and its relationship too
                    if parent is not None:
                        tso.merge_subclass_skills(base_skill=parent, sub_skills=skill, merge_parent=True)
                        print("[{}] | {} and {} relationship merged".format(process_str, parent["name"], skill["name"]))
                    else:
                        tso.merge_skills(skill)

                    # Step 2 : Merge resource skills and relationship with current skill
                    tso.merge_subclass_skills(base_skill=skill, sub_skills=resource_skills)
                    print("[{}] | [RESOURCES] : {} resources found for {}. Merging into ontology".format(process_str,len(resource_skills), skill["name"]))

                    # Step 3: Pass request to resource alias process
                    resource_processor_conn.send(resource_skills)

                    # Step 4 Fetch Sub-concepts for skill
                    sub_concept_skills = dbpedia.get_sub_concepts(skill)
                    if len(sub_concept_skills) != 0:
                        print('[CATEGORIES] : {} sub-concepts found for {}. Adding for processing.'
                              .format(len(sub_concept_skills), skill['name']))
                        queue.extend(sub_concept_skills)
                    else:
                        print("[CATEGORIES] : No sub-concepts found for {}. Not adding for processing".format(skill['name']))
                else:
                    print("No technical resources found for {}. Not pursuing.".format(skill['name']))
                processed.add(skill['uri'])
            else:
                print(skill['name'] + "Skill already visited")
        except Exception as e:
            print("Failed for skill:" + skill['name'])
            print("Failure : " + str(e))

    print("[{}] | Waiting for alias process to complete".format(process_str))
    p_alias_processors.join()
    print(process_str + " exiting")


if __name__ == "__main__":
    queue = list()
    parent_skill = {
                    "skill": {
                            "name": "Big_data",
                            "uri": "http://dbpedia.org/resource/Category:Big_data",
                            "type": CATEGORY_TYPE
                        },
                    "parent": None
                }

    queue.append(parent_skill)
    build_ontology(queue, TSO())

