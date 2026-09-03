"""Deterministic authoritative game engines (pure Python, no UI, no DB).

Every function takes the persisted state dict (from game_room.state_json),
the rules dict (rules_json) and the seated player order, and returns a NEW
state dict. Invalid player intent raises MoveError, which the state layer
turns into a toast. The server is the only authority: nothing here trusts
client-provided positions, hands or outcomes.
"""

from __future__ import annotations

import math
import random

SUITS = ["S", "H", "D", "C"]
SUIT_GLYPH = {"S": "♠", "H": "♥", "D": "♦", "C": "♣"}
RANK_LABEL = {
    2: "2",
    3: "3",
    4: "4",
    5: "5",
    6: "6",
    7: "7",
    8: "8",
    9: "9",
    10: "10",
    11: "J",
    12: "Q",
    13: "K",
    14: "A",
}


class MoveError(ValueError):
    """Raised when a requested move is not legal."""


# ---------------------------------------------------------------------------
# LOTO: canonical French 90-ball 9x3 cards
# ---------------------------------------------------------------------------


def generate_loto_card(rng: random.Random) -> list[list[int]]:
    """Return a 3x9 grid holding exactly 15 numbers in valid decade columns."""
    for _ in range(400):
        counts = [1] * 9
        for _ in range(6):
            options = [i for i in range(9) if counts[i] < 3]
            counts[rng.choice(options)] += 1
        remaining = [5, 5, 5]
        grid = [[0] * 9 for _ in range(3)]
        ok = True
        for col in range(9):
            need = counts[col]
            rows = sorted(range(3), key=lambda r: (-remaining[r], rng.random()))
            pick = sorted(rows[:need])
            if any(remaining[r] <= 0 for r in pick):
                ok = False
                break
            low = 1 if col == 0 else col * 10
            high = 9 if col == 0 else (90 if col == 8 else col * 10 + 9)
            numbers = sorted(rng.sample(range(low, high + 1), need))
            for offset, row in enumerate(pick):
                grid[row][col] = numbers[offset]
                remaining[row] -= 1
        if ok and remaining == [0, 0, 0]:
            return grid
    raise MoveError("Impossible de generer un carton valide.")


def loto_initial_state() -> dict:
    return {"phase": "waiting", "drawn": [], "claims": [], "log": []}


def loto_draw(state: dict) -> tuple[dict, int]:
    drawn = list(state.get("drawn", []))
    pool = [n for n in range(1, 91) if n not in drawn]
    if not pool:
        raise MoveError("Les 90 boules ont ete tirees.")
    number = random.Random().choice(pool)
    drawn.append(number)
    new_state = dict(state)
    new_state["drawn"] = drawn
    return new_state, number


def loto_card_progress(
    grid: list[list[int]], drawn: list[int]
) -> tuple[list[int], int, int]:
    """Return (per-row marked counts, marked total, remaining to full house)."""
    drawn_set = set(drawn)
    rows = []
    total = 0
    for row in grid:
        hit = sum(1 for value in row if value and value in drawn_set)
        rows.append(hit)
        total += hit
    return rows, total, 15 - total


# ---------------------------------------------------------------------------
# DOMINO
# ---------------------------------------------------------------------------


def domino_initial_state(order: list[int], rules: dict) -> dict:
    rng = random.Random()
    tiles = [[a, b] for a in range(7) for b in range(a, 7)]
    if rules.get("no_double_six"):
        tiles = [t for t in tiles if t != [6, 6]]
    rng.shuffle(tiles)
    hands: dict[str, list[list[int]]] = {}
    per_hand = 7 if len(order) <= 2 else 6
    for account_id in order:
        hands[str(account_id)] = [tiles.pop() for _ in range(per_hand)]
    return {
        "phase": "playing",
        "hands": hands,
        "boneyard": tiles,
        "chain": [],
        "ends": [-1, -1],
        "turn": order[0],
        "scores": {str(a): 0 for a in order},
        "round": 1,
        "passes": 0,
        "last": "",
    }


def _domino_playable(tile: list[int], ends: list[int]) -> bool:
    if ends[0] < 0:
        return True
    return ends[0] in tile or ends[1] in tile


def domino_place(state: dict, actor: int, index: int, side: str) -> dict:
    hand = list(state["hands"].get(str(actor), []))
    if index < 0 or index >= len(hand):
        raise MoveError("Tuile introuvable.")
    tile = list(hand[index])
    ends = list(state["ends"])
    chain = list(state["chain"])
    if ends[0] < 0:
        chain = [tile]
        ends = [tile[0], tile[1]]
    elif side == "left":
        if tile[1] == ends[0]:
            chain = [tile] + chain
            ends[0] = tile[0]
        elif tile[0] == ends[0]:
            chain = [[tile[1], tile[0]]] + chain
            ends[0] = tile[1]
        else:
            raise MoveError("Cette tuile ne colle pas a gauche.")
    else:
        if tile[0] == ends[1]:
            chain = chain + [tile]
            ends[1] = tile[1]
        elif tile[1] == ends[1]:
            chain = chain + [[tile[1], tile[0]]]
            ends[1] = tile[0]
        else:
            raise MoveError("Cette tuile ne colle pas a droite.")
    hand.pop(index)
    new_state = dict(state)
    hands = dict(state["hands"])
    hands[str(actor)] = hand
    new_state["hands"] = hands
    new_state["chain"] = chain
    new_state["ends"] = ends
    new_state["passes"] = 0
    new_state["last"] = f"pose {tile[0]}-{tile[1]}"
    return new_state


def domino_draw(state: dict, actor: int) -> dict:
    boneyard = list(state.get("boneyard", []))
    if not boneyard:
        raise MoveError("La pioche est vide, passez votre tour.")
    tile = boneyard.pop()
    hands = dict(state["hands"])
    hands[str(actor)] = list(hands.get(actor, [])) + [tile]
    new_state = dict(state)
    new_state["hands"] = hands
    new_state["boneyard"] = boneyard
    new_state["last"] = "pioche"
    return new_state


def domino_can_play(state: dict, actor: int) -> bool:
    ends = state.get("ends", [-1, -1])
    return any(
        _domino_playable(list(t), list(ends))
        for t in state["hands"].get(str(actor), [])
    )


def domino_round_result(state: dict, order: list[int]) -> tuple[int, int]:
    """Return (winner_account_id, points won from losers' remaining pips)."""
    totals = {
        account_id: sum(sum(t) for t in state["hands"].get(str(account_id), []))
        for account_id in order
    }
    winner = min(totals, key=lambda a: totals[a])
    points = sum(v for a, v in totals.items() if a != winner)
    return winner, points


# ---------------------------------------------------------------------------
# LUDO
# ---------------------------------------------------------------------------

LUDO_TRACK = 51
LUDO_SAFE = {0, 8, 13, 21, 26, 34, 39, 47}


def ludo_path() -> list[tuple[int, int]]:
    """The 51 visible track cells of the 15x15 board, in travel order."""
    path: list[tuple[int, int]] = []
    path += [(6, c) for c in range(1, 6)]
    path += [(r, 6) for r in range(5, -1, -1)]
    path += [(0, 7)]
    path += [(r, 8) for r in range(0, 6)]
    path += [(6, c) for c in range(9, 15)]
    path += [(7, 14)]
    path += [(8, c) for c in range(14, 8, -1)]
    path += [(r, 8) for r in range(9, 15)]
    path += [(14, 7)]
    path += [(r, 6) for r in range(14, 8, -1)]
    path += [(8, c) for c in range(5, -1, -1)]
    path += [(7, 0)]
    return path


def ludo_initial_state(order: list[int], rules: dict) -> dict:
    colors = ["red", "green", "yellow", "blue"]
    goal = int(rules.get("goal_pawns", 3))
    return {
        "phase": "playing",
        "turn": order[0],
        "dice": 0,
        "rolled": False,
        "goal": goal,
        "colors": {str(a): colors[i % 4] for i, a in enumerate(order)},
        "starts": {str(a): (i % 4) * 13 for i, a in enumerate(order)},
        "pawns": {str(a): [-1] * goal for a in order},
        "hearts": {str(a): 3 for a in order},
        "last": "",
    }


def ludo_roll(state: dict, actor: int) -> dict:
    if state.get("rolled"):
        raise MoveError("Vous avez deja lance le de.")
    value = random.Random().randint(1, 6)
    new_state = dict(state)
    new_state["dice"] = value
    new_state["rolled"] = True
    new_state["last"] = f"de {value}"
    return new_state


def ludo_legal_pawns(state: dict, actor: int) -> list[int]:
    dice = int(state.get("dice", 0))
    if dice == 0:
        return []
    pawns = state["pawns"].get(str(actor), [])
    legal = []
    for index, pos in enumerate(pawns):
        if pos >= 58:
            continue
        if pos == -1:
            if dice == 6:
                legal.append(index)
            continue
        target = pos + dice
        if target <= 58:
            legal.append(index)
    return legal


def ludo_move(state: dict, actor: int, pawn_index: int) -> tuple[dict, str]:
    if not state.get("rolled"):
        raise MoveError("Lancez le de d'abord.")
    if pawn_index not in ludo_legal_pawns(state, actor):
        raise MoveError("Ce pion ne peut pas bouger.")
    dice = int(state["dice"])
    pawns_all = {k: list(v) for k, v in state["pawns"].items()}
    pawns = pawns_all[str(actor)]
    note = ""
    if pawns[pawn_index] == -1:
        pawns[pawn_index] = 0
    else:
        pawns[pawn_index] = pawns[pawn_index] + dice
    start = int(state["starts"].get(str(actor), 0))
    my_cell = (start + pawns[pawn_index]) % LUDO_TRACK
    if pawns[pawn_index] < LUDO_TRACK and my_cell not in LUDO_SAFE:
        for other, other_pawns in pawns_all.items():
            if other == str(actor):
                continue
            other_start = int(state["starts"].get(other, 0))
            for idx, pos in enumerate(other_pawns):
                if 0 <= pos < LUDO_TRACK:
                    if (other_start + pos) % LUDO_TRACK == my_cell:
                        other_pawns[idx] = -1
                        note = "capture"
    new_state = dict(state)
    new_state["pawns"] = pawns_all
    new_state["dice"] = 0
    new_state["rolled"] = False
    if note:
        hearts = dict(state.get("hearts", {}))
        new_state["hearts"] = hearts
    new_state["last"] = note or "deplacement"
    return new_state, note


def ludo_winner(state: dict) -> int:
    goal = int(state.get("goal", 3))
    for account_id, pawns in state["pawns"].items():
        if sum(1 for p in pawns if p >= 58) >= goal:
            return int(account_id)
    return 0


# ---------------------------------------------------------------------------
# FARITANY (Fanorona-inspired, 5x5 diamond network)
# ---------------------------------------------------------------------------


def faritany_neighbours(index: int) -> list[int]:
    row, col = divmod(index, 5)
    result = []
    steps = [(-1, 0), (1, 0), (0, -1), (0, 1)]
    if (row + col) % 2 == 0:
        steps += [(-1, -1), (-1, 1), (1, -1), (1, 1)]
    for dr, dc in steps:
        r, c = row + dr, col + dc
        if 0 <= r < 5 and 0 <= c < 5:
            result.append(r * 5 + c)
    return result


def faritany_initial_state(order: list[int]) -> dict:
    cells = ["" for _ in range(25)]
    for index in range(10):
        cells[index] = str(order[1] if len(order) > 1 else order[0])
    for index in range(15, 25):
        cells[index] = str(order[0])
    return {
        "phase": "playing",
        "cells": cells,
        "turn": order[0],
        "last": "",
    }


def faritany_move(state: dict, actor: int, origin: int, target: int) -> dict:
    cells = list(state["cells"])
    if not (0 <= origin < 25 and 0 <= target < 25):
        raise MoveError("Case invalide.")
    if cells[origin] != str(actor):
        raise MoveError("Ce pion n'est pas le votre.")
    if cells[target] != "":
        raise MoveError("La case d'arrivee est occupee.")
    if target not in faritany_neighbours(origin):
        raise MoveError("Deplacement non adjacent.")
    cells[origin] = ""
    cells[target] = str(actor)
    o_row, o_col = divmod(origin, 5)
    t_row, t_col = divmod(target, 5)
    dr, dc = t_row - o_row, t_col - o_col
    captures = 0
    row, col = t_row + dr, t_col + dc
    while 0 <= row < 5 and 0 <= col < 5:
        cell = cells[row * 5 + col]
        if cell == "" or cell == str(actor):
            break
        cells[row * 5 + col] = ""
        captures += 1
        row, col = row + dr, col + dc
    new_state = dict(state)
    new_state["cells"] = cells
    new_state["last"] = f"{captures} capture(s)" if captures else "deplacement"
    return new_state


def faritany_has_moves(state: dict, account_id: int) -> bool:
    cells = state["cells"]
    for index, owner in enumerate(cells):
        if owner != str(account_id):
            continue
        for neighbour in faritany_neighbours(index):
            if cells[neighbour] == "":
                return True
    return False


# ---------------------------------------------------------------------------
# JEUX DE POINT (dots and boxes, 5x5 dots / 4x4 boxes)
# ---------------------------------------------------------------------------

DOT_SIZE = 5
BOX_SIZE = DOT_SIZE - 1


def points_initial_state(order: list[int]) -> dict:
    return {
        "phase": "playing",
        "h": [""] * (DOT_SIZE * BOX_SIZE),
        "v": [""] * (BOX_SIZE * DOT_SIZE),
        "boxes": [""] * (BOX_SIZE * BOX_SIZE),
        "turn": order[0],
        "scores": {str(a): 0 for a in order},
        "last": "",
    }


def points_claim(
    state: dict, actor: int, kind: str, index: int
) -> tuple[dict, bool]:
    lines = list(state[kind])
    if index < 0 or index >= len(lines):
        raise MoveError("Ligne invalide.")
    if lines[index] != "":
        raise MoveError("Cette ligne est deja prise.")
    lines[index] = str(actor)
    horizontal = list(state["h"]) if kind == "v" else lines
    vertical = list(state["v"]) if kind == "h" else lines
    boxes = list(state["boxes"])
    scores = dict(state["scores"])
    closed = False
    for row in range(BOX_SIZE):
        for col in range(BOX_SIZE):
            box_index = row * BOX_SIZE + col
            if boxes[box_index] != "":
                continue
            top = horizontal[row * BOX_SIZE + col]
            bottom = horizontal[(row + 1) * BOX_SIZE + col]
            left = vertical[row * DOT_SIZE + col]
            right = vertical[row * DOT_SIZE + col + 1]
            if top and bottom and left and right:
                boxes[box_index] = str(actor)
                scores[str(actor)] = int(scores.get(actor, 0)) + 1
                closed = True
    new_state = dict(state)
    new_state["h"] = horizontal
    new_state["v"] = vertical
    new_state["boxes"] = boxes
    new_state["scores"] = scores
    new_state["last"] = "boite fermee" if closed else "ligne"
    return new_state, closed


def points_finished(state: dict) -> bool:
    return all(owner != "" for owner in state["boxes"])


# ---------------------------------------------------------------------------
# Card games: RAMI (52) and TRI (32)
# ---------------------------------------------------------------------------


def _deck(min_rank: int) -> list[int]:
    return [
        rank * 10 + suit for rank in range(min_rank, 15) for suit in range(4)
    ]


def card_label(code: int) -> str:
    return f"{RANK_LABEL[code // 10]}{SUIT_GLYPH[SUITS[code % 10]]}"


def cards_initial_state(order: list[int], min_rank: int, deal: int) -> dict:
    rng = random.Random()
    deck = _deck(min_rank)
    rng.shuffle(deck)
    hands = {str(a): [deck.pop() for _ in range(deal)] for a in order}
    discard = [deck.pop()]
    return {
        "phase": "playing",
        "hands": hands,
        "stock": deck,
        "discard": discard,
        "melds": {str(a): [] for a in order},
        "turn": order[0],
        "drawn": False,
        "last": "",
    }


def cards_draw(state: dict, actor: int, source: str) -> dict:
    if state.get("drawn"):
        raise MoveError("Vous avez deja pioche.")
    stock = list(state["stock"])
    discard = list(state["discard"])
    if source == "discard":
        if not discard:
            raise MoveError("La defausse est vide.")
        card = discard.pop()
    else:
        if not stock:
            stock = discard[:-1]
            discard = discard[-1:]
            random.Random().shuffle(stock)
        if not stock:
            raise MoveError("Plus aucune carte disponible.")
        card = stock.pop()
    hands = {k: list(v) for k, v in state["hands"].items()}
    hands[str(actor)].append(card)
    new_state = dict(state)
    new_state["hands"] = hands
    new_state["stock"] = stock
    new_state["discard"] = discard
    new_state["drawn"] = True
    new_state["last"] = f"pioche ({source})"
    return new_state


def cards_discard(state: dict, actor: int, index: int) -> dict:
    hands = {k: list(v) for k, v in state["hands"].items()}
    hand = hands.get(actor, [])
    if index < 0 or index >= len(hand):
        raise MoveError("Carte introuvable.")
    card = hand.pop(index)
    new_state = dict(state)
    new_state["hands"] = hands
    new_state["discard"] = list(state["discard"]) + [card]
    new_state["drawn"] = False
    new_state["last"] = f"defausse {card_label(card)}"
    return new_state


def validate_meld(codes: list[int]) -> str:
    """Return the meld kind, or raise when the selection is not a valid meld."""
    if len(codes) < 3:
        raise MoveError("Une combinaison demande au moins 3 cartes.")
    ranks = [c // 10 for c in codes]
    suits = [c % 10 for c in codes]
    if len(set(ranks)) == 1 and len(set(suits)) == len(suits):
        return "set"
    if len(set(suits)) == 1:
        ordered = sorted(ranks)
        if len(set(ordered)) == len(ordered) and all(
            ordered[i + 1] - ordered[i] == 1 for i in range(len(ordered) - 1)
        ):
            return "run"
    raise MoveError("Combinaison invalide: meme rang ou suite de meme couleur.")


def cards_meld(state: dict, actor: int, indexes: list[int]) -> dict:
    hands = {k: list(v) for k, v in state["hands"].items()}
    hand = hands.get(actor, [])
    chosen = [hand[i] for i in sorted(set(indexes)) if 0 <= i < len(hand)]
    validate_meld(chosen)
    for code in chosen:
        hand.remove(code)
    melds = {k: list(v) for k, v in state["melds"].items()}
    melds.setdefault(actor, []).append(chosen)
    new_state = dict(state)
    new_state["hands"] = hands
    new_state["melds"] = melds
    new_state["last"] = "combinaison posee"
    return new_state


def tri_play(state: dict, actor: int, index: int) -> dict:
    hands = {k: list(v) for k, v in state["hands"].items()}
    hand = hands.get(actor, [])
    if index < 0 or index >= len(hand):
        raise MoveError("Carte introuvable.")
    card = hand[index]
    discard = list(state["discard"])
    top = discard[-1] if discard else card
    if card // 10 != top // 10 and card % 10 != top % 10:
        raise MoveError("Jouez la meme couleur ou le meme rang.")
    hand.pop(index)
    new_state = dict(state)
    new_state["hands"] = hands
    new_state["discard"] = discard + [card]
    new_state["last"] = f"joue {card_label(card)}"
    return new_state


# ---------------------------------------------------------------------------
# BILLARD: deterministic 2D shot simulation (server side)
# ---------------------------------------------------------------------------

TABLE_W = 200.0
TABLE_H = 100.0
BALL_R = 3.0
POCKET_R = 6.5
POCKETS = [
    (4.0, 4.0),
    (100.0, 2.5),
    (196.0, 4.0),
    (4.0, 96.0),
    (100.0, 97.5),
    (196.0, 96.0),
]


def billard_initial_state(order: list[int]) -> dict:
    balls = [{"id": 0, "x": 50.0, "y": 50.0, "potted": False}]
    layout = [1, 9, 2, 10, 8, 3, 11, 4, 12, 5, 13, 6, 14, 7, 15]
    pointer = 0
    for column in range(5):
        for row in range(column + 1):
            balls.append(
                {
                    "id": layout[pointer],
                    "x": 140.0 + column * 6.4,
                    "y": 50.0 - column * 3.2 + row * 6.4,
                    "potted": False,
                }
            )
            pointer += 1
    return {
        "phase": "playing",
        "balls": balls,
        "turn": order[0],
        "groups": {},
        "last": "",
        "foul": False,
        "shots": 0,
    }


def _pocketed(x: float, y: float) -> bool:
    return any(math.hypot(x - px, y - py) < POCKET_R for px, py in POCKETS)


def billard_shoot(
    state: dict, actor: int, angle_deg: float, power: float
) -> tuple[dict, list[int], bool]:
    """Simulate one shot; return (state, potted ids, cue ball potted)."""
    balls = [dict(b) for b in state["balls"]]
    speed = max(2.0, min(100.0, power)) * 0.32
    radians = math.radians(angle_deg)
    for ball in balls:
        ball["vx"] = 0.0
        ball["vy"] = 0.0
    cue = next((b for b in balls if b["id"] == 0), None)
    if cue is None or cue["potted"]:
        raise MoveError("La blanche n'est pas sur la table.")
    cue["vx"] = math.cos(radians) * speed
    cue["vy"] = math.sin(radians) * speed
    potted: list[int] = []
    cue_potted = False

    for _ in range(2600):
        moving = False
        for ball in balls:
            if ball["potted"]:
                continue
            ball["x"] += ball["vx"] * 0.12
            ball["y"] += ball["vy"] * 0.12
            ball["vx"] *= 0.988
            ball["vy"] *= 0.988
            if abs(ball["vx"]) < 0.04 and abs(ball["vy"]) < 0.04:
                ball["vx"] = 0.0
                ball["vy"] = 0.0
            else:
                moving = True
            if ball["x"] < BALL_R:
                ball["x"] = BALL_R
                ball["vx"] = -ball["vx"] * 0.9
            if ball["x"] > TABLE_W - BALL_R:
                ball["x"] = TABLE_W - BALL_R
                ball["vx"] = -ball["vx"] * 0.9
            if ball["y"] < BALL_R:
                ball["y"] = BALL_R
                ball["vy"] = -ball["vy"] * 0.9
            if ball["y"] > TABLE_H - BALL_R:
                ball["y"] = TABLE_H - BALL_R
                ball["vy"] = -ball["vy"] * 0.9
            if _pocketed(ball["x"], ball["y"]):
                ball["potted"] = True
                ball["vx"] = 0.0
                ball["vy"] = 0.0
                if ball["id"] == 0:
                    cue_potted = True
                else:
                    potted.append(int(ball["id"]))
        live = [b for b in balls if not b["potted"]]
        for i in range(len(live)):
            for j in range(i + 1, len(live)):
                a, b = live[i], live[j]
                dx, dy = b["x"] - a["x"], b["y"] - a["y"]
                distance = math.hypot(dx, dy)
                if distance == 0 or distance >= BALL_R * 2:
                    continue
                nx, ny = dx / distance, dy / distance
                overlap = BALL_R * 2 - distance
                a["x"] -= nx * overlap / 2
                a["y"] -= ny * overlap / 2
                b["x"] += nx * overlap / 2
                b["y"] += ny * overlap / 2
                relative = (b["vx"] - a["vx"]) * nx + (b["vy"] - a["vy"]) * ny
                if relative < 0:
                    a["vx"] += relative * nx
                    a["vy"] += relative * ny
                    b["vx"] -= relative * nx
                    b["vy"] -= relative * ny
                    moving = True
        if not moving:
            break

    if cue_potted:
        cue["potted"] = False
        cue["x"] = 30.0
        cue["y"] = 50.0
    clean = [
        {
            "id": int(b["id"]),
            "x": round(float(b["x"]), 2),
            "y": round(float(b["y"]), 2),
            "potted": bool(b["potted"]),
        }
        for b in balls
    ]
    new_state = dict(state)
    new_state["balls"] = clean
    new_state["shots"] = int(state.get("shots", 0)) + 1
    new_state["foul"] = cue_potted or (not potted and not cue_potted)
    new_state["last"] = (
        "faute"
        if cue_potted
        else (
            f"{len(potted)} bille(s) empochee(s)" if potted else "pas de bille"
        )
    )
    return new_state, potted, cue_potted


def billard_group_of(ball_id: int) -> str:
    if ball_id == 8:
        return "eight"
    return "solids" if 1 <= ball_id <= 7 else "stripes"
