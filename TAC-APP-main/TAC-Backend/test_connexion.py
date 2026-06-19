'''
from DataBase import driver

with driver.session() as session:
    result = session.run("RETURN 'Neo4j connecté !' AS message")
    print(result.single()["message"])
 
from google import genai

client = genai.Client(api_key="")

for model in client.models.list():
    print(model.name)
'''
from google import genai

client = genai.Client(api_key="")

response = client.models.generate_content(
    model="gemini-2.5-flash",
    contents="Bonjour, tu peux m'aider ?"
)
print(response.text)


'''
from arango import ArangoClient

client = ArangoClient(hosts="http://localhost:8529")
db = client.db("as", username="rasri", password="")

thesaurus_col = db.collection("thesaurus")


thesaurus_data = [
    {
        "_key": "theso_architecture",
        "title": "Thésaurus Architecture",
        "description": "Vocabulaire contrôlé sur l'architecture du patrimoine",
        "language": "fr",
        "creator": "FSP",
        "concepts": [
            {
                "prefLabel": "Arc brisé",
                "altLabel": ["arc ogival", "arc gothique"],
                "definition": "Arc dont le sommet est formé par deux courbes se rejoignant en pointe.",
                "broader": "Architecture gothique",
                "narrower": ["Arc en tiers-point", "Arc en accolade"],
                "related": ["Voûte", "Cathédrale"]
            },
            {
                "prefLabel": "Voûte ogivale",
                "altLabel": ["voûte gothique"],
                "definition": "Voûte caractéristique de l'architecture gothique.",
                "broader": "Architecture gothique",
                "narrower": ["Voûte en étoile", "Voûte à liernes"],
                "related": ["Arc brisé", "Pilier"]
            },
            {
                "prefLabel": "Contrefort",
                "altLabel": ["éperon"],
                "definition": "Massif de maçonnerie faisant saillie contre un mur pour le renforcer.",
                "broader": "Éléments structurels",
                "narrower": ["Arc-boutant"],
                "related": ["Mur", "Cathédrale"]
            }
        ]
    },
    {
        "_key": "theso_peinture",
        "title": "Thésaurus Peinture",
        "description": "Vocabulaire contrôlé sur les techniques de peinture",
        "language": "fr",
        "creator": "FSP",
        "concepts": [
            {
                "prefLabel": "Fresque",
                "altLabel": ["peinture murale", "buon fresco"],
                "definition": "Technique de peinture murale exécutée sur un enduit frais à base de chaux.",
                "broader": "Peinture murale",
                "narrower": ["Fresque sèche", "Fresque humide"],
                "related": ["Enduit", "Pigment"]
            },
            {
                "prefLabel": "Tempera",
                "altLabel": ["détrempe", "peinture à l'oeuf"],
                "definition": "Technique picturale utilisant des pigments liés à l'eau et à un liant organique.",
                "broader": "Techniques picturales",
                "narrower": [],
                "related": ["Pigment", "Panneau de bois"]
            }
        ]
    },
    {
        "_key": "theso_archeologie",
        "title": "Thésaurus Archéologie",
        "description": "Vocabulaire contrôlé sur l'archéologie",
        "language": "fr",
        "creator": "FSP",
        "concepts": [
            {
                "prefLabel": "Stratigraphie",
                "altLabel": ["analyse stratigraphique"],
                "definition": "Méthode d'étude des couches sédimentaires pour dater et interpréter les vestiges archéologiques.",
                "broader": "Méthodes archéologiques",
                "narrower": ["Stratigraphie relative", "Stratigraphie absolue"],
                "related": ["Fouille", "Datation"]
            }
        ]
    }
]


for theso in thesaurus_data:
    if not thesaurus_col.has(theso["_key"]):
        thesaurus_col.insert(theso)
        print(f"✅ Thésaurus inséré : {theso['title']} ({len(theso['concepts'])} concept(s))")
    else:
        print(f"⚠️ Déjà existant : {theso['title']}")    



def get_arango_db():
    client = ArangoClient(hosts="http://localhost:8529")
    db = client.db("as", username="rasri", password="")
    return db

def get_arango_thesauri():
    db = get_arango_db()
    thesauri = list(db.aql.execute("FOR theso IN thesaurus RETURN theso"))
    return {"thesauri": thesauri}


print("\n" + "="*50)
print("📚 THÉSAURUS ET LEURS CONCEPTS")
print("="*50)

cursor = get_arango_thesauri()


for theso in cursor["thesauri"]:
    print(f"\n📖 {theso['title']}")


from arango import ArangoClient

client = ArangoClient(hosts="http://localhost:8529")
db = client.db("as", username="rasri", password="")

result = list(db.aql.execute("FOR theso IN thesaurus RETURN theso"))
print("Nombre :", len(result))
print(result)

'''


