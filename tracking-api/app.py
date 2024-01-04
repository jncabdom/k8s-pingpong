from flask import Flask, request, jsonify
from neo4j import GraphDatabase
import os

app = Flask(__name__)

# Neo4j connection configuration
uri = os.getenv('NEO4J_URI', "bolt://192.168.49.2:30687")
username = os.getenv('NEO4J_USER', "neo4j")
password = os.getenv('NEO4J_PASSWORD', "password")
driver = GraphDatabase.driver(uri, auth=(username, password))

def update_ping_count(tx, origin, target):
    query = """
    MERGE (a:Service {name: $origin})
    MERGE (b:Service {name: $target})
    MERGE (a)-[r:PINGED]->(b)
    ON CREATE SET r.count = 1
    ON MATCH SET r.count = r.count + 1
    RETURN a.name AS origin, b.name AS target, r.count AS count
    """
    result = tx.run(query, origin=origin, target=target)
    return result.single()

@app.route('/pings', methods=['POST'])
def record_ping():
    data = request.json
    origin = data['origin']
    target = data['target']

    print(f"Registering ping between [${origin}] - [${target}]")

    try:
        with driver.session() as session:
            ping = session.write_transaction(update_ping_count, origin, target)
            if ping:
                return jsonify(ping), 201
            else:
                return jsonify({"error": "No record created"}), 400
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/health', methods=['GET'])
def health():
    return "API is running", 200

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=int(os.getenv('PORT', 5000)))
