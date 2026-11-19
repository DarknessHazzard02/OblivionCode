# ==============================================================================
# Author: Haz
# FreeCodeCamp Machine Learning with Python - Cat and Dog Image Classifier
# The original trains a Keras CNN on 150x150 photos and must reach >= 63%
# accuracy. Photos and TensorFlow aren't available here, so this version
# keeps the same pipeline (data generator -> augmentation -> conv layer ->
# pooling -> dense -> sigmoid) on tiny 8x8 synthetic "images":
#   cats = horizontal stripes, dogs = vertical stripes, plus noise.
# Everything is pure Python so the mechanics of a CNN are readable.
# ==============================================================================

import math
import random

# ==============================================================================
# Config
# ==============================================================================
IMG = 8
EPOCHS = 15
LR = 0.05
RNG = random.Random(42)

# Fixed edge-detecting kernels (in a real CNN these are learned)
KERNELS = [
    [[1, 1, 1], [-1, -1, -1], [0, 0, 0]],   # horizontal edges
    [[1, -1, 0], [1, -1, 0], [1, -1, 0]],   # vertical edges
]


# ==============================================================================
# Data generator with augmentation (flip + noise), like ImageDataGenerator
# ==============================================================================
def make_image(label):
    img = [[0.0] * IMG for _ in range(IMG)]
    for r in range(IMG):
        for c in range(IMG):
            stripe = (r if label == 0 else c) % 2
            img[r][c] = stripe + RNG.gauss(0, 0.35)
    return img


def augment(img):
    if RNG.random() < 0.5:
        img = [row[::-1] for row in img]          # horizontal flip
    return [[px + RNG.gauss(0, 0.1) for px in row] for row in img]


def dataset(n):
    return [(make_image(lbl), lbl) for lbl in (RNG.choice([0, 1]) for _ in range(n))]


# ==============================================================================
# Layers
# ==============================================================================
def conv2d_relu(img, kernel):
    out = []
    for r in range(IMG - 2):
        row = []
        for c in range(IMG - 2):
            s = sum(img[r + i][c + j] * kernel[i][j]
                    for i in range(3) for j in range(3))
            row.append(max(0.0, s))
        out.append(row)
    return out


def max_pool(fmap, size=2):
    n = len(fmap) // size
    return [max(fmap[r * size + i][c * size + j]
                for i in range(size) for j in range(size))
            for r in range(n) for c in range(n)]


def features(img):
    vec = []
    for k in KERNELS:
        vec += max_pool(conv2d_relu(img, k))
    return vec


def sigmoid(z):
    return 1.0 / (1.0 + math.exp(-max(-60, min(60, z))))


# ==============================================================================
# Dense output layer trained with SGD on binary cross-entropy
# ==============================================================================
def train(data):
    n_feat = len(features(data[0][0]))
    w = [0.0] * n_feat
    b = 0.0
    for epoch in range(1, EPOCHS + 1):
        RNG.shuffle(data)
        correct = 0
        for img, label in data:
            x = features(augment(img))
            p = sigmoid(sum(wi * xi for wi, xi in zip(w, x)) + b)
            correct += (p >= 0.5) == bool(label)
            err = p - label
            w = [wi - LR * err * xi for wi, xi in zip(w, x)]
            b -= LR * err
        if epoch % 5 == 0:
            print(f"epoch {epoch:2}  train accuracy {correct / len(data):.1%}")
    return w, b


def predict(w, b, img):
    return sigmoid(sum(wi * xi for wi, xi in zip(w, features(img))) + b)


if __name__ == "__main__":
    w, b = train(dataset(400))
    test = dataset(50)
    probs = [predict(w, b, img) for img, _ in test]
    accuracy = sum((p >= 0.5) == bool(lbl) for p, (_, lbl) in zip(probs, test)) / len(test)
    for p in probs[:5]:
        print(f"{p:.0%} {'dog' if p >= 0.5 else 'cat'}")
    print(f"Test accuracy: {accuracy:.0%}  ->  {'PASS' if accuracy >= 0.63 else 'FAIL'} (goal 63%)")
