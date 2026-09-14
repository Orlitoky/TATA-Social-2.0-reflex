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
            "Loto 90 boules. Cartons 3x9 de 15 numeros, tirages "
            "automatiques, Mandry 1, Mandry 2 et Aoka."
        ),
        "category": "tirage",
        "min_players": 1,
        "max_players": 30,
        "default_entry_coins": 200,
        "tag": "4 paliers",
        "medallion": "dices",
    },
    {
        "slug": "domino",
        "name": "DOMINO",
        "description": (
            "Domino double-six, 7 tuiles par joueur, objectif Maty 50 a "
            "120, variantes Sans Double-Six et Un sur Blanc."
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

# Canonical allowlist of games visible on the bright /games discovery page.
# Legacy entries stay in the database and remain playable via their own
# routes: they are only hidden from discovery.
VISIBLE_SLUGS: list[str] = ["domino", "ludo", "loto"]

# Original TATA cover artwork + compact discovery metadata.
DISCOVERY: dict[str, dict[str, str | int | bool]] = {
    "domino": {
        "cover": "/domino_original_tata.png",
        "subtitle": "Tuiles double-six, Maty 50 a 120",
        "mode": "Multijoueur 2-3",
        "category_label": "Tuiles",
        "accent": "sky",
        "featured": True,
        "order": 0,
    },
    "ludo": {
        "cover": "/ludo_game_board.png",
        "subtitle": "Plateau quatre couleurs, cases sures",
        "mode": "Multijoueur 2-4",
        "category_label": "Plateau",
        "accent": "cyan",
        "featured": False,
        "order": 1,
    },
    "loto": {
        "cover": "/loto_game_original.png",
        "subtitle": "Cartons 3x9, Mandry 1, Mandry 2 et Aoka",
        "mode": "Tirage minute",
        "category_label": "Tirage",
        "accent": "navy",
        "featured": False,
        "order": 2,
    },
}

DISCOVERY_CATEGORIES: list[dict[str, str]] = [
    {"value": "tous", "label": "Tous"},
    {"value": "plateau", "label": "Plateau"},
    {"value": "tuiles", "label": "Tuiles"},
    {"value": "tirage", "label": "Tirage"},
]


def discovery_meta(slug: str) -> dict[str, str | int | bool]:
    return DISCOVERY.get(
        slug,
        {
            "cover": "/placeholder.svg",
            "subtitle": "",
            "mode": "Multijoueur",
            "category_label": "Jeu",
            "accent": "sky",
            "featured": False,
            "order": 99,
        },
    )


# Exactly four canonical LOTO tiers. The "Ar" suffix is an in-game tier
# denomination only: the debited value is an internal TATA point amount.
LOTO_MAX_CARDS: int = 5
LOTO_MIN_CARDS: int = 1

LOTO_TIER_NOTICE: str = (
    "Denomination de palier en jeu uniquement: les libelles en Ar nomment "
    "les paliers TATA et sont debites en points internes. Aucun depot, "
    "aucun retrait, aucune valeur monetaire, aucune conversion."
)

LOTO_TIERS: list[dict[str, str | int]] = [
    {
        "key": "bronze",
        "label": "Bronze 200 Ar",
        "card_price": 200,
        "max_cards": LOTO_MAX_CARDS,
        "accent": "amber",
    },
    {
        "key": "standard",
        "label": "Standard 500 Ar",
        "card_price": 500,
        "max_cards": LOTO_MAX_CARDS,
        "accent": "sky",
    },
    {
        "key": "premium",
        "label": "Premium 1000 Ar",
        "card_price": 1000,
        "max_cards": LOTO_MAX_CARDS,
        "accent": "cyan",
    },
    {
        "key": "vip",
        "label": "VIP 1500 Ar",
        "card_price": 1500,
        "max_cards": LOTO_MAX_CARDS,
        "accent": "gold",
    },
]

# Legacy persisted tier keys keep working without a data migration.
LEGACY_TIER_ALIASES: dict[str, str] = {
    "bronze_lite": "bronze",
    "bronze_club": "bronze",
    "silver_club": "standard",
    "gold_club": "premium",
    "platinum_club": "premium",
    "diamond_club": "vip",
}

# Persisted claim columns are unchanged; only the display names are renamed.
LOTO_CLAIM_LABELS: dict[str, str] = {
    "quine": "Mandry 1",
    "double_quine": "Mandry 2",
    "full_house": "Aoka",
}


def loto_claim_label(key: str) -> str:
    return LOTO_CLAIM_LABELS.get(key, key)


# ---------------------------------------------------------------------------
# Per-game detail metadata for the bright /games/[game_slug] experience.
# Every rules/how-to line below describes the engine as implemented today.
# ---------------------------------------------------------------------------

GAME_DETAILS: dict[str, dict[str, str]] = {
    "domino": {
        "cover": "/domino_original_tata.png",
        "mode": "Multijoueur 2-3 joueurs",
        "player_range": "2 a 3 joueurs",
        "overview": (
            "Domino double-six autoritatif cote serveur: 7 tuiles par "
            "joueur a 2 comme a 3, chaque pose est verifiee, la pioche et "
            "les passes sont gardees, et la manche se termine sur une main "
            "vide ou un blocage."
        ),
        "stake": (
            "Mise par defaut 100 points internes TATA, ajoutee au pot de la "
            "salle. Aucun achat, aucun depot, aucun retrait, aucune valeur "
            "monetaire."
        ),
    },
    "ludo": {
        "cover": "/ludo_game_board.png",
        "mode": "Multijoueur 2-4 joueurs",
        "player_range": "2 a 4 joueurs",
        "overview": (
            "Plateau quatre couleurs, quatre pions par joueur: un seul "
            "lancer de de par tour, sortie de base sur un 6, cases sures "
            "protegees, captures et arrivee exacte calculees par le "
            "serveur. La victoire demande les quatre pions a la maison."
        ),
        "stake": (
            "Mise par defaut 100 points internes TATA. Les points sont "
            "virtuels: aucun achat, aucun depot, aucun retrait."
        ),
    },
    "loto": {
        "cover": "/loto_game_original.png",
        "mode": "Tirage minute multijoueur",
        "player_range": "2 a 30 joueurs",
        "overview": (
            "Loto 90 boules avec cartons officiels 3x9 de 15 numeros, 1 a "
            "5 cartons par joueur, tirages uniques automatiques, marquage "
            "et validation des annonces Mandry 1, Mandry 2 et Aoka "
            "calcules par le serveur."
        ),
        "stake": (
            "Palier du carton: Bronze 200 Ar, Standard 500 Ar, Premium "
            "1000 Ar ou VIP 1500 Ar, debite en points internes TATA. "
            "Aucun achat, aucun depot, aucun retrait, aucune conversion."
        ),
    },
}

GAME_RULES: dict[str, list[str]] = {
    "domino": [
        "Jeu double-six: 28 tuiles de 0|0 a 6|6. L'option Sans Double-Six "
        "retire la tuile 6|6 du jeu.",
        "Salle configuree pour 2 ou 3 joueurs, choisis a la creation.",
        "Distribution standard: exactement 7 tuiles par joueur, a 2 comme a "
        "3 joueurs, dans tous les modes; les tuiles restantes forment la "
        "pioche.",
        "Le plus fort double ouvre la manche; sans double, la tuile de plus "
        "haute somme part, les egalites etant tranchees par le siege.",
        "Une tuile ne se pose que si l'un de ses chiffres correspond a "
        "l'extremite gauche ou droite de la chaine.",
        "Il faut piocher tant que la pioche n'est pas vide: passer est "
        "refuse si une pose est possible ou si la pioche contient encore "
        "une tuile.",
        "Objectif Maty configurable: 50, 80, 100, 120 ou score libre de 20 "
        "a 500 points.",
        "Score de manche: somme des points (pips) restants dans les mains "
        "adverses, ajoutee au total du gagnant.",
        "Manche bloquee (tous les joueurs passent): le plus petit total de "
        "points en main remporte la manche.",
        "Option Un sur Blanc: poser la tuile 1|0 accorde un tour "
        "supplementaire a son auteur.",
    ],
    "ludo": [
        "2 a 4 joueurs, une couleur attribuee par siege: rouge, vert, jaune "
        "puis bleu.",
        "Un seul lancer de de par tour: relancer avant de bouger est refuse.",
        "Un 6 est obligatoire pour faire sortir un pion de sa base.",
        "Un pion avance exactement de la valeur du de et ne peut pas "
        "depasser la position 58, qui est la maison.",
        "Les cases sures du parcours protegent totalement les pions qui s'y "
        "trouvent.",
        "Arriver sur un pion adverse hors case sure le renvoie a sa base.",
        "Chaque joueur dispose de quatre pions: la partie est gagnee "
        "lorsque les quatre pions atteignent exactement la maison.",
        "Un 6 accorde un tour supplementaire; si aucun pion n'a de coup "
        "legal, le tour passe automatiquement au joueur suivant.",
    ],
    "loto": [
        "Cartons officiels 90 boules: grille 3x9 contenant exactement 15 "
        "numeros, 5 par ligne, chaque colonne couvrant une dizaine.",
        "Chaque joueur peut detenir de 1 a 5 cartons valides, quel que "
        "soit le palier de la salle.",
        "Quatre paliers uniquement: Bronze 200 Ar, Standard 500 Ar, "
        "Premium 1000 Ar et VIP 1500 Ar. Ces libelles sont des "
        "denominations de palier en jeu, debitees en points internes: "
        "aucun depot, aucun retrait, aucune valeur monetaire, aucune "
        "conversion.",
        "Tirages automatiques: chaque boule tiree est unique, sans doublon, "
        "jusqu'a epuisement des 90 boules.",
        "Le marquage des numeros et la progression par ligne sont calcules "
        "automatiquement par le serveur.",
        "Annonces: Mandry 1 (une ligne complete), Mandry 2 (deux lignes "
        "completes) et Aoka (les 15 numeros du carton).",
        "Repartition du pot net: 20% Mandry 1, 30% Mandry 2, 50% Aoka.",
        "Le tirage s'arrete des que Aoka est remporte ou que les 90 "
        "boules sont epuisees.",
    ],
}

GAME_HOWTO: dict[str, list[str]] = {
    "domino": [
        "Lancez Quick Play, creez une salle ou rejoignez une salle ouverte "
        "avec son code.",
        "Dans la salle d'attente, attendez que tous les sieges configures "
        "soient occupes puis que l'hote lance la partie.",
        "A votre tour, touchez une tuile jouable: le serveur choisit le "
        "cote valide, ou vous indiquez gauche/droite.",
        "Seules les tuiles jouables sont actives: les cotes gauche et "
        "droite invalides sont desactives, jamais refuses apres coup.",
        "Aucune tuile ne colle ? Piochez tant que la pioche contient des "
        "tuiles.",
        "Pioche vide et aucune pose possible: passez votre tour.",
        "La manche se termine des qu'une main est vide ou que tout le monde "
        "passe; les points des adversaires sont ajoutes au gagnant.",
        "Les manches se rejouent jusqu'a l'objectif Maty de la salle.",
    ],
    "ludo": [
        "Rejoignez ou creez une salle 2 a 4 joueurs et attendez le "
        "lancement par l'hote.",
        "A votre tour, lancez le de une seule fois.",
        "Sur un 6, vous pouvez sortir un pion de la base; sinon, choisissez "
        "un pion deja sur le parcours.",
        "Touchez un pion mis en evidence: seuls les pions dont le "
        "deplacement exact reste valide sont proposes.",
        "Visez les cases sures pour proteger vos pions et capturez les "
        "adversaires hors de ces cases.",
        "La partie est gagnee des que vos quatre pions atteignent "
        "exactement la maison.",
    ],
    "loto": [
        "Choisissez une salle selon son palier (Bronze 200 Ar, Standard "
        "500 Ar, Premium 1000 Ar, VIP 1500 Ar) puis rejoignez-la avec vos "
        "points internes.",
        "Prenez de 1 a 5 cartons: ils sont generes et valides par le serveur.",
        "Suivez les tirages: chaque boule sortie est marquee "
        "automatiquement sur vos cartons.",
        "Surveillez la progression par ligne affichee pour chaque carton.",
        "Mandry 1, Mandry 2 et Aoka sont detectes et payes "
        "automatiquement par le serveur: aucun bouton d'annonce n'est "
        "necessaire.",
        "Le tirage avance seul a l'expiration du minuteur et s'arrete sur "
        "Aoka ou apres la 90e boule.",
    ],
}

# Ludo is fixed at the standard four pawns per player: no configurable goal.
LUDO_GOAL_PAWNS: int = 4


def detail_meta(slug: str) -> dict[str, str]:
    return GAME_DETAILS.get(
        slug,
        {
            "cover": "/placeholder.svg",
            "mode": "Multijoueur",
            "player_range": "",
            "overview": "",
            "stake": "",
        },
    )


def detail_rules(slug: str) -> list[str]:
    return GAME_RULES.get(slug, [])


def detail_howto(slug: str) -> list[str]:
    return GAME_HOWTO.get(slug, [])


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
    resolved = LEGACY_TIER_ALIASES.get(key, key)
    for tier in LOTO_TIERS:
        if tier["key"] == resolved:
            return tier
    return LOTO_TIERS[0]


def game_by_slug(slug: str) -> dict[str, str | int]:
    for game in CATALOG:
        if game["slug"] == slug:
            return game
    return CATALOG[0]
