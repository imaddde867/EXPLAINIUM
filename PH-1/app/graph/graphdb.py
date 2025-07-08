"""
Knowledge graph integration utilities for EXPLAINIUM Phase 2
"""
from neo4j import GraphDatabase

# Example: Connect to Neo4j and add a relationship
def add_entity_relationship(uri: str, user: str, password: str, source: str, target: str, rel_type: str):
    driver = GraphDatabase.driver(uri, auth=(user, password))
    with driver.session() as session:
        session.run(
            "MERGE (a:Entity {name: $source}) "
            "MERGE (b:Entity {name: $target}) "
            "MERGE (a)-[r:%s]->(b)" % rel_type,
            {"source": source, "target": target}
        )
    driver.close()
