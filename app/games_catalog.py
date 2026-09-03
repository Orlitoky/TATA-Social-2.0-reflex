"""Static games catalog, LOTO tiers and shared dark-hall vocabularies.

Coins referenced here are TATA Coins: internal virtual points only. They can
never be purchased, deposited, withdrawn or converted to money.
"""

from __future__ import annotations

CATALOG: list[dict[str, str | int]] = [
    {
        "slug": "loto",
        "name": "LOTO",
        "description": (
            "Loto français 90 boules. Cartons 9x3, tirages minutés, "
            "Quine, Double Quine et Carton plein."
        ),
        "category": "tirage",
        "min_players": 1,
        "max_players": 30,
        "default_entry_coins": 50,
        "tag": "6 niveaux",
        "medallion": "dices",
    },
    {
        "slug": "domino",
        "name": "DOMINO",
        "description": (
            "Domino double-six, objectif Maty 50 a 120, variantes "
            "Sans Double-Six et Un sur Blanc."
        ),
        "category": "tuiles",
        "min_players": 2,
        "max_players": 3,
        "default_entry_coins": 100,
        "tag": "Maty",
        "medallion": "grip",
    },
    {
        "slug": "ludo",
        "name": "LUDO",
        "description": (
            "Plateau quatre couleurs, cases sures, des animes et captures."
        ),
        "category": "plateau",
        "min_players": 2,
        "max_players": 4,
        "default_entry_coins": 100,
        "tag": "4 couleurs",
        "medallion": "dice-5",
    },
    {
        "slug": "faritany",
        "name": "FARITANY",
        "description": (
            "Reseau en diamant inspire du Fanorona: deplacements adjacents, "
            "captures par approche, 15 secondes par tour."
        ),
        "category": "strategie",
        "min_players": 2,
        "max_players": 2,
        "default_entry_coins": 150,
        "tag": "15s / tour",
        "medallion": "gem",
    },
    {
        "slug": "points",
        "name": "JEUX DE POINT",
        "description": (
            "Pipopipette: reliez les points, fermez les boites et rejouez."
        ),
        "category": "papier",
        "min_players": 2,
        "max_players": 2,
        "default_entry_coins": 50,
        "tag": "Boites",
        "medallion": "grid-3x3",
    },
    {
        "slug": "rami",
        "name": "RAMI",
        "description": (
            "52 cartes, pioche ou defausse, combinaisons de meme rang ou "
            "suites de meme couleur."
        ),
        "category": "cartes",
        "min_players": 2,
        "max_players": 4,
        "default_entry_coins": 150,
        "tag": "52 cartes",
        "medallion": "spade",
    },
    {
        "slug": "tri",
        "name": "TRI",
        "description": (
            "Variante malgache de jeu de defausse a 32 cartes: posez la meme "
            "couleur ou le meme rang, sinon piochez."
        ),
        "category": "cartes",
        "min_players": 2,
        "max_players": 4,
        "default_entry_coins": 100,
        "tag": "32 cartes",
        "medallion": "club",
    },
    {
        "slug": "billard",
        "name": "BILLARD",
        "description": (
            "Billard 1v1 vue de dessus, visee angle/puissance et simulation "
            "de tir calculee par le serveur."
        ),
        "category": "adresse",
        "min_players": 2,
        "max_players": 2,
        "default_entry_coins": 200,
        "tag": "1v1",
        "medallion": "circle-dot",
    },
]

LOTO_TIERS: list[dict[str, str | int]] = [
    {
        "key": "bronze_lite",
        "label": "Bronze Lite",
        "card_price": 25,
        "max_cards": 2,
        "accent": "amber",
    },
    {
        "key": "bronze_club",
        "label": "Bronze Club",
        "card_price": 50,
        "max_cards": 3,
        "accent": "amber",
    },
    {
        "key": "silver_club",
        "label": "Silver Club",
        "card_price": 100,
        "max_cards": 5,
        "accent": "slate",
    },
    {
        "key": "gold_club",
        "label": "Gold Club",
        "card_price": 250,
        "max_cards": 6,
        "accent": "gold",
    },
    {
        "key": "platinum_club",
        "label": "Platinum Club",
        "card_price": 500,
        "max_cards": 8,
        "accent": "cyan",
    },
    {
        "key": "diamond_club",
        "label": "Diamond Club",
        "card_price": 1000,
        "max_cards": 10,
        "accent": "emerald",
    },
]

MATY_TARGETS: list[int] = [50, 80, 100, 120]
LUDO_COLORS: list[str] = ["red", "green", "yellow", "blue"]
LANGUAGES: list[dict[str, str]] = [
    {"value": "en", "label": "English"},
    {"value": "fr", "label": "Français"},
    {"value": "mg", "label": "Malagasy"},
    {"value": "ar", "label": "العربية"},
    {"value": "hi", "label": "हिन्दी"},
    {"value": "zh", "label": "中文"},
    {"value": "es", "label": "Español"},
    {"value": "pt", "label": "Português"},
]
GAME_REACTIONS: list[dict[str, str]] = [
    {"emoji": "🔥", "label": "Feu", "group": "emoji"},
    {"emoji": "😂", "label": "Rire", "group": "emoji"},
    {"emoji": "😮", "label": "Wow", "group": "emoji"},
    {"emoji": "😭", "label": "Perdu", "group": "emoji"},
    {"emoji": "👏", "label": "Bravo", "group": "geste"},
    {"emoji": "🤝", "label": "Fair-play", "group": "geste"},
    {"emoji": "👊", "label": "Allez", "group": "geste"},
    {"emoji": "🙏", "label": "Merci", "group": "geste"},
]


def tier_by_key(key: str) -> dict[str, str | int]:
    for tier in LOTO_TIERS:
        if tier["key"] == key:
            return tier
    return LOTO_TIERS[0]


def game_by_slug(slug: str) -> dict[str, str | int]:
    for game in CATALOG:
        if game["slug"] == slug:
            return game
    return CATALOG[0]
