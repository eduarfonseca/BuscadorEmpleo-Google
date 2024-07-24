import os
from flask import Flask, send_file, request, jsonify
from pymongo import MongoClient
from mistralai.client import MistralClient
from getpass import getpass

app = Flask(__name__)

# Conectar a MongoDB
clientM = MongoClient('mongodb+srv://ruben:zixelowe1@personal.yycznyk.mongodb.net/')
db = clientM['Salarios_DEV']
coleccion = db['google_offers']

# Configurar MistralAI
# api_key = os.environ.get('MISTRAL_API_KEY') or getpass('Key: ')
client = MistralClient(api_key="IntnyAbpxjAlR9QARqymXuOygsgSkE2a")

def obtener_embeddings(texto):
    embeddings_batch_response = client.embeddings(
        model="mistral-embed",
        input=[texto],
    )
    return embeddings_batch_response.data[0].embedding

def buscar(embedding, cantResultados):
    pipeline = [
        {
            "$vectorSearch": {
                "index": "eduardo_index",
                "path": "embedding",
                "queryVector": embedding,
                "numCandidates": cantResultados,
                "limit": cantResultados
            }
        }
    ]
    resultados = list(coleccion.aggregate(pipeline))
    return resultados

@app.route("/")
def index():
    return send_file('src/index.html')

@app.route("/search", methods=['POST'])
def search():
    query = request.json['query']
    embedding = obtener_embeddings(query)
    results = buscar(embedding, 8)
    # Convertir los resultados a un formato JSON serializable
    serializable_results = []
    for result in results:
        serializable_result = {
            'title': result.get('Title', 'N/A'),
            'category': result.get('Category', 'N/A'),
            'location': result.get('Location', 'N/A'),
            'responsibilities': result.get('Responsibilities', 'N/A'),
            'minimum_qualifications': result.get('Minimum Qualifications', 'N/A'),
            'preferred_qualifications': result.get('Preferred Qualifications', 'N/A')
        }
        serializable_results.append(serializable_result)
    return jsonify(serializable_results)

def main():
    app.run(port=int(os.environ.get('PORT', 80)))

if __name__ == "__main__":
    main()