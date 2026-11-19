# ==============================================================================
# Author: Haz
# FreeCodeCamp Machine Learning with Python - Rock Paper Scissors
# A player that beats the four built-in bots (quincy, abbey, kris, mrugesh)
# at least 60% of the time, using an ensemble of Markov chains plus a
# "mirror" predictor that models bots which study your own moves.
# ==============================================================================

import random
from collections import Counter, defaultdict

# ==============================================================================
# Constants
# ==============================================================================
MOVES = ["R", "P", "S"]
BEATS = {"R": "P", "P": "S", "S": "R"}  # move -> move that beats it


# ==============================================================================
# Player
# ==============================================================================
class EnsemblePlayer:
    """Runs several predictors and plays the one that has been winning lately.

    Predictors:
      - Markov chains of order 1..5 over the opponent's moves.
      - Mirror: models an opponent that predicts MY next move from pairs of
        my own past moves (beats bots that study you, like abbey).
    """

    ORDERS = (1, 2, 3, 4, 5)
    DECAY = 0.9

    def __init__(self):
        self.reset()

    def reset(self):
        self.opp = []
        self.mine = []
        self.tables = {o: defaultdict(Counter) for o in self.ORDERS}
        self.my_pairs = Counter()
        self.scores = Counter()
        self.last_suggestions = {}

    def _markov(self, order):
        key = "".join(self.opp[-order:])
        table = self.tables[order]
        if len(self.opp) >= order and key in table:
            return BEATS[table[key].most_common(1)[0][0]]
        return None

    def _mirror(self):
        if not self.mine:
            return None
        last = self.mine[-1]
        my_next = max(MOVES, key=lambda m: self.my_pairs[last + m])
        their_move = BEATS[my_next]
        return BEATS[their_move]

    def __call__(self, prev_opponent_play):
        if prev_opponent_play == "":
            self.reset()
        else:
            # Score last round's suggestions against what the opponent played
            for name, move in self.last_suggestions.items():
                self.scores[name] *= self.DECAY
                if move == BEATS[prev_opponent_play]:
                    self.scores[name] += 1
                elif BEATS[move] == prev_opponent_play:
                    self.scores[name] -= 1
            # Learn
            for o in self.ORDERS:
                if len(self.opp) >= o:
                    self.tables[o]["".join(self.opp[-o:])][prev_opponent_play] += 1
            self.opp.append(prev_opponent_play)

        suggestions = {f"markov{o}": self._markov(o) for o in self.ORDERS}
        suggestions["mirror"] = self._mirror()
        self.last_suggestions = {k: v for k, v in suggestions.items() if v}

        if self.last_suggestions:
            best = max(self.last_suggestions, key=lambda k: self.scores[k])
            move = self.last_suggestions[best]
        else:
            move = random.choice(MOVES)

        if self.mine:
            self.my_pairs[self.mine[-1] + move] += 1
        self.mine.append(move)
        return move


# ==============================================================================
# Opponent bots (same behaviour as the freeCodeCamp boilerplate)
# ==============================================================================
def quincy(prev, counter=[0]):
    counter[0] += 1
    return ["R", "R", "P", "P", "S"][counter[0] % 5]


def kris(prev):
    return BEATS[prev or "R"]


def mrugesh(prev, history=[]):
    history.append(prev)
    last_ten = [m for m in history[-10:] if m]
    most = Counter(last_ten).most_common(1)[0][0] if last_ten else "S"
    return BEATS[most]


def abbey(prev, history=["R"], pairs={}):
    prev = prev or "R"
    history.append(prev)
    last_two = "".join(history[-2:])
    if len(last_two) == 2:
        pairs[last_two] = pairs.get(last_two, 0) + 1
    options = [prev + m for m in MOVES]
    predicted = max(options, key=lambda k: pairs.get(k, 0))[-1]
    return BEATS[predicted]


# ==============================================================================
# Game loop
# ==============================================================================
def play(player1, player2, num_games):
    p1_prev, p2_prev = "", ""
    results = Counter()
    for _ in range(num_games):
        p1 = player1(p2_prev)
        p2 = player2(p1_prev)
        if p1 == p2:
            results["tie"] += 1
        elif BEATS[p2] == p1:
            results["p1"] += 1
        else:
            results["p2"] += 1
        p1_prev, p2_prev = p1, p2
    decided = results["p1"] + results["p2"]
    win_rate = results["p1"] / decided * 100 if decided else 0.0
    return results, win_rate


if __name__ == "__main__":
    for bot in (quincy, abbey, kris, mrugesh):
        results, rate = play(EnsemblePlayer(), bot, 1000)
        status = "PASS" if rate >= 60 else "FAIL"
        print(f"{bot.__name__:8} win rate {rate:5.1f}%  {dict(results)}  {status}")
