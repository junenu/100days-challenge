"""MNIST モデルの学習スクリプト。初回のみ実行する。"""

import pickle
from pathlib import Path

import numpy as np
from sklearn.datasets import fetch_openml
from sklearn.neural_network import MLPClassifier
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.pipeline import Pipeline

MODEL_PATH = Path("model.pkl")


def train():
    print("MNIST データセットをロード中...")
    mnist = fetch_openml("mnist_784", version=1, as_frame=False, parser="liac-arff")
    X, y = mnist.data, mnist.target.astype(int)

    X = X / 255.0

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42
    )

    print("モデルを学習中... (数分かかります)")
    pipeline = Pipeline([
        ("scaler", StandardScaler()),
        ("clf", MLPClassifier(
            hidden_layer_sizes=(128, 64),
            max_iter=20,
            random_state=42,
            verbose=True,
            early_stopping=True,
            validation_fraction=0.1,
        )),
    ])

    pipeline.fit(X_train, y_train)

    accuracy = pipeline.score(X_test, y_test)
    print(f"\nテスト精度: {accuracy:.4f} ({accuracy * 100:.2f}%)")

    with open(MODEL_PATH, "wb") as f:
        pickle.dump(pipeline, f)

    print(f"モデルを保存しました: {MODEL_PATH}")


if __name__ == "__main__":
    train()
