from flask import Flask, jsonify

app = Flask(__name__)

MODELS = ["bert-base", "gpt2", "resnet50", "whisper"]

@app.route("/data")
def data():
    return jsonify({
        "service": "data-service",
        "available_models": MODELS
    })

@app.route("/health")
def health():
    return jsonify({"status": "healthy"})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5001)
