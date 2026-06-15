from flask import Flask, jsonify
import requests
import os
import redis

app = Flask(__name__)

DATA_SERVICE_URL = os.environ.get(
    "DATA_SERVICE_URL",
    "http://data-service:5001"
)

REDIS_HOST = os.environ.get("REDIS_HOST", "redis")
REDIS_PORT = int(os.environ.get("REDIS_PORT", 6379))
redis_client = redis.Redis(
    host=REDIS_HOST,
    port=REDIS_PORT,
    decode_responses=True
)

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

@app.route("/health")
def health():
    return jsonify({"status": "healthy"})

@app.route("/config")
def config():
    return jsonify({
        "data_service": DATA_SERVICE_URL,
        "redis_host": REDIS_HOST,
        "redis_port": REDIS_PORT
    })

@app.route("/cache-model/<model_name>")
def cache_model(model_name):

    redis_client.set("last_model", model_name)

    return jsonify({
        "message": f"{model_name} cached"
    })

@app.route("/get-model")
def get_model():

    model = redis_client.get("last_model")

    return jsonify({
        "last_model": model
    })

@app.route("/counter")
def counter():

    visits = redis_client.incr("page_visits")

    return jsonify({
        "visits": visits
    })

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
