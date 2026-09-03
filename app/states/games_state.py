"""Games hub: idempotent catalog/room seeding, listings and room creation."""

from __future__ import annotations

import json
import secrets
from typing import Any, TypedDict

import reflex as rx
from sqlalchemy import text

from app.games_catalog import CATALOG, LOTO_TIERS, MATY_TARGETS, game_by_slug
from app.security import hash_password
from app.states.auth_state import AuthState
from app.wallet import balance_of, move_coins


class GameCard(TypedDict):
    slug: str
    name: str
    description: str
    category: str
    tag: str
    medallion: str
    min_players: int
    max_players: int
    entry_coins: int
    open_rooms: int
    live_players: int


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
    entry_coins: int
    pot_coins: int
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

    tier_options: list[dict[str, str]] = [
        {
            "key": str(tier["key"]),
            "label": str(tier["label"]),
            "price": str(tier["card_price"]),
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
    def is_loto(self) -> bool:
        return self.active_slug == "loto"

    @rx.var
    def is_domino(self) -> bool:
        return self.active_slug == "domino"

    @rx.var
    def referral_code(self) -> str:
        return f"TATA-{self.router.session.client_token[:6].upper()}"

    # ---------------------------------------------------------------- seeding
    async def _seed(self, asession, me_id: int) -> None:
        for entry in CATALOG:
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
                    "entry": entry["default_entry_coins"],
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
                entry = int(catalog["default_entry_coins"])
                if slug == "loto":
                    tier = LOTO_TIERS[index * 2]
                    rules = {"tier": tier["key"], "draw_seconds": 12}
                    entry = int(tier["card_price"])
                elif slug == "domino":
                    rules = {
                        "maty": MATY_TARGETS[index],
                        "no_double_six": False,
                        "one_on_blank": index == 1,
                    }
                elif slug == "ludo":
                    rules = {"goal_pawns": 3}
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
            await self._seed(asession, auth.account_id)
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
                        GROUP BY g.id, g.slug, g.name, g.description,
                                 g.category, g.min_players, g.max_players,
                                 g.default_entry_coins
                        ORDER BY g.id
                        """
                    )
                )
            ).all()
        catalog_index = {str(c["slug"]): c for c in CATALOG}
        self.cards = [
            {
                "slug": str(r[0]),
                "name": str(r[1]),
                "description": str(r[2]),
                "category": str(r[3]),
                "tag": str(catalog_index.get(str(r[0]), {}).get("tag", "Live")),
                "medallion": str(
                    catalog_index.get(str(r[0]), {}).get("medallion", "gem")
                ),
                "min_players": int(r[4]),
                "max_players": int(r[5]),
                "entry_coins": int(r[6]),
                "open_rooms": int(r[7] or 0),
                "live_players": int(r[8] or 0),
            }
            for r in rows
        ]
        await self._load_my_rooms(auth.account_id)
        self.loading = False

    async def _load_my_rooms(self, account_id: int) -> None:
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
            "entry_coins": int(r[9] or 0),
            "pot_coins": int(r[10] or 0),
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
        slug = str(self.router.page.params.get("game_slug", "")) or "loto"
        self.active_slug = slug
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
            entry = int(
                form_data.get("entry_coins") or catalog["default_entry_coins"]
            )
        except ValueError:
            entry = int(catalog["default_entry_coins"])
        entry = max(0, min(5000, entry))

        rules: dict[str, Any] = {}
        if slug == "loto":
            tier_key = str(form_data.get("tier", "bronze_lite"))
            rules = {"tier": tier_key, "draw_seconds": 12}
            for tier in LOTO_TIERS:
                if tier["key"] == tier_key:
                    entry = int(tier["card_price"])
        elif slug == "domino":
            rules = {
                "maty": int(form_data.get("maty") or 50),
                "no_double_six": str(form_data.get("no_double_six", ""))
                == "on",
                "one_on_blank": str(form_data.get("one_on_blank", "")) == "on",
            }
        elif slug == "ludo":
            rules = {
                "goal_pawns": int(form_data.get("goal_pawns") or 3),
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
        code = self.join_code
        if not code:
            return rx.toast("Entrez un code de salle.")
        async with rx.asession() as asession:
            row = (
                await asession.execute(
                    text("SELECT id FROM game_room WHERE code = :c"),
                    {"c": code},
                )
            ).first()
        if row is None:
            return rx.toast("Aucune salle avec ce code.")
        return GamesState.join_room(int(row[0]), "")

    @rx.event
    async def join_room(self, room_id: int, secret: str):
        """Capacity + private code validation, atomic entry debit, membership."""
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
                               g.slug, r.host_id
                        FROM game_room r JOIN game g ON g.id = r.game_id
                        WHERE r.id = :id FOR UPDATE
                        """
                    ),
                    {"id": room_id},
                )
            ).first()
            if room is None:
                return rx.toast("Salle introuvable.")
            status = str(room[0])
            if status in ("finished", "closed"):
                return rx.toast("Cette salle est terminee.")
            member = (
                await asession.execute(
                    text(
                        "SELECT id, left_at FROM game_room_member "
                        "WHERE room_id = :r AND account_id = :a"
                    ),
                    {"r": room_id, "a": me},
                )
            ).first()
            already = member is not None and member[1] is None
            if not already:
                if int(room[4] or 0) >= int(room[3] or 0):
                    return rx.toast("Salle complete.")
                if bool(room[1]):
                    from app.security import verify_password

                    if not secret or not verify_password(secret, str(room[2])):
                        return rx.toast("Code de salle invalide.")
                entry = int(room[5] or 0)
                if entry > 0 and str(room[6]) != "loto":
                    ok, message, _ = await move_coins(
                        asession,
                        me,
                        -entry,
                        "game_entry",
                        f"Entree salle #{room_id}",
                        room_id,
                        f"entry:{room_id}:{me}",
                    )
                    if not ok and message:
                        return rx.toast(message)
                    if ok:
                        await asession.execute(
                            text(
                                "UPDATE game_room SET pot_coins = "
                                "pot_coins + :e WHERE id = :r"
                            ),
                            {"e": entry, "r": room_id},
                        )
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
                            "seat": int(room[4] or 0),
                            "host": int(room[7]) == me,
                        },
                    )
                else:
                    await asession.execute(
                        text(
                            "UPDATE game_room_member SET left_at = NULL "
                            "WHERE id = :id"
                        ),
                        {"id": int(member[0])},
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
            balance = await balance_of(asession, me)
        auth.coin_balance = balance
        return rx.redirect(f"/game/room/{room_id}")
