"""Games hub: idempotent catalog/room seeding, listings and room creation."""

from __future__ import annotations

import json
import logging
import random
import secrets
from typing import Any, TypedDict

import reflex as rx
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError

from app import game_engine as engine

from app.games_catalog import (
    CATALOG,
    DISCOVERY_CATEGORIES,
    LOTO_TIERS,
    MATY_TARGETS,
    VISIBLE_SLUGS,
    detail_howto,
    detail_meta,
    detail_rules,
    discovery_meta,
    game_by_slug,
)
from app.security import hash_password
from app.states.auth_state import AuthState


class GameCard(TypedDict):
    slug: str
    name: str
    description: str
    category: str
    tag: str
    medallion: str
    min_players: int
    max_players: int
    open_rooms: int
    live_players: int
    cover: str
    subtitle: str
    mode: str
    category_label: str
    accent: str
    featured: bool
    player_range: str
    live_label: str
    is_live: bool
    search_blob: str


class RoomRow(TypedDict):
    id: int
    code: str
    name: str
    slug: str
    game_name: str
    status: str
    status_label: str
    is_private: bool
    player_count: int
    max_players: int
    host_name: str
    host_online: bool
    tier_label: str
    joined: bool
    full: bool


class GamesState(rx.State):
    loading: bool = True
    error: str = ""
    cards: list[GameCard] = []
    rooms: list[RoomRow] = []
    my_rooms: list[RoomRow] = []
    active_slug: str = ""
    create_open: bool = False
    join_code: str = ""
    referral_open: bool = False
    search_text: str = ""
    category: str = "tous"
    categories: list[dict[str, str]] = DISCOVERY_CATEGORIES

    # ---- bright game detail page ---------------------------------------
    slug_valid: bool = True
    panel_tab: str = "rules"
    status_filter: str = "all"
    secret_room_id: int = 0
    secret_room_name: str = ""
    room_secret: str = ""
    quick_playing: bool = False

    # ---- one-click authenticated solo practice -------------------------
    solo_busy: bool = False
    solo_slug: str = ""
    solo_error: str = ""
    status_filters: list[dict[str, str]] = [
        {"value": "all", "label": "Toutes"},
        {"value": "open", "label": "Ouvertes"},
        {"value": "waiting", "label": "Attente"},
        {"value": "active", "label": "En cours"},
    ]

    # ---- generic (Ludo / Loto) creation sheet ---------------------------
    create_sheet_open: bool = False
    create_busy: bool = False
    create_error: str = ""
    gen_name: str = ""
    gen_private: bool = False
    gen_secret: str = ""
    gen_players: int = 4
    gen_tier: str = "bronze"
    gen_entry: str = "100"

    # ---- Domino "Creer une partie" bottom sheet draft -------------------
    domino_sheet_open: bool = False
    domino_creating: bool = False
    draft_mode: str = "classic"
    draft_score_choice: str = "50"
    draft_custom_score: str = ""
    draft_players: int = 2
    draft_no_double_six: bool = False
    draft_one_on_blank: bool = False
    draft_fill_with_bots: bool = True
    draft_error: str = ""

    domino_modes: list[dict[str, str]] = [
        {
            "key": "classic",
            "label": "Classique",
            "hint": "standard",
            "icon": "grip",
        },
        {
            "key": "rush_auto",
            "label": "Rush Auto",
            "hint": "coups auto",
            "icon": "zap",
        },
        {
            "key": "rush_manual",
            "label": "Rush Manuel",
            "hint": "tu choisis",
            "icon": "hand",
        },
        {
            "key": "draw",
            "label": "Pioche",
            "hint": "7 tuiles, pioche large",
            "icon": "layers",
        },
    ]
    domino_scores: list[dict[str, str]] = [
        {"key": "50", "label": "50"},
        {"key": "80", "label": "80"},
        {"key": "100", "label": "100"},
        {"key": "120", "label": "120"},
        {"key": "custom", "label": "Libre"},
    ]
    domino_rules: list[dict[str, str]] = [
        {
            "key": "no_double_six",
            "label": "Sans Double-Six",
            "hint": "Le 6|6 est retire du jeu",
            "icon": "dice-6",
        },
        {
            "key": "one_on_blank",
            "label": "Un sur Blanc",
            "hint": "Le 1 peut se poser sur un blanc",
            "icon": "circle-dashed",
        },
        {
            "key": "fill_with_bots",
            "label": "Completer avec des bots",
            "hint": "Sieges vides remplis par le serveur",
            "icon": "bot",
        },
    ]

    @rx.var
    def draft_is_custom_score(self) -> bool:
        return self.draft_score_choice == "custom"

    @rx.var
    def draft_score_summary(self) -> str:
        if self.draft_score_choice == "custom":
            return (
                f"{self.draft_custom_score} points"
                if self.draft_custom_score
                else "Score libre"
            )
        return f"{self.draft_score_choice} points"

    tier_options: list[dict[str, str]] = [
        {
            "key": str(tier["key"]),
            "label": str(tier["label"]),
            "max": str(tier["max_cards"]),
        }
        for tier in LOTO_TIERS
    ]
    maty_targets: list[int] = MATY_TARGETS

    @rx.var
    def active_game_name(self) -> str:
        if not self.active_slug:
            return "Jeux"
        return str(game_by_slug(self.active_slug)["name"])

    @rx.var
    def active_game_description(self) -> str:
        if not self.active_slug:
            return ""
        return str(game_by_slug(self.active_slug)["description"])

    @rx.var
    def detail_cover(self) -> str:
        return str(detail_meta(self.active_slug)["cover"])

    @rx.var
    def detail_mode(self) -> str:
        return str(detail_meta(self.active_slug)["mode"])

    @rx.var
    def detail_player_range(self) -> str:
        return str(detail_meta(self.active_slug)["player_range"])

    @rx.var
    def detail_overview(self) -> str:
        return str(detail_meta(self.active_slug)["overview"])

    @rx.var
    def detail_rules_list(self) -> list[str]:
        return detail_rules(self.active_slug)

    @rx.var
    def detail_howto_list(self) -> list[str]:
        return detail_howto(self.active_slug)

    @rx.var
    def showing_rules(self) -> bool:
        return self.panel_tab == "rules"

    @rx.var
    def visible_rooms(self) -> list[RoomRow]:
        if self.status_filter == "all":
            return self.rooms
        if self.status_filter == "active":
            return [
                r
                for r in self.rooms
                if r["status"] in ("active", "in_progress")
            ]
        return [r for r in self.rooms if r["status"] == self.status_filter]

    @rx.var
    def open_room_count(self) -> int:
        return len(
            [
                r
                for r in self.rooms
                if r["status"] in ("open", "waiting") and not r["full"]
            ]
        )

    @rx.var
    def live_player_count(self) -> int:
        return sum(r["player_count"] for r in self.rooms)

    @rx.var
    def create_player_options(self) -> list[int]:
        if self.active_slug == "ludo":
            return [2, 3, 4]
        if self.active_slug == "loto":
            return [2, 4, 6, 8, 10, 12]
        return [2, 3]

    @rx.var
    def is_loto(self) -> bool:
        return self.active_slug == "loto"

    @rx.var
    def is_domino(self) -> bool:
        return self.active_slug == "domino"

    # ------------------------------------------------ discovery filtering
    @rx.event
    def set_search_text(self, value: str):
        self.search_text = value[:60]

    @rx.event
    def clear_search(self):
        self.search_text = ""

    @rx.event
    def set_category(self, value: str):
        allowed = {c["value"] for c in DISCOVERY_CATEGORIES}
        if value in allowed:
            self.category = value

    def _matches(self, card: GameCard) -> bool:
        query = self.search_text.strip().lower()
        if query and query not in card["search_blob"]:
            return False
        if self.category != "tous" and card["category"] != self.category:
            return False
        return True

    @rx.var
    def filtered_cards(self) -> list[GameCard]:
        return [c for c in self.cards if self._matches(c)]

    @rx.var
    def has_results(self) -> bool:
        return len(self.filtered_cards) > 0

    @rx.var
    def is_filtering(self) -> bool:
        return bool(self.search_text.strip()) or self.category != "tous"

    @rx.var
    def featured_card(self) -> list[GameCard]:
        """Single-item list so the UI can foreach the editorial lead."""
        for card in self.cards:
            if card["featured"]:
                return [card]
        return self.cards[:1]

    @rx.var
    def supporting_cards(self) -> list[GameCard]:
        lead = {c["slug"] for c in self.featured_card}
        return [c for c in self.cards if c["slug"] not in lead]

    @rx.var
    def popular_cards(self) -> list[GameCard]:
        return sorted(
            self.cards,
            key=lambda c: (
                -c["live_players"],
                -c["open_rooms"],
                c["name"],
            ),
        )

    @rx.var
    def total_open_rooms(self) -> int:
        return sum(c["open_rooms"] for c in self.cards)

    @rx.var
    def total_live_players(self) -> int:
        return sum(c["live_players"] for c in self.cards)

    @rx.var
    def referral_code(self) -> str:
        return f"TATA-{self.router.session.client_token[:6].upper()}"

    # ---------------------------------------------------------------- seeding
    async def _seed(
        self, asession, me_id: int, slugs: list[str] | None = None
    ) -> None:
        allow = set(slugs) if slugs else None
        for entry in CATALOG:
            if allow is not None and str(entry["slug"]) not in allow:
                continue
            await asession.execute(
                text(
                    """
                    INSERT INTO game (slug, name, description, category,
                        cover_key, min_players, max_players,
                        default_entry_coins, is_active, created_at, updated_at)
                    VALUES (CAST(:slug AS VARCHAR), CAST(:name AS VARCHAR),
                            CAST(:description AS TEXT),
                            CAST(:category AS VARCHAR), '',
                            CAST(:min_players AS INTEGER),
                            CAST(:max_players AS INTEGER),
                            CAST(:entry AS INTEGER), true, NOW(), NOW())
                    ON CONFLICT (slug) DO NOTHING
                    """
                ),
                {
                    "slug": entry["slug"],
                    "name": entry["name"],
                    "description": entry["description"],
                    "category": entry["category"],
                    "min_players": entry["min_players"],
                    "max_players": entry["max_players"],
                    "entry": 0,
                },
            )
        rows = (
            await asession.execute(
                text("SELECT id, slug, max_players FROM game")
            )
        ).all()
        host_row = (
            await asession.execute(
                text(
                    "SELECT id FROM account WHERE id <> :me AND "
                    "status = 'active' ORDER BY id LIMIT 1"
                ),
                {"me": me_id},
            )
        ).first()
        host_id = int(host_row[0]) if host_row is not None else me_id
        for game_id, slug, max_players in rows:
            if allow is not None and str(slug) not in allow:
                continue
            existing = (
                await asession.execute(
                    text(
                        "SELECT COUNT(*) FROM game_room WHERE game_id = :g "
                        "AND status IN ('open', 'waiting')"
                    ),
                    {"g": int(game_id)},
                )
            ).first()
            if int(existing[0] or 0) >= 2:
                continue
            catalog = game_by_slug(str(slug))
            for index in range(2):
                rules: dict[str, Any] = {}
                entry = 0
                if slug == "loto":
                    tier = LOTO_TIERS[index]
                    rules = {"tier": tier["key"], "draw_seconds": 12}
                    entry = 0
                elif slug == "domino":
                    rules = {
                        "maty": MATY_TARGETS[index],
                        "no_double_six": False,
                        "one_on_blank": index == 1,
                    }
                elif slug == "ludo":
                    rules = {"goal_pawns": 4}
                elif slug in ("faritany", "points"):
                    rules = {"turn_seconds": 15}
                await asession.execute(
                    text(
                        """
                        INSERT INTO game_room (game_id, host_id, code, name,
                            status, is_private, password_hash, max_players,
                            player_count, entry_coins, rules_json, state_json,
                            round_number, pot_coins, state_version,
                            created_at, updated_at)
                        VALUES (:g, :h, :code, :name, 'open', false, '',
                            :max_players, 0, :entry, :rules, '{}', 0, 0, 0,
                            NOW(), NOW())
                        """
                    ),
                    {
                        "g": int(game_id),
                        "h": host_id,
                        "code": secrets.token_hex(3).upper(),
                        "name": f"{catalog['name']} salle {index + 1}",
                        "max_players": int(max_players),
                        "entry": entry,
                        "rules": json.dumps(rules),
                    },
                )

    # ----------------------------------------------------------------- loads
    @rx.event
    async def load_hub(self):
        auth = await self.get_state(AuthState)
        if not auth.account_id:
            return
        self.loading = True
        self.error = ""
        self.active_slug = ""
        async with rx.asession() as asession:
            await self._seed(asession, auth.account_id, VISIBLE_SLUGS)
            await asession.commit()
            rows = (
                await asession.execute(
                    text(
                        """
                        SELECT g.slug, g.name, g.description, g.category,
                               g.min_players, g.max_players,
                               g.default_entry_coins,
                               COALESCE(SUM(CASE WHEN r.status IN
                                   ('open','waiting') THEN 1 ELSE 0 END), 0),
                               COALESCE(SUM(r.player_count), 0)
                        FROM game g
                        LEFT JOIN game_room r ON r.game_id = g.id
                             AND r.status <> 'closed'
                        WHERE g.is_active = true
                          AND g.slug IN ('domino', 'ludo', 'loto')
                        GROUP BY g.id, g.slug, g.name, g.description,
                                 g.category, g.min_players, g.max_players,
                                 g.default_entry_coins
                        ORDER BY g.id
                        """
                    )
                )
            ).all()
        catalog_index = {str(c["slug"]): c for c in CATALOG}
        cards: list[GameCard] = []
        for r in rows:
            slug = str(r[0])
            if slug not in VISIBLE_SLUGS:
                continue
            meta = discovery_meta(slug)
            open_rooms = int(r[7] or 0)
            live_players = int(r[8] or 0)
            name = str(r[1])
            description = str(r[2])
            mode = str(meta["mode"])
            cards.append(
                {
                    "slug": slug,
                    "name": name,
                    "description": description,
                    "category": str(r[3]),
                    "tag": str(catalog_index.get(slug, {}).get("tag", "Live")),
                    "medallion": str(
                        catalog_index.get(slug, {}).get("medallion", "gem")
                    ),
                    "min_players": int(r[4]),
                    "max_players": int(r[5]),
                    "open_rooms": open_rooms,
                    "live_players": live_players,
                    "cover": str(meta["cover"]),
                    "subtitle": str(meta["subtitle"]),
                    "mode": mode,
                    "category_label": str(meta["category_label"]),
                    "accent": str(meta["accent"]),
                    "featured": bool(meta["featured"]),
                    "player_range": f"{int(r[4])}-{int(r[5])} joueurs",
                    "live_label": (
                        f"{live_players} en direct"
                        if live_players > 0
                        else (
                            f"{open_rooms} salle(s) ouverte(s)"
                            if open_rooms > 0
                            else "Aucune salle ouverte"
                        )
                    ),
                    "is_live": live_players > 0 or open_rooms > 0,
                    "search_blob": (
                        f"{name} {description} {mode} "
                        f"{meta['subtitle']} {meta['category_label']}"
                    ).lower(),
                }
            )
        cards.sort(key=lambda c: int(discovery_meta(c["slug"])["order"]))
        self.cards = cards
        await self._load_my_rooms(auth.account_id, True)
        self.loading = False

    async def _load_my_rooms(
        self, account_id: int, only_visible: bool = False
    ) -> None:
        slug_clause = (
            " AND g.slug IN ('domino', 'ludo', 'loto')" if only_visible else ""
        )
        async with rx.asession() as asession:
            rows = (
                await asession.execute(
                    text(
                        """
                        SELECT r.id, r.code, r.name, g.slug, g.name, r.status,
                               r.is_private, r.player_count, r.max_players,
                               r.entry_coins, r.pot_coins,
                               COALESCE(p.display_name, a.username),
                               a.is_online, r.rules_json
                        FROM game_room_member m
                        JOIN game_room r ON r.id = m.room_id
                        JOIN game g ON g.id = r.game_id
                        JOIN account a ON a.id = r.host_id
                        LEFT JOIN profile p ON p.account_id = a.id
                        WHERE m.account_id = :me AND m.left_at IS NULL
                          AND r.status <> 'closed'
                        """
                        + slug_clause
                        + """
                        ORDER BY r.updated_at DESC
                        LIMIT 12
                        """
                    ),
                    {"me": account_id},
                )
            ).all()
        self.my_rooms = [self._room_row(r, True) for r in rows]

    def _room_row(self, r, joined: bool) -> RoomRow:
        try:
            rules = json.loads(str(r[13]) or "{}")
        except ValueError:
            rules = {}
        tier_label = ""
        if rules.get("tier"):
            for tier in LOTO_TIERS:
                if tier["key"] == rules.get("tier"):
                    tier_label = str(tier["label"])
        elif rules.get("maty"):
            tier_label = f"Maty {rules['maty']}"
        status = str(r[5])
        labels = {
            "open": "Ouverte",
            "waiting": "Salle d'attente",
            "active": "En cours",
            "in_progress": "En cours",
            "finished": "Terminee",
            "closed": "Fermee",
        }
        return {
            "id": int(r[0]),
            "code": str(r[1]),
            "name": str(r[2]) or f"Salle {r[1]}",
            "slug": str(r[3]),
            "game_name": str(r[4]),
            "status": status,
            "status_label": labels.get(status, status),
            "is_private": bool(r[6]),
            "player_count": int(r[7] or 0),
            "max_players": int(r[8] or 0),
            "host_name": str(r[11]),
            "host_online": bool(r[12]),
            "tier_label": tier_label,
            "joined": joined,
            "full": int(r[7] or 0) >= int(r[8] or 0),
        }

    @rx.event
    async def load_lobby(self):
        auth = await self.get_state(AuthState)
        if not auth.account_id:
            return
        slug = str(self.router.page.params.get("game_slug", "")).lower()
        if slug not in VISIBLE_SLUGS:
            self.active_slug = ""
            self.slug_valid = False
            self.rooms = []
            self.loading = False
            self.error = "Ce jeu n'est pas disponible."
            return rx.redirect("/games")
        self.slug_valid = True
        self.active_slug = slug
        self.panel_tab = "rules"
        self.status_filter = "all"
        self.secret_room_id = 0
        self.room_secret = ""
        self.loading = True
        self.error = ""
        async with rx.asession() as asession:
            await self._seed(asession, auth.account_id)
            await asession.commit()
            rows = (
                await asession.execute(
                    text(
                        """
                        SELECT r.id, r.code, r.name, g.slug, g.name, r.status,
                               r.is_private, r.player_count, r.max_players,
                               r.entry_coins, r.pot_coins,
                               COALESCE(p.display_name, a.username),
                               a.is_online, r.rules_json,
                               (SELECT COUNT(*) FROM game_room_member m
                                WHERE m.room_id = r.id
                                  AND m.account_id = :me
                                  AND m.left_at IS NULL)
                        FROM game_room r
                        JOIN game g ON g.id = r.game_id
                        JOIN account a ON a.id = r.host_id
                        LEFT JOIN profile p ON p.account_id = a.id
                        WHERE g.slug = :slug AND r.status <> 'closed'
                          AND CAST(r.rules_json AS TEXT) NOT LIKE
                              '%solo_test%'
                        ORDER BY
                          CASE r.status WHEN 'open' THEN 0
                               WHEN 'waiting' THEN 1
                               WHEN 'active' THEN 2 ELSE 3 END,
                          r.updated_at DESC
                        LIMIT 40
                        """
                    ),
                    {"slug": slug, "me": auth.account_id},
                )
            ).all()
        self.rooms = [self._room_row(r, int(r[14] or 0) > 0) for r in rows]
        await self._load_my_rooms(auth.account_id)
        self.loading = False

    # --------------------------------------------------------------- actions
    @rx.event
    def toggle_create(self):
        self.create_open = not self.create_open
        self.error = ""

    # ------------------------------------------------- domino draft events
    def _reset_domino_draft(self) -> None:
        self.draft_mode = "classic"
        self.draft_score_choice = "50"
        self.draft_custom_score = ""
        self.draft_players = 2
        self.draft_no_double_six = False
        self.draft_one_on_blank = False
        self.draft_fill_with_bots = True
        self.draft_error = ""
        self.domino_creating = False

    @rx.event
    def open_domino_sheet(self):
        self._reset_domino_draft()
        self.error = ""
        self.domino_sheet_open = True

    @rx.event
    def cancel_domino_sheet(self):
        """Close without creating anything and fully reset the draft."""
        self.domino_sheet_open = False
        self._reset_domino_draft()

    @rx.event
    def set_draft_mode(self, key: str):
        if key in {"classic", "rush_auto", "rush_manual", "draw"}:
            self.draft_mode = key
            self.draft_error = ""

    @rx.event
    def set_draft_score_choice(self, key: str):
        self.draft_score_choice = key
        self.draft_error = ""
        if key != "custom":
            self.draft_custom_score = ""

    @rx.event
    def set_draft_custom_score(self, value: str):
        self.draft_custom_score = "".join(c for c in value if c.isdigit())[:3]
        self.draft_error = ""

    @rx.event
    def set_draft_players(self, count: int):
        if count in (2, 3):
            self.draft_players = count
            self.draft_error = ""

    @rx.event
    def toggle_draft_rule(self, key: str):
        if key == "no_double_six":
            self.draft_no_double_six = not self.draft_no_double_six
        elif key == "one_on_blank":
            self.draft_one_on_blank = not self.draft_one_on_blank
        elif key == "fill_with_bots":
            self.draft_fill_with_bots = not self.draft_fill_with_bots
        self.draft_error = ""

    @rx.var
    def draft_rule_values(self) -> dict[str, bool]:
        return {
            "no_double_six": self.draft_no_double_six,
            "one_on_blank": self.draft_one_on_blank,
            "fill_with_bots": self.draft_fill_with_bots,
        }

    def _resolve_draft_score(self) -> tuple[int, str]:
        """Return (target_score, error_message)."""
        if self.draft_score_choice == "custom":
            raw = self.draft_custom_score.strip()
            if not raw:
                return 0, "Entrez un score personnalise pour le mode Libre."
            if not raw.isdigit():
                return 0, "Le score doit contenir uniquement des chiffres."
            value = int(raw)
            if value < 20 or value > 500:
                return 0, "Le score libre doit etre compris entre 20 et 500."
            return value, ""
        return int(self.draft_score_choice), ""

    @rx.event
    async def create_domino_room(self):
        """Persist a waiting domino room + host membership in one transaction."""
        auth = await self.get_state(AuthState)
        if not auth.account_id:
            self.draft_error = "Connectez-vous pour creer une partie."
            yield rx.toast("Connectez-vous pour creer une partie.")
            return
        target_score, message = self._resolve_draft_score()
        if message:
            self.draft_error = message
            return
        if self.draft_players not in (2, 3):
            self.draft_error = "Choisissez 2 ou 3 joueurs."
            return
        if self.domino_creating:
            return
        self.domino_creating = True
        self.draft_error = ""
        yield

        catalog = game_by_slug("domino")
        rules = {
            "game_mode": self.draft_mode,
            "target_score": target_score,
            "custom_score": target_score
            if self.draft_score_choice == "custom"
            else None,
            "number_of_players": self.draft_players,
            "no_double_six": self.draft_no_double_six,
            "one_on_blank": self.draft_one_on_blank,
            "fill_with_bots": self.draft_fill_with_bots,
            "game_state": "waiting",
            "maty": target_score,
        }
        entry = 0
        room_id = 0
        try:
            async with rx.asession() as asession:
                game_row = (
                    await asession.execute(
                        text("SELECT id FROM game WHERE slug = 'domino'")
                    )
                ).first()
                if game_row is None:
                    self.domino_creating = False
                    self.draft_error = "Jeu Domino introuvable."
                    return
                for _ in range(8):
                    code = secrets.token_hex(4).upper()
                    taken = (
                        await asession.execute(
                            text(
                                "SELECT 1 FROM game_room WHERE code = :c "
                                "LIMIT 1"
                            ),
                            {"c": code},
                        )
                    ).first()
                    if taken is not None:
                        continue
                    inserted = (
                        await asession.execute(
                            text(
                                """
                                INSERT INTO game_room (game_id, host_id, code,
                                    name, status, is_private, password_hash,
                                    max_players, player_count, entry_coins,
                                    rules_json, state_json, round_number,
                                    pot_coins, state_version, created_at,
                                    updated_at)
                                VALUES (:g, :h, :code, :name, 'waiting',
                                    false, '', :max_players, 1, :entry,
                                    :rules, '{}', 0, 0, 0, NOW(), NOW())
                                RETURNING id
                                """
                            ),
                            {
                                "g": int(game_row[0]),
                                "h": auth.account_id,
                                "code": code,
                                "name": f"Domino de {auth.display_name}",
                                "max_players": self.draft_players,
                                "entry": entry,
                                "rules": json.dumps(rules),
                            },
                        )
                    ).first()
                    room_id = int(inserted[0])
                    break
                if not room_id:
                    await asession.rollback()
                    self.domino_creating = False
                    self.draft_error = (
                        "Impossible de generer un code de salle unique. "
                        "Reessayez."
                    )
                    return
                await asession.execute(
                    text(
                        """
                        INSERT INTO game_room_member (room_id, account_id,
                            seat, is_host, is_ready, score, result, joined_at)
                        VALUES (:r, :a, 0, true, false, 0, '', NOW())
                        """
                    ),
                    {"r": room_id, "a": auth.account_id},
                )
                await asession.execute(
                    text(
                        """
                        INSERT INTO game_room_event (room_id, account_id,
                            event_type, detail, created_at)
                        VALUES (:r, :a, 'join', :d, NOW())
                        """
                    ),
                    {
                        "r": room_id,
                        "a": auth.account_id,
                        "d": f"{auth.display_name} a cree la partie",
                    },
                )
                await asession.commit()
        except SQLAlchemyError as exc:
            logging.exception(f"Error: {exc}")
            self.domino_creating = False
            self.draft_error = (
                "La creation a echoue. Verifiez votre connexion et reessayez."
            )
            yield rx.toast("La creation de la partie a echoue.")
            return
        self.domino_sheet_open = False
        self._reset_domino_draft()
        yield rx.toast("Partie creee. Bienvenue dans la salle d'attente.")
        yield rx.redirect(f"/game/room/{room_id}")

    # ------------------------------------------------ detail page controls
    @rx.event
    def set_panel_tab(self, value: str):
        if value in ("rules", "howto"):
            self.panel_tab = value

    @rx.event
    def set_status_filter(self, value: str):
        if value in {f["value"] for f in self.status_filters}:
            self.status_filter = value

    @rx.event
    def open_secret_dialog(self, room_id: int, room_name: str):
        self.secret_room_id = room_id
        self.secret_room_name = room_name
        self.room_secret = ""
        self.error = ""

    @rx.event
    def close_secret_dialog(self):
        self.secret_room_id = 0
        self.room_secret = ""

    @rx.event
    def set_room_secret(self, value: str):
        self.room_secret = value.strip()[:40]

    @rx.event
    def submit_room_secret(self):
        if not self.room_secret:
            self.error = "Entrez le code d'acces de la salle privee."
            return rx.toast("Entrez le code d'acces.")
        room_id = self.secret_room_id
        secret = self.room_secret
        self.secret_room_id = 0
        self.room_secret = ""
        return GamesState.join_room(room_id, secret)

    @rx.event
    def copy_code(self, code: str):
        return [
            rx.set_clipboard(code),
            rx.toast(f"Code {code} copie.", duration=3000),
        ]

    # -------------------------------------------------------- quick play
    async def _insert_public_room(
        self, asession, slug: str, host_id: int, host_name: str
    ) -> int:
        catalog = game_by_slug(slug)
        game_row = (
            await asession.execute(
                text("SELECT id FROM game WHERE slug = :s"), {"s": slug}
            )
        ).first()
        if game_row is None:
            return 0
        rules: dict[str, Any] = {}
        entry = 0
        max_players = int(catalog["max_players"])
        if slug == "loto":
            tier = LOTO_TIERS[0]
            rules = {"tier": tier["key"], "draw_seconds": 12}
            entry = 0
            max_players = 8
        elif slug == "ludo":
            rules = {"goal_pawns": 4}
            max_players = 4
        elif slug == "domino":
            rules = {
                "game_mode": "classic",
                "target_score": 50,
                "maty": 50,
                "number_of_players": 2,
                "no_double_six": False,
                "one_on_blank": False,
                "fill_with_bots": False,
                "game_state": "waiting",
            }
            max_players = 2
        for _ in range(8):
            code = secrets.token_hex(3).upper()
            taken = (
                await asession.execute(
                    text("SELECT 1 FROM game_room WHERE code = :c LIMIT 1"),
                    {"c": code},
                )
            ).first()
            if taken is not None:
                continue
            inserted = (
                await asession.execute(
                    text(
                        """
                        INSERT INTO game_room (game_id, host_id, code, name,
                            status, is_private, password_hash, max_players,
                            player_count, entry_coins, rules_json, state_json,
                            round_number, pot_coins, state_version,
                            created_at, updated_at)
                        VALUES (:g, :h, :code, :name, 'waiting', false, '',
                            :max_players, 0, :entry, :rules, '{}', 0, 0, 0,
                            NOW(), NOW())
                        RETURNING id
                        """
                    ),
                    {
                        "g": int(game_row[0]),
                        "h": host_id,
                        "code": code,
                        "name": f"{catalog['name']} de {host_name}",
                        "max_players": max_players,
                        "entry": entry,
                        "rules": json.dumps(rules),
                    },
                )
            ).first()
            return int(inserted[0])
        return 0

    @rx.event
    async def quick_play(self):
        """Join the best joinable public room, or create one and join it."""
        auth = await self.get_state(AuthState)
        if not auth.account_id:
            return rx.redirect("/login")
        slug = self.active_slug
        if slug not in VISIBLE_SLUGS:
            return rx.toast("Ce jeu n'est pas disponible.")
        self.quick_playing = True
        self.error = ""
        room_id = 0
        try:
            async with rx.asession() as asession:
                row = (
                    await asession.execute(
                        text(
                            """
                            SELECT r.id
                            FROM game_room r
                            JOIN game g ON g.id = r.game_id
                            WHERE g.slug = :s
                              AND r.is_private = false
                              AND r.status IN ('open', 'waiting')
                              AND CAST(r.rules_json AS TEXT) NOT LIKE
                                  '%solo_test%'
                              AND r.player_count < r.max_players
                            ORDER BY
                              CASE r.status WHEN 'waiting' THEN 0 ELSE 1 END,
                              r.player_count DESC,
                              r.updated_at DESC
                            LIMIT 1
                            """
                        ),
                        {"s": slug},
                    )
                ).first()
                if row is not None:
                    room_id = int(row[0])
                else:
                    room_id = await self._insert_public_room(
                        asession, slug, auth.account_id, auth.display_name
                    )
                    if not room_id:
                        await asession.rollback()
                        self.quick_playing = False
                        self.error = "Impossible de creer une salle rapide."
                        return rx.toast("Impossible de creer une salle.")
                    await asession.commit()
        except SQLAlchemyError as exc:
            logging.exception(f"Error: {exc}")
            self.quick_playing = False
            self.error = "Quick Play a echoue. Reessayez."
            return rx.toast("Quick Play a echoue.")
        self.quick_playing = False
        return GamesState.join_room(room_id, "")

    # ------------------------------------------------- solo practice mode
    @rx.var
    def solo_hint(self) -> str:
        return (
            "Mode test solo — ouvrez une partie instantanement, sans "
            "attendre d'autres joueurs. Session d'entrainement privee: "
            "elle n'affecte pas les salles publiques ni les statistiques."
        )

    def _solo_plan(
        self, slug: str, account_id: int
    ) -> tuple[dict[str, Any], dict[str, Any], int, int, int]:
        """Return (rules, state, turn, deadline seconds, max_players)."""
        if slug == "domino":
            bots = [{"id": -1, "name": "Bot TATA"}]
            participants = [account_id, -1]
            rules: dict[str, Any] = {
                "solo_test": True,
                "game_mode": "classic",
                "target_score": 50,
                "maty": 50,
                "number_of_players": 2,
                "no_double_six": False,
                "one_on_blank": False,
                "fill_with_bots": True,
                "bots": bots,
                "order": participants,
                "game_state": "playing",
            }
            state = engine.domino_initial_state(participants, rules)
            return (
                rules,
                state,
                int(state.get("turn", account_id)),
                engine.domino_turn_seconds(rules),
                2,
            )
        if slug == "ludo":
            rules = engine.ludo_normalize_rules(
                {"solo_test": True, "number_of_players": 1}
            )
            state = engine.ludo_initial_state([account_id], rules)
            return rules, state, account_id, 30, 4
        rules = {"solo_test": True, "tier": "bronze", "draw_seconds": 12}
        state = engine.loto_initial_state()
        state["phase"] = "playing"
        return rules, state, 0, 12, 8

    @rx.event
    async def start_solo_test(self, slug: str):
        """Create a private, immediately playable practice room and enter it."""
        auth = await self.get_state(AuthState)
        if not auth.account_id:
            yield rx.redirect("/login")
            return
        if slug not in VISIBLE_SLUGS:
            yield rx.toast("Ce jeu n'est pas disponible.")
            return
        if self.solo_busy:
            return
        self.solo_busy = True
        self.solo_slug = slug
        self.solo_error = ""
        yield

        me = auth.account_id
        rules, state, turn, seconds, max_players = self._solo_plan(slug, me)
        title = f"Test solo — {slug.upper()}"
        room_id = 0
        try:
            async with rx.asession() as asession:
                game_row = (
                    await asession.execute(
                        text("SELECT id FROM game WHERE slug = :s"),
                        {"s": slug},
                    )
                ).first()
                if game_row is None:
                    self.solo_busy = False
                    self.solo_slug = ""
                    self.solo_error = "Jeu introuvable."
                    yield rx.toast("Jeu introuvable.")
                    return
                for _ in range(10):
                    code = f"S{secrets.token_hex(3).upper()}"
                    taken = (
                        await asession.execute(
                            text(
                                "SELECT 1 FROM game_room WHERE code = :c "
                                "LIMIT 1"
                            ),
                            {"c": code},
                        )
                    ).first()
                    if taken is not None:
                        continue
                    inserted = (
                        await asession.execute(
                            text(
                                """
                                INSERT INTO game_room (game_id, host_id, code,
                                    name, status, is_private, password_hash,
                                    max_players, player_count, entry_coins,
                                    rules_json, state_json, round_number,
                                    pot_coins, state_version,
                                    current_turn_account_id, turn_deadline_at,
                                    created_at, updated_at)
                                VALUES (:g, :h, :code, :name, 'active', true,
                                    '', :max_players, 1, 0, :rules, :state, 1,
                                    0, 0, :turn,
                                    NOW() + (:seconds * INTERVAL '1 second'),
                                    NOW(), NOW())
                                RETURNING id
                                """
                            ),
                            {
                                "g": int(game_row[0]),
                                "h": me,
                                "code": code,
                                "name": title,
                                "max_players": max_players,
                                "rules": json.dumps(rules),
                                "state": json.dumps(state),
                                "turn": turn or None,
                                "seconds": seconds,
                            },
                        )
                    ).first()
                    room_id = int(inserted[0])
                    break
                if not room_id:
                    await asession.rollback()
                    self.solo_busy = False
                    self.solo_slug = ""
                    self.solo_error = (
                        "Impossible de generer un code unique. Reessayez."
                    )
                    yield rx.toast("Impossible d'ouvrir le test solo.")
                    return
                await asession.execute(
                    text(
                        """
                        INSERT INTO game_room_member (room_id, account_id,
                            seat, is_host, is_ready, score, result, joined_at)
                        VALUES (:r, :a, 0, true, true, 0, '', NOW())
                        """
                    ),
                    {"r": room_id, "a": me},
                )
                if slug == "loto":
                    rng = random.Random()
                    for index in (1, 2):
                        await asession.execute(
                            text(
                                """
                                INSERT INTO bingo_card (room_id, account_id,
                                    card_index, grid_json, marked_json,
                                    marked_count, row_progress_json,
                                    price_coins, tier, claimed_quine,
                                    claimed_double_quine, claimed_full_house,
                                    is_void, created_at, updated_at)
                                VALUES (:r, :a, :i, :grid, '[]', 0,
                                    '[0, 0, 0]', 0, 'bronze', false, false,
                                    false, false, NOW(), NOW())
                                """
                            ),
                            {
                                "r": room_id,
                                "a": me,
                                "i": index,
                                "grid": json.dumps(
                                    engine.generate_loto_card(rng)
                                ),
                            },
                        )
                await asession.execute(
                    text(
                        """
                        INSERT INTO game_room_event (room_id, account_id,
                            event_type, detail, created_at)
                        VALUES (:r, :a, 'system', :d, NOW())
                        """
                    ),
                    {
                        "r": room_id,
                        "a": me,
                        "d": (
                            f"Mode test solo ouvert par {auth.display_name} "
                            "(session d'entrainement)"
                        ),
                    },
                )
                await asession.commit()
        except (SQLAlchemyError, engine.MoveError) as exc:
            logging.exception(f"Error: {exc}")
            self.solo_busy = False
            self.solo_slug = ""
            self.solo_error = "Le test solo a echoue. Reessayez."
            yield rx.toast("Le test solo a echoue.")
            return
        self.solo_busy = False
        self.solo_slug = ""
        yield rx.toast("Mode test solo pret: la partie est lancee.")
        yield rx.redirect(f"/game/room/{room_id}")

    # ------------------------------------------- generic creation sheet
    @rx.event
    def open_create_sheet(self):
        self.create_error = ""
        self.create_busy = False
        self.gen_name = ""
        self.gen_private = False
        self.gen_secret = ""
        if self.active_slug == "ludo":
            self.gen_players = 4
            self.gen_entry = "100"
        else:
            self.gen_players = 8
            self.gen_entry = "200"
            self.gen_tier = "bronze"
        self.create_sheet_open = True

    @rx.event
    def close_create_sheet(self):
        self.create_sheet_open = False
        self.create_error = ""
        self.create_busy = False

    @rx.event
    def set_gen_name(self, value: str):
        self.gen_name = value[:80]
        self.create_error = ""

    @rx.event
    def toggle_gen_private(self):
        self.gen_private = not self.gen_private
        self.create_error = ""

    @rx.event
    def set_gen_secret(self, value: str):
        self.gen_secret = value.strip()[:40]
        self.create_error = ""

    @rx.event
    def set_gen_players(self, value: int):
        self.gen_players = int(value)
        self.create_error = ""

    @rx.event
    def set_gen_entry(self, value: str):
        self.gen_entry = "".join(c for c in value if c.isdigit())[:4]
        self.create_error = ""

    @rx.event
    def set_gen_tier(self, value: str):
        for tier in LOTO_TIERS:
            if tier["key"] == value:
                self.gen_tier = value
                self.gen_entry = "0"
        self.create_error = ""

    @rx.event
    async def submit_generic_room(self):
        auth = await self.get_state(AuthState)
        if not auth.account_id:
            return rx.redirect("/login")
        slug = self.active_slug
        if slug not in ("ludo", "loto"):
            self.create_error = "Utilisez la feuille dediee a ce jeu."
            return
        allowed = [2, 3, 4] if slug == "ludo" else [2, 4, 6, 8, 10, 12]
        if self.gen_players not in allowed:
            self.create_error = "Nombre de joueurs invalide pour ce jeu."
            return
        if self.gen_private and len(self.gen_secret) < 4:
            self.create_error = (
                "Le code d'acces prive doit contenir au moins 4 caracteres."
            )
            return
        catalog = game_by_slug(slug)
        rules: dict[str, Any] = {}
        entry = int(self.gen_entry or 0)
        if slug == "loto":
            rules = {"tier": self.gen_tier, "draw_seconds": 12}
            for tier in LOTO_TIERS:
                if tier["key"] == self.gen_tier:
                    entry = 0
        else:
            # Standard Ludo: always four pawns, never configurable.
            rules = {"goal_pawns": 4}
        entry = max(0, min(5000, entry))
        self.create_busy = True
        self.create_error = ""
        room_id = 0
        try:
            async with rx.asession() as asession:
                game_row = (
                    await asession.execute(
                        text("SELECT id FROM game WHERE slug = :s"),
                        {"s": slug},
                    )
                ).first()
                if game_row is None:
                    self.create_busy = False
                    self.create_error = "Jeu introuvable."
                    return
                for _ in range(8):
                    code = secrets.token_hex(3).upper()
                    taken = (
                        await asession.execute(
                            text(
                                "SELECT 1 FROM game_room WHERE code = :c "
                                "LIMIT 1"
                            ),
                            {"c": code},
                        )
                    ).first()
                    if taken is not None:
                        continue
                    inserted = (
                        await asession.execute(
                            text(
                                """
                                INSERT INTO game_room (game_id, host_id, code,
                                    name, status, is_private, password_hash,
                                    max_players, player_count, entry_coins,
                                    rules_json, state_json, round_number,
                                    pot_coins, state_version, created_at,
                                    updated_at)
                                VALUES (:g, :h, :code, :name, 'waiting',
                                    :private, :hash, :max_players, 0, :entry,
                                    :rules, '{}', 0, 0, 0, NOW(), NOW())
                                RETURNING id
                                """
                            ),
                            {
                                "g": int(game_row[0]),
                                "h": auth.account_id,
                                "code": code,
                                "name": self.gen_name.strip()
                                or f"{catalog['name']} de {auth.display_name}",
                                "private": self.gen_private,
                                "hash": hash_password(self.gen_secret)
                                if self.gen_private
                                else "",
                                "max_players": self.gen_players,
                                "entry": entry,
                                "rules": json.dumps(rules),
                            },
                        )
                    ).first()
                    room_id = int(inserted[0])
                    break
                if not room_id:
                    await asession.rollback()
                    self.create_busy = False
                    self.create_error = (
                        "Impossible de generer un code unique. Reessayez."
                    )
                    return
                await asession.commit()
        except SQLAlchemyError as exc:
            logging.exception(f"Error: {exc}")
            self.create_busy = False
            self.create_error = "La creation a echoue. Reessayez."
            return
        self.create_busy = False
        self.create_sheet_open = False
        secret = self.gen_secret if self.gen_private else ""
        self.gen_secret = ""
        return GamesState.join_room(room_id, secret)

    @rx.event
    def toggle_referral(self):
        self.referral_open = not self.referral_open

    @rx.event
    def set_join_code(self, value: str):
        self.join_code = value.strip().upper()

    @rx.event
    async def create_room(self, form_data: dict[str, Any]):
        auth = await self.get_state(AuthState)
        if not auth.account_id:
            yield rx.toast("Connectez-vous pour creer une salle.")
            return
        slug = self.active_slug or "loto"
        catalog = game_by_slug(slug)
        name = str(form_data.get("name", "")).strip()[:80]
        code_secret = str(form_data.get("room_code", "")).strip()
        is_private = bool(code_secret)
        try:
            max_players = int(
                form_data.get("max_players") or catalog["max_players"]
            )
        except ValueError:
            max_players = int(catalog["max_players"])
        max_players = max(2, min(int(catalog["max_players"]), max_players))
        try:
            entry = 0
        except ValueError:
            entry = 0
        entry = 0

        rules: dict[str, Any] = {}
        if slug == "loto":
            tier_key = str(form_data.get("tier", "bronze"))
            rules = {"tier": tier_key, "draw_seconds": 12}
            for tier in LOTO_TIERS:
                if tier["key"] == tier_key:
                    entry = 0
        elif slug == "domino":
            rules = {
                "maty": int(form_data.get("maty") or 50),
                "no_double_six": str(form_data.get("no_double_six", ""))
                == "on",
                "one_on_blank": str(form_data.get("one_on_blank", "")) == "on",
            }
        elif slug == "ludo":
            rules = {
                "goal_pawns": 4,
                "color": str(form_data.get("color", "red")),
            }
        elif slug in ("faritany", "points"):
            rules = {"turn_seconds": 15}
        elif slug in ("rami", "tri"):
            rules = {"turn_seconds": 30}
        elif slug == "billard":
            rules = {"turn_seconds": 45}

        async with rx.asession() as asession:
            game_row = (
                await asession.execute(
                    text("SELECT id FROM game WHERE slug = :s"), {"s": slug}
                )
            ).first()
            if game_row is None:
                self.error = "Jeu introuvable."
                yield rx.toast("Jeu introuvable.")
                return
            inserted = (
                await asession.execute(
                    text(
                        """
                        INSERT INTO game_room (game_id, host_id, code, name,
                            status, is_private, password_hash, max_players,
                            player_count, entry_coins, rules_json, state_json,
                            round_number, pot_coins, state_version,
                            created_at, updated_at)
                        VALUES (:g, :h, :code, :name, 'waiting', :private,
                            :hash, :max_players, 0, :entry, :rules, '{}', 0,
                            0, 0, NOW(), NOW())
                        RETURNING id
                        """
                    ),
                    {
                        "g": int(game_row[0]),
                        "h": auth.account_id,
                        "code": secrets.token_hex(3).upper(),
                        "name": name
                        or f"{catalog['name']} de {auth.display_name}",
                        "private": is_private,
                        "hash": hash_password(code_secret)
                        if is_private
                        else "",
                        "max_players": max_players,
                        "entry": entry,
                        "rules": json.dumps(rules),
                    },
                )
            ).first()
            room_id = int(inserted[0])
            await asession.commit()
        self.create_open = False
        yield GamesState.join_room(room_id, "")

    @rx.event
    async def join_by_code(self):
        code = self.join_code.strip().upper()
        if not code:
            self.error = "Entrez un code de salle."
            return rx.toast("Entrez un code de salle.")
        if len(code) < 4 or not code.isalnum():
            self.error = "Code invalide: 4 caracteres alphanumeriques minimum."
            return rx.toast("Code de salle invalide.")
        self.error = ""
        async with rx.asession() as asession:
            row = (
                await asession.execute(
                    text("SELECT id FROM game_room WHERE code = :c"),
                    {"c": code},
                )
            ).first()
        if row is None:
            self.error = "Aucune salle ne correspond a ce code."
            return rx.toast("Aucune salle avec ce code.")
        self.error = ""
        self.join_code = ""
        return GamesState.join_room(int(row[0]), "")

    @rx.event
    async def join_room(self, room_id: int, secret: str):
        """Locked, capacity-safe join with single entry debit and clear toasts."""
        auth = await self.get_state(AuthState)
        if not auth.account_id:
            return rx.redirect("/login")
        me = auth.account_id
        async with rx.asession() as asession:
            room = (
                await asession.execute(
                    text(
                        """
                        SELECT r.status, r.is_private, r.password_hash,
                               r.max_players, r.player_count, r.entry_coins,
                               g.slug, r.host_id, r.rules_json
                        FROM game_room r JOIN game g ON g.id = r.game_id
                        WHERE r.id = :id FOR UPDATE OF r
                        """
                    ),
                    {"id": room_id},
                )
            ).first()
            if room is None:
                return rx.toast("Salle introuvable.")
            status = str(room[0])
            if status in ("finished", "closed"):
                return rx.toast("Cette salle est terminee ou fermee.")
            member = (
                await asession.execute(
                    text(
                        "SELECT id, left_at FROM game_room_member "
                        "WHERE room_id = :r AND account_id = :a "
                        "ORDER BY id LIMIT 1"
                    ),
                    {"r": room_id, "a": me},
                )
            ).first()
            already = member is not None and member[1] is None
            if already:
                # Duplicate active membership is impossible: just resume.
                await asession.commit()
                return rx.redirect(f"/game/room/{room_id}")
            if status in ("active", "in_progress"):
                return rx.toast(
                    "La partie a deja commence: impossible de rejoindre."
                )

            try:
                rules = json.loads(str(room[8]) or "{}")
            except ValueError:
                rules = {}
            capacity = int(room[3] or 0)
            wanted = rules.get("number_of_players")
            if wanted:
                try:
                    capacity = min(capacity, int(wanted))
                except (TypeError, ValueError):
                    pass
            seats = (
                await asession.execute(
                    text(
                        "SELECT seat FROM game_room_member "
                        "WHERE room_id = :r AND left_at IS NULL"
                    ),
                    {"r": room_id},
                )
            ).all()
            taken = {int(s[0] or 0) for s in seats}
            if len(taken) >= capacity:
                return rx.toast("Salle complete: tous les sieges sont occupes.")
            if bool(room[1]):
                from app.security import verify_password

                if not secret or not verify_password(secret, str(room[2])):
                    return rx.toast("Salle privee: code d'acces invalide.")
            free_seat = 0
            while free_seat in taken:
                free_seat += 1

            entry = int(room[5] or 0)
            if member is None:
                await asession.execute(
                    text(
                        """
                        INSERT INTO game_room_member (room_id, account_id,
                            seat, is_host, is_ready, score, result,
                            joined_at)
                        VALUES (:r, :a, :seat, :host, false, 0, '', NOW())
                        """
                    ),
                    {
                        "r": room_id,
                        "a": me,
                        "seat": free_seat,
                        "host": int(room[7]) == me,
                    },
                )
            else:
                await asession.execute(
                    text(
                        "UPDATE game_room_member SET left_at = NULL, "
                        "is_ready = false, seat = :seat WHERE id = :id"
                    ),
                    {"id": int(member[0]), "seat": free_seat},
                )
            await asession.execute(
                text(
                    """
                    UPDATE game_room
                    SET player_count = (
                        SELECT COUNT(*) FROM game_room_member
                        WHERE room_id = :r AND left_at IS NULL),
                        status = CASE WHEN status = 'open'
                            THEN 'waiting' ELSE status END,
                        updated_at = NOW()
                    WHERE id = :r
                    """
                ),
                {"r": room_id},
            )
            await asession.execute(
                text(
                    """
                    INSERT INTO game_room_event (room_id, account_id,
                        event_type, detail, created_at)
                    VALUES (:r, :a, 'join', :d, NOW())
                    """
                ),
                {
                    "r": room_id,
                    "a": me,
                    "d": f"{auth.display_name} a rejoint la salle",
                },
            )
            await asession.commit()
        return rx.redirect(f"/game/room/{room_id}")
