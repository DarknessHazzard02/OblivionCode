# ==============================================================================
# Author: Haz
# FreeCodeCamp Machine Learning with Python - Neural Network SMS Text Classifier
# `predict_message(text)` returns [probability_of_spam, "ham" | "spam"].
# The original trains a Keras model on the SMS Spam Collection; this version
# is a single-neuron network (logistic regression) over a bag-of-words,
# trained with stochastic gradient descent in pure Python.
# Training messages are short invented examples, not the course dataset.
# ==============================================================================

import math
import random
import re

# ==============================================================================
# Training data (invented)
# ==============================================================================
HAM = [
    "how are you doing today", "i will call you later", "see you at lunch",
    "are we still meeting tomorrow", "thanks for the help yesterday",
    "can you pick up milk on the way home", "running late be there soon",
    "happy birthday hope you have a great day", "what time is the game",
    "i left my keys in your car", "the meeting moved to friday",
    "lets watch a movie tonight", "did you finish the report",
    "good morning have a nice day", "ok sounds good to me",
]
SPAM = [
    "win cash now click here", "you have won a free prize call now",
    "urgent your account has been selected claim reward",
    "free entry to win a brand new phone text win to 80086",
    "congratulations you won 1000 cash claim now",
    "sale today only call now for free ringtones",
    "you are a winner reply now to claim your prize",
    "limited offer free credit text yes now",
    "claim your free vacation call this number now",
    "exclusive deal win money fast click link",
    "big sale this week to stop these texts reply stop",
    "new mobile service install the app on your phone now",
    "live now our new video service free trial for your mobile",
    "to opt out of texts call this number",
]


# ==============================================================================
# Text -> features
# ==============================================================================
def tokenize(text):
    return re.findall(r"[a-z0-9]+", text.lower())


def build_vocab(messages):
    vocab = sorted({tok for msg in messages for tok in tokenize(msg)})
    return {tok: i for i, tok in enumerate(vocab)}


def vectorize(text, vocab):
    vec = [0.0] * len(vocab)
    for tok in tokenize(text):
        if tok in vocab:
            vec[vocab[tok]] = 1.0
    return vec


def sigmoid(z):
    return 1.0 / (1.0 + math.exp(-z))


# ==============================================================================
# Training
# ==============================================================================
def train(samples, vocab, epochs=200, lr=0.3, seed=0):
    rng = random.Random(seed)
    w = [0.0] * len(vocab)
    b = 0.0
    for _ in range(epochs):
        rng.shuffle(samples)
        for text, label in samples:
            x = vectorize(text, vocab)
            p = sigmoid(sum(wi * xi for wi, xi in zip(w, x)) + b)
            err = p - label
            w = [wi - lr * err * xi for wi, xi in zip(w, x)]
            b -= lr * err
    return w, b


SAMPLES = [(m, 0) for m in HAM] + [(m, 1) for m in SPAM]
VOCAB = build_vocab([m for m, _ in SAMPLES])
WEIGHTS, BIAS = train(list(SAMPLES), VOCAB)


def predict_message(pred_text):
    x = vectorize(pred_text, VOCAB)
    prob = sigmoid(sum(wi * xi for wi, xi in zip(WEIGHTS, x)) + BIAS)
    return [round(prob, 4), "spam" if prob >= 0.5 else "ham"]


# ==============================================================================
# Challenge test
# ==============================================================================
if __name__ == "__main__":
    tests = [
        ("how are you doing today", "ham"),
        ("sale today! to stop texts call 98912460324", "spam"),
        ("i dont want to go. can we try it a different day? available sat", "ham"),
        ("our new mobile video service is live. just install on your phone", "spam"),
        ("you have won 1000 cash! call to claim your prize.", "spam"),
        ("i'll bring it tomorrow. don't forget the milk.", "ham"),
        ("wow, is your arm alright. that happened to me one time too", "ham"),
    ]
    passed = 0
    for text, expected in tests:
        result = predict_message(text)
        ok = result[1] == expected
        passed += ok
        print(f"{'OK ' if ok else 'XX '} {result}  <- {text}")
    print(f"\n{passed}/{len(tests)} correct")
