from flask import Flask, jsonify

app = Flask(__name__)

@app.route("/data")
def data():
    return jsonify({
        "service": "data-service",
        "records": ["model_v1", "model_v2", "model_v3"]
    })

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5001)
