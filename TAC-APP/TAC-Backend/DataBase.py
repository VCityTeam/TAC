# ==============================
# NEO4J (commenté — remplacé par ArangoDB)
# ==============================
# from neo4j import GraphDatabase
#
# driver = GraphDatabase.driver(
#     "neo4j://127.0.0.1:7687",
#     auth=("neo4j", "MIDvi1234!!")
# )
#
# def get_session():
#     return driver.session()

# ==============================
# ARANGODB
# ==============================
from arango import ArangoClient

_arango_client = ArangoClient(hosts="http://localhost:8529")

def get_arango_db():
    return _arango_client.db("_system", username="root", password="MIDvi1234!!")
