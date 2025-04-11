from fastapi import FastAPI

app = FastAPI()


@app.get("/predict")
def predict():
    return {"result": "dummy prediction"}
