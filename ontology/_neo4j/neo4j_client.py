from neo4j.v1 import GraphDatabase, basic_auth

import _neo4j.utils as neo4j_utils


class Neo4jClient:
    def __init__(self):
        self.driver = GraphDatabase.driver("bolt://localhost:7687", auth=basic_auth("neo4j", "skillit"))

    def merge_nodes(self, node_type, node_props):
        merge_query = "MERGE (s:{node_type} {node_prop})"

        if not isinstance(node_props, list):
            node_props = [node_props]

        with self.driver.session() as session:
            with session.begin_transaction() as tx:
                for prop in node_props:
                    prop_value = neo4j_utils.n4j_dict_format(prop)
                    q = merge_query.format(node_type=node_type, node_prop=prop_value)
                    _ = tx.run(q)
                    #print("Merged :", q)

    def merge_relationship(self, parent_type, parent_query, child_type, children_query, relationship):
        merge_query = "MATCH (parent:{parent_type} {parent_query}), (child:{child_type}{child_query})" \
                      "MERGE  (child)-[:{rel_type}]->(parent)"

        if not isinstance(children_query, list):
            children_query = [children_query]

        with self.driver.session() as session:
            with session.begin_transaction() as tx:
                parent_query = neo4j_utils.n4j_dict_format(parent_query)
                for child in children_query:
                    child_query = neo4j_utils.n4j_dict_format(child)
                    q = merge_query.format(parent_type=parent_type, parent_query=parent_query,
                                           child_type=child_type, child_query=child_query, rel_type=relationship)
                    _ = tx.run(q)

    def ancestors_by_property(self, node_type, relationship_type, property_name, property_val, hops=5):

        ancestor_query = "MATCH (p:{node_type})<-[:{relationship_type}*..{hops}]-(c:{node_type}) " \
                         "WHERE c.{property_name} =~'(?i){property_val}' RETURN p.{property_name} as name"

        if not isinstance(hops, int):
            hops = '*'

        ancestor_query = ancestor_query.format(node_type=node_type, relationship_type=relationship_type,
                                               hops=hops, property_name=property_name, property_val=property_val)

        with self.driver.session() as session:
            with session.begin_transaction() as tx:
                res = tx.run(ancestor_query)
                return res.records()

    def match_by_property(self, node_type, property_name, property_val, case_sensitive=False):
        match_query = "MATCH (s:{node_type}) WHERE s.{property_name}=~'{regex}{property_val}' RETURN s as skill"
        regex = '(?i)' if case_sensitive else ''
        match_query = match_query.format(node_type=node_type, property_name=property_name,
                                         property_val=property_val, regex=regex)
        with self.driver.session() as session:
            with session.begin_transaction() as tx:
                res = tx.run(match_query)
                return [r['skill'] for r in res.records()]

    def match_parent_by_property(self, node_type, parent_type, rel_type, property_name, property_val, case_sensitive=False):
        match_query = "MATCH(c:{node_type})-[:{rel_type}]->(p:{parent_type}) where c.{property_name}=~'{regex}{" \
                      "property_val}' RETURN p as parent "
        regex = '(?i)' if case_sensitive else ''
        match_query = match_query.format(node_type=node_type, parent_type=parent_type, rel_type=rel_type,
                                         property_name=property_name, property_val=property_val, regex=regex)
        with self.driver.session() as session:
            with session.begin_transaction() as tx:
                res = tx.run(match_query)
                return [r['parent']for r in res.records()]


