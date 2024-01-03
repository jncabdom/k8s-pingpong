from flask import Flask, request, jsonify
from neo4j import GraphDatabase
from datetime import datetime
import os

app = Flask(__name__)

# Configure Neo4j connection
uri = os.getenv('NEO4J_URI', "bolt://192.168.49.2:30687")
username = os.getenv('NEO4J_USER', "neo4j")
password = os.getenv('NEO4J_PASSWORD', "password")
driver = GraphDatabase.driver(uri, auth=(username, password))

def create_ping(tx, origin, destiny, timeStamp):
    query = """
    MERGE (a:Service {name: $origin})
    MERGE (b:Service {name: $destiny})
    CREATE (a)-[r:PINGED {timeStamp: $timeStamp}]->(b)
    RETURN a.name AS origin, b.name AS destiny, r.timeStamp AS timeStamp
    """
    result = tx.run(query, origin=origin, destiny=destiny, timeStamp=timeStamp)
    return result.single()

@app.route('/pings', methods=['POST'])
def record_ping():
    data = request.json
    origin = data['origin']
    destiny = data['destiny']
    timeStamp = data.get('timeStamp', datetime.utcnow().isoformat())

    print(f"Registering ping between [${origin}] - [${destiny}]")

    try:
        with driver.session() as session:
            ping = session.write_transaction(create_ping, origin, destiny, timeStamp)
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
