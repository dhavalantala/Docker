from flask import Flask, jsonify
import os

app = Flask(__name__)

# Read from environment variables — NOT hardcoded
MODEL_NAME = os.environ.get("MODEL_NAME", "default-model")
ENV        = os.environ.get("APP_ENV", "development")
PORT       = int(os.environ.get("PORT", 5000))

@app.route("/")
def home():
    return jsonify({
        "message": "ML Model Server",
        "model": MODEL_NAME,
        "environment": ENV
    })

@app.route("/health")
def health():
    return jsonify({"status": "healthy"})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=PORT)
