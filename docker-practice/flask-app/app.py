from flask import Flask
import os

ENV = os.getenv("APP_ENV", "development")

app = Flask(__name__)

@app.route("/")
def home():
    print(f"{ENV}")
    return {"message": "Hello Docker"}

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
