"""手書き数字認識 FastAPI サーバー。"""

import base64
import io
import pickle
from pathlib import Path

import numpy as np
from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from PIL import Image, ImageOps
from pydantic import BaseModel

MODEL_PATH = Path("model.pkl")

app = FastAPI(title="MNIST Sketch")

if not MODEL_PATH.exists():
    raise RuntimeError("model.pkl が見つかりません。先に python train.py を実行してください。")

with open(MODEL_PATH, "rb") as f:
    model = pickle.load(f)


class PredictRequest(BaseModel):
    image: str  # base64 encoded PNG (data URL)


class PredictResponse(BaseModel):
    digit: int
    confidence: float
    probabilities: list[float]


def preprocess(data_url: str) -> np.ndarray:
    header, encoded = data_url.split(",", 1)
    img_bytes = base64.b64decode(encoded)
    img = Image.open(io.BytesIO(img_bytes)).convert("L")

    img = ImageOps.invert(img)

    img = img.resize((28, 28), Image.LANCZOS)

    arr = np.array(img, dtype=np.float32) / 255.0
    return arr.flatten().reshape(1, -1)


@app.post("/predict", response_model=PredictResponse)
def predict(req: PredictRequest):
    try:
        arr = preprocess(req.image)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"画像の処理に失敗しました: {e}")

    proba = model.predict_proba(arr)[0]
    digit = int(np.argmax(proba))
    confidence = float(proba[digit])

    return PredictResponse(
        digit=digit,
        confidence=confidence,
        probabilities=proba.tolist(),
    )


app.mount("/", StaticFiles(directory="static", html=True), name="static")
