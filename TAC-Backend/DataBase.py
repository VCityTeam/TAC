from neo4j import GraphDatabase

driver = GraphDatabase.driver(
    "neo4j://127.0.0.1:7687", 
    auth=("neo4j", "MIDvi1234!!")
    )

def get_session():
    return driver.session()

