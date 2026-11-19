# ==============================================================================
# Author: Haz
# FreeCodeCamp Machine Learning with Python - Book Recommendation Engine (KNN)
# `get_recommends(title)` returns [title, [[book, distance], ...]] with the
# 5 nearest books by cosine distance over the user-rating vectors.
# The original uses scikit-learn NearestNeighbors on Book-Crossings; this
# version implements item-based KNN in pure Python on invented ratings.
# Course filtering rule kept: users with >= 200 ratings and books with
# >= 100 ratings (scaled down here to MIN_USER / MIN_BOOK).
# ==============================================================================

import math
import random
from collections import defaultdict

# ==============================================================================
# Config
# ==============================================================================
MIN_USER_RATINGS = 5
MIN_BOOK_RATINGS = 5
NEIGHBORS = 5

GENRES = {
    "fantasy": ["The Silver Gate", "Dragons of Ember", "The Last Rune",
                "Crown of Ash", "Wizard's Winter", "The Hollow Throne"],
    "mystery": ["Murder at Pier 9", "The Quiet Witness", "Cold Ledger",
                "The Locked Study", "Shadows on Elm Street", "Final Alibi"],
    "scifi":   ["Orbit Zero", "The Mars Accord", "Neural Tide",
                "Starlight Protocol", "Quantum Drift", "Echoes of Titan"],
}


# ==============================================================================
# Synthetic ratings: each user prefers one genre
# ==============================================================================
def make_ratings(users=120, seed=3):
    rng = random.Random(seed)
    ratings = []
    for u in range(users):
        fav = rng.choice(list(GENRES))
        for genre, books in GENRES.items():
            for book in books:
                if rng.random() < (0.85 if genre == fav else 0.15):
                    score = rng.randint(7, 10) if genre == fav else rng.randint(1, 5)
                    ratings.append((f"user_{u}", book, score))
    return ratings


# ==============================================================================
# Pivot: book -> {user: rating}, after filtering
# ==============================================================================
def build_matrix(ratings):
    per_user = defaultdict(int)
    per_book = defaultdict(int)
    for user, book, _ in ratings:
        per_user[user] += 1
        per_book[book] += 1
    matrix = defaultdict(dict)
    for user, book, score in ratings:
        if per_user[user] >= MIN_USER_RATINGS and per_book[book] >= MIN_BOOK_RATINGS:
            matrix[book][user] = score
    return matrix


def cosine_distance(a, b):
    dot = sum(a[u] * b[u] for u in a.keys() & b.keys())
    norm_a = math.sqrt(sum(v * v for v in a.values()))
    norm_b = math.sqrt(sum(v * v for v in b.values()))
    if not norm_a or not norm_b:
        return 1.0
    return 1.0 - dot / (norm_a * norm_b)


MATRIX = build_matrix(make_ratings())


def get_recommends(book=""):
    if book not in MATRIX:
        raise ValueError(f"Book not found or filtered out: {book!r}")
    target = MATRIX[book]
    distances = [(other, round(cosine_distance(target, vec), 4))
                 for other, vec in MATRIX.items() if other != book]
    distances.sort(key=lambda pair: pair[1])
    nearest = distances[:NEIGHBORS]
    # Course format: farthest first, closest last
    return [book, [list(pair) for pair in reversed(nearest)]]


if __name__ == "__main__":
    for title in ("The Silver Gate", "Cold Ledger", "Orbit Zero"):
        result = get_recommends(title)
        print(result[0])
        for rec, dist in result[1]:
            print(f"   {dist:.4f}  {rec}")
