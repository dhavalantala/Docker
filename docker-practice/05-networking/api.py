from flask import Flask, jsonify
import requests
import os

app = Flask(__name__)

DATA_SERVICE_URL = os.environ.get("DATA_SERVICE_URL", "http://data-service:5001")

@app.route("/")
def home():
    try:
        response = requests.get(f"{DATA_SERVICE_URL}/data")
        data = response.json()
        return jsonify({
            "api": "running",
            "data_from_other_container": data
        })
    except Exception as e:
        return jsonify({"api": "running", "error": str(e)})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
