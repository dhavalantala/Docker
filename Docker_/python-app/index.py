import os
import uvicorn
from fastapi import FastAPI

# Read port from environment variable, default to 8000
PORT = int(os.getenv("PORT", 8000))

app = FastAPI()

@app.get("/")
def read_root():
    return {
        "status": "Success",
        "message": "Hello from first image"
    }

@app.get("/health")
def health_check():
    return {"message": "I am healthy"}

if __name__ == "__main__":
    print(f"Server started on PORT {PORT}")
    uvicorn.run("index:app", host="0.0.0.0", port=PORT, reload=True)

