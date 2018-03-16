""" Interface to the custom technical skills ontology """
from _neo4j.neo4j_client import Neo4jClient
import common_utils as utils
from config import *


class TSO:
    def __init__(self):
        self.neo4j = Neo4jClient()

    def merge_skills(self, skills):
        self.neo4j.merge_nodes(node_type=SKILL_NODE_LABEL, node_props=skills)

    def merge_aliases(self, aliases):
        self.neo4j.merge_nodes(node_type=ALIAS_NODE_LABEL, node_props=aliases)

    def merge_subclass_skills(self, base_skill, sub_skills, merge_parent=False):
        if merge_parent:
            self.merge_skills(base_skill)
        self.merge_skills(sub_skills)
        self.neo4j.merge_relationship(parent_type=SKILL_NODE_LABEL, parent_query=base_skill,
                                      child_type=SKILL_NODE_LABEL, children_query=sub_skills,
                                      relationship=SUBCLASS_REL_LABEL)

    def merge_skill_aliases(self, base_skill, aliases, merge_parent=False):
        if merge_parent:
            self.merge_skills(base_skill)
        self.merge_aliases(aliases)
        self.neo4j.merge_relationship(parent_type=SKILL_NODE_LABEL, parent_query=base_skill,
                                      child_type=ALIAS_NODE_LABEL, children_query=aliases,
                                      relationship=ALIAS_REL_LABEL)

    def find_skill_by_name(self, skill_name):
        skills = self.neo4j.match_by_property(node_type=SKILL_NODE_LABEL, property_name=SKILL_PROP_NAME, property_val=skill_name, case_sensitive=True)
        result = None
        for skill in skills:
            result = {
                     "name": skill["name"],
                     "type": skill["type"],
                     "uri": skill["uri"]
            }
            break
        return result

    def find_skill_by_alias(self, alias_name):
        skills = self.neo4j.match_parent_by_property(node_type=ALIAS_NODE_LABEL, parent_type=SKILL_NODE_LABEL,
                                                     property_name=ALIAS_PROP_NAME, property_val=alias_name,
                                                     rel_type=ALIAS_REL_LABEL, case_sensitive=True)
        result = None
        for skill in skills:
            result = {
                    "name": skill["name"],
                    "type": skill["type"],
                    "uri": skill["uri"]
                }
            break
        return result

    def get_skill_ancestors(self, skill_name, hops, include_self):
        ancestors = self.neo4j.ancestors_by_property(node_type=SKILL_NODE_LABEL, relationship_type=SUBCLASS_REL_LABEL,
                                                     property_name=SKILL_PROP_NAME, property_val=skill_name, hops=hops)
        result = set()
        for ancestor in ancestors:
            result.add(ancestor['name'])
        if include_self:
            result.add(skill_name)

        return result

    def resolve_skill(self, skill_name):
        skill_name = utils.clean_skill_label(skill_name)
        skill = self.find_skill_by_name(skill_name)
        if skill is None:
            skill = self.find_skill_by_alias(skill_name)
        return skill


if __name__ == '__main__':
    TSO().find_skill_by_name("Computer programming")


