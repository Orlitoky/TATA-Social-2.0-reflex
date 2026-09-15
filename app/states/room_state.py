"""Authoritative, route-driven play room state for every TATA game.

All match state lives in game_room.state_json with an optimistic
state_version guard and SELECT ... FOR UPDATE row locking. Every accepted
action is appended to game_action. Coins are internal virtual points only.
"""

from __future__ import annotations

import asyncio
import json
import random
import secrets
from typing import Any, TypedDict

import reflex as rx
from sqlalchemy import text

from app import game_engine as engine
from app.games_catalog import (
    GAME_REACTIONS,
    LOTO_MAX_CARDS,
    LOTO_MIN_CARDS,
    loto_claim_label,
    tier_by_key,
)
from app.media import avatar_source
from app.states.auth_state import AuthState

import logging


class PlayerRow(TypedDict):
    account_id: int
    name: str
    avatar_url: str
    avatar_remote: bool
    is_host: bool
    is_ready: bool
    is_online: bool
    is_turn: bool
    score: int
    cards: int
    hand_count: int
    color: str
    hearts: int
    home_pawns: int
    is_me: bool
    is_bot: bool


class LobbySlot(TypedDict):
    seat: int
    kind: str
    account_id: int
    name: str
    avatar_url: str
    avatar_remote: bool
    is_host: bool
    is_online: bool
    is_ready: bool
    is_me: bool
    can_remove: bool
    cards: int
    color: str


class ActivityRow(TypedDict):
    id: int
    text: str
    time_label: str


class ReactionRow(TypedDict):
    id: int
    emoji: str
    label: str
    name: str


class LotoCell(TypedDict):
    value: int
    marked: bool


class LotoCard(TypedDict):
    card_index: int
    tier: str
    remaining: int
    marked: int
    rows: list[list[LotoCell]]


class SpectatorRow(TypedDict):
    name: str
    card_index: int
    remaining: int
    low: bool


class TileRow(TypedDict):
    index: int
    a: int
    b: int
    playable: bool
    can_left: bool
    can_right: bool


class ChatRow(TypedDict):
    id: int
    name: str
    text: str
    time_label: str
    is_me: bool


class HistoryRow(TypedDict):
    sequence: int
    kind_label: str
    actor: str
    summary: str
    round_number: int
    time_label: str


class StandingRow(TypedDict):
    account_id: int
    name: str
    avatar_url: str
    avatar_remote: bool
    score: int
    detail: str
    is_winner: bool
    is_me: bool


class ScoreRow(TypedDict):
    name: str
    score: int


class LudoCell(TypedDict):
    kind: str
    color: str
    pawn: str
    safe: bool
    arrow: str


class LudoZone(TypedDict):
    color: str
    name: str
    base: int
    home: int
    is_turn: bool
    corner: str


class NodeRow(TypedDict):
    index: int
    owner: str
    mine: bool
    selected: bool
    empty: bool


class PointCell(TypedDict):
    kind: str
    index: int
    owner: str
    claimable: bool


class HandCard(TypedDict):
    index: int
    label: str
    red: bool
    selected: bool


class MeldRow(TypedDict):
    name: str
    label: str


class BallRow(TypedDict):
    id: int
    label: str
    left: float
    top: float
    color: str
    stripe: bool


class RoomState(rx.State):
    active_id: int = 0
    loaded: bool = False
    error: str = ""
    polling: bool = False

    slug: str = ""
    game_name: str = ""
    room_name: str = ""
    code: str = ""
    status: str = ""
    status_label: str = ""
    is_private: bool = False
    is_host: bool = False
    is_member: bool = False
    max_players: int = 0
    player_count: int = 0
    state_version: int = 0
    round_number: int = 0
    turn_account_id: int = 0
    turn_name: str = ""
    my_turn: bool = False
    seconds_left: int = 0
    timer_expired: bool = False
    winner_name: str = ""
    last_note: str = ""
    players: list[PlayerRow] = []
    activity: list[ActivityRow] = []
    reactions: list[ReactionRow] = []
    announcements: list[str] = []
    reaction_choices: list[dict[str, str]] = GAME_REACTIONS
    reaction_tab: str = "emoji"

    my_account_id: int = 0

    # Shared gameplay tools
    chat_messages: list[ChatRow] = []
    history_rows: list[HistoryRow] = []
    history_open: bool = False
    replay_open: bool = False
    audio_on: bool = True
    result_dismissed: bool = False
    winner_account_id: int = 0
    winner_avatar: str = ""
    winner_avatar_remote: bool = False
    standings: list[StandingRow] = []
    result_headline: str = ""
    result_detail: str = ""
    rematch_busy: bool = False

    # LOTO
    loto_max_cards: int = LOTO_MAX_CARDS
    tier_key: str = ""
    tier_label: str = ""
    tier_max_cards: int = 0
    drawn: list[int] = []
    last_number: int = 0
    buy_count: int = 1
    my_cards: list[LotoCard] = []
    spectators: list[SpectatorRow] = []
    my_card_count: int = 0

    # DOMINO
    domino_mode_name: str = "Classique"
    domino_mode_key: str = "classic"
    domino_bot_count: int = 0
    my_tiles: list[TileRow] = []
    chain: list[TileRow] = []
    left_end: int = -1
    right_end: int = -1
    boneyard_count: int = 0
    scores: list[ScoreRow] = []
    maty_target: int = 50
    domino_variants: str = ""
    round_result_open: bool = False
    round_result_text: str = ""
    domino_can_draw: bool = False
    domino_can_pass: bool = False

    # LUDO
    ludo_rows: list[list[LudoCell]] = []
    dice_value: int = 0
    dice_rolled: bool = False
    ludo_goal: int = 4
    my_pawns: list[int] = []
    my_home_pawns: int = 0
    ludo_zones: list[LudoZone] = []
    legal_pawns: list[int] = []

    # FARITANY
    faritany_rows: list[list[NodeRow]] = []
    selected_node: int = -1

    # POINTS
    points_grid: list[list[PointCell]] = []

    # RAMI / TRI
    my_hand: list[HandCard] = []
    selected_cards: list[int] = []
    discard_label: str = ""
    stock_count: int = 0
    has_drawn: bool = False
    melds: list[MeldRow] = []

    # SHARED WAITING LOBBY (domino / ludo / loto)
    lobby_slots: list[LobbySlot] = []
    lobby_mode: str = "classic"
    lobby_target_score: int = 50
    lobby_target_players: int = 2
    lobby_min_players: int = 2
    lobby_special_rules: list[str] = []
    lobby_fill_bots: bool = False
    lobby_occupied: int = 0
    lobby_bot_count: int = 0
    lobby_human_count: int = 0
    lobby_unready_count: int = 0
    lobby_host_name: str = ""
    lobby_goal_pawns: int = 4
    lobby_tier_label: str = ""
    lobby_tier_max_cards: int = 0
    lobby_draw_seconds: int = 12
    lobby_ticket_total: int = 0
    lobby_my_tickets: int = 0
    my_ready: bool = False

    # BILLARD
    balls: list[BallRow] = []
    aim_angle: int = 0
    aim_power: int = 55
    my_group: str = ""
    billard_note: str = ""

    @rx.var
    def is_playing(self) -> bool:
        return self.status in ("active", "in_progress")

    @rx.var
    def is_waiting(self) -> bool:
        return self.status in ("open", "waiting")

    @rx.var
    def is_finished(self) -> bool:
        return self.status == "finished"

    @rx.var
    def domino_is_rush_auto(self) -> bool:
        return self.domino_mode_key == "rush_auto"

    @rx.var
    def is_tata_game(self) -> bool:
        return self.slug in ("domino", "ludo", "loto")

    @rx.var
    def show_result(self) -> bool:
        return self.is_finished and not self.result_dismissed

    @rx.var
    def i_won(self) -> bool:
        return (
            self.winner_account_id > 0
            and self.winner_account_id == self.my_account_id
        )

    @rx.var
    def urgent(self) -> bool:
        return self.is_playing and self.seconds_left <= 5

    @rx.var
    def audio_label(self) -> str:
        return "Sons actifs" if self.audio_on else "Sons coupes"

    @rx.var
    def timer_label(self) -> str:
        return f"{self.seconds_left}s" if self.seconds_left > 0 else "0s"

    @rx.var
    def drawn_count(self) -> int:
        return len(self.drawn)

    @rx.var
    def recent_draws(self) -> list[int]:
        return self.drawn[:12]

    @rx.var
    def is_game_lobby(self) -> bool:
        """Shared waiting lobby for the three visible TATA games."""
        return self.slug in ("domino", "ludo", "loto") and self.status in (
            "open",
            "waiting",
        )

    @rx.var
    def is_loto_lobby(self) -> bool:
        return self.slug == "loto" and self.status in ("open", "waiting")

    @rx.var
    def connection_state(self) -> str:
        if self.error != "":
            return "error"
        if not self.loaded:
            return "connecting"
        if not self.is_member:
            return "removed"
        if not self.polling:
            return "paused"
        return "live"

    @rx.var
    def connection_label(self) -> str:
        return {
            "error": "Connexion perdue",
            "connecting": "Connexion...",
            "removed": "Hors de la salle",
            "paused": "Synchro en pause",
            "live": "En direct",
        }.get(self.connection_state, "En direct")

    @rx.var
    def lobby_locked_out(self) -> bool:
        """Loaded waiting room viewed by a removed / departed account."""
        return self.loaded and (not self.is_member) and self.error == ""

    @rx.var
    def detail_href(self) -> str:
        return f"/games/{self.slug}"

    @rx.var
    def lobby_mode_label(self) -> str:
        return {
            "classic": "Classique",
            "rush_auto": "Rush Auto",
            "rush_manual": "Rush Manuel",
            "draw": "Pioche",
        }.get(self.lobby_mode, "Classique")

    @rx.var
    def lobby_free_seats(self) -> int:
        return max(0, self.lobby_target_players - self.lobby_occupied)

    @rx.var
    def lobby_is_complete(self) -> bool:
        return self.lobby_occupied >= self.lobby_target_players

    @rx.var
    def lobby_can_start(self) -> bool:
        if not self.is_host or not self.is_waiting:
            return False
        if self.lobby_unready_count > 0:
            return False
        if self.lobby_human_count > self.lobby_target_players:
            return False
        if self.slug == "loto":
            return self.lobby_human_count >= 1 and self.lobby_ticket_total > 0
        if self.slug == "ludo":
            return self.lobby_human_count >= 2
        if self.slug == "domino":
            if self.lobby_human_count >= self.lobby_target_players:
                return True
            return self.lobby_fill_bots and self.lobby_human_count >= 1
        return self.lobby_human_count >= self.lobby_min_players

    @rx.var
    def lobby_start_hint(self) -> str:
        if not self.is_waiting:
            return "La partie a deja commence."
        if self.lobby_human_count > self.lobby_target_players:
            return (
                f"Trop de joueurs: {self.lobby_target_players} place(s) "
                "configuree(s)."
            )
        if self.lobby_unready_count > 0:
            return (
                f"{self.lobby_unready_count} joueur(s) ne sont pas encore "
                "prets."
            )
        if self.slug == "loto":
            if self.lobby_ticket_total == 0:
                return "Achetez au moins un carton avant de lancer le tirage."
            return "Tirage pret: les cartons sont en jeu."
        if self.slug == "ludo":
            if self.lobby_human_count < 2:
                return "Ludo demande au moins 2 joueurs humains."
            return "Tous les joueurs sont prets."
        if self.lobby_human_count >= self.lobby_target_players:
            return "Tous les sieges sont occupes."
        missing = self.lobby_target_players - self.lobby_human_count
        if self.lobby_fill_bots:
            return (
                f"{missing} siege(s) libre(s): le serveur les completera "
                "avec des bots."
            )
        return f"En attente de {missing} joueur(s) pour lancer la partie."

    @rx.var
    def visible_reactions(self) -> list[ReactionRow]:
        return [
            r for r in self.reactions if r["label"] != "" or r["emoji"] != ""
        ][:12]

    # ------------------------------------------------------------- utilities
    def _params_room_id(self) -> int:
        raw = self.router.page.params.get("room_id", "0")
        try:
            return int(str(raw))
        except ValueError:
            return 0

    async def _ctx(self, asession, room_id: int, lock: bool = False):
        suffix = " FOR UPDATE OF r" if lock else ""
        return (
            await asession.execute(
                text(
                    """
                    SELECT r.state_json, r.rules_json, r.status,
                           r.state_version, r.current_turn_account_id,
                           r.round_number, r.pot_coins, g.slug, r.host_id,
                           r.entry_coins, r.max_players, r.code, r.name,
                           g.name, r.is_private, r.winner_account_id, g.id,
                           r.turn_deadline_at, r.settled_at, r.player_count,
                           r.created_at
                    FROM game_room r JOIN game g ON g.id = r.game_id
                    WHERE r.id = :id
                    """
                    + suffix
                ),
                {"id": room_id},
            )
        ).first()

    async def _order(self, asession, room_id: int) -> list[int]:
        rows = (
            await asession.execute(
                text(
                    "SELECT account_id FROM game_room_member "
                    "WHERE room_id = :r AND left_at IS NULL "
                    "ORDER BY seat, id"
                ),
                {"r": room_id},
            )
        ).all()
        return [int(r[0]) for r in rows]

    async def _log(
        self,
        asession,
        room_id: int,
        kind: str,
        payload: dict[str, Any],
        version: int,
        round_number: int,
        actor: int | None,
    ) -> None:
        row = (
            await asession.execute(
                text(
                    "SELECT COALESCE(MAX(sequence), 0) + 1 FROM game_action "
                    "WHERE room_id = :r"
                ),
                {"r": room_id},
            )
        ).first()
        await asession.execute(
            text(
                """
                INSERT INTO game_action (room_id, account_id, kind,
                    payload_json, state_version, sequence, round_number,
                    created_at)
                VALUES (:r, :a, :k, :p, :v, :s, :n, NOW())
                """
            ),
            {
                "r": room_id,
                "a": actor,
                "k": kind,
                "p": json.dumps(payload)[:6000],
                "v": version,
                "s": int(row[0]),
                "n": round_number,
            },
        )

    async def _event(
        self, asession, room_id: int, kind: str, detail: str, actor: int | None
    ) -> None:
        await asession.execute(
            text(
                """
                INSERT INTO game_room_event (room_id, account_id, event_type,
                    detail, created_at)
                VALUES (:r, :a, :k, :d, NOW())
                """
            ),
            {"r": room_id, "a": actor, "k": kind, "d": detail[:2000]},
        )

    async def _write(
        self,
        asession,
        room_id: int,
        expected: int,
        state: dict,
        *,
        status: str | None = None,
        turn: int | None = None,
        deadline_seconds: int | None = None,
        round_number: int | None = None,
        winner: int | None = None,
        rules: dict | None = None,
        kind: str = "system",
        payload: dict[str, Any] | None = None,
        actor: int | None = None,
    ) -> bool:
        """Optimistic write: succeeds only when state_version still matches."""
        sets = [
            "state_json = :state",
            "state_version = state_version + 1",
            "updated_at = NOW()",
        ]
        params: dict[str, Any] = {
            "state": json.dumps(state),
            "id": room_id,
            "v": expected,
        }
        if status is not None:
            sets.append("status = :status")
            params["status"] = status
        if turn is not None:
            sets.append("current_turn_account_id = :turn")
            params["turn"] = turn
        if deadline_seconds is not None:
            sets.append(
                "turn_deadline_at = NOW() + (:seconds * INTERVAL '1 second')"
            )
            params["seconds"] = deadline_seconds
        if round_number is not None:
            sets.append("round_number = :round")
            params["round"] = round_number
        if winner is not None:
            sets.append("winner_account_id = :winner")
            params["winner"] = winner
        if rules is not None:
            sets.append("rules_json = :rules")
            params["rules"] = json.dumps(rules)
        result = await asession.execute(
            text(
                "UPDATE game_room SET "
                + ", ".join(sets)
                + " WHERE id = :id AND state_version = :v"
            ),
            params,
        )
        if result.rowcount == 0:
            return False
        await self._log(
            asession,
            room_id,
            kind,
            payload or {},
            expected + 1,
            round_number if round_number is not None else self.round_number,
            actor,
        )
        return True

    async def _stats(
        self, asession, room_id: int, game_id: int, winner_id: int
    ) -> None:
        members = await self._order(asession, room_id)
        for account_id in members:
            won = 1 if account_id == winner_id else 0
            await asession.execute(
                text(
                    """
                    INSERT INTO player_game_stat (account_id, game_id,
                        matches_played, wins, losses, draws, best_score,
                        total_score, current_streak, best_streak,
                        coins_earned, last_played_at, created_at, updated_at)
                    VALUES (:a, :g, 1, :w, :l, 0, 0, 0, :w, :w, 0, NOW(),
                        NOW(), NOW())
                    ON CONFLICT (account_id, game_id) DO UPDATE SET
                        matches_played = player_game_stat.matches_played + 1,
                        wins = player_game_stat.wins + :w,
                        losses = player_game_stat.losses + :l,
                        current_streak = CASE WHEN :w = 1
                            THEN player_game_stat.current_streak + 1 ELSE 0 END,
                        best_streak = GREATEST(player_game_stat.best_streak,
                            CASE WHEN :w = 1
                            THEN player_game_stat.current_streak + 1 ELSE 0 END),
                        last_played_at = NOW(),
                        updated_at = NOW()
                    """
                ),
                {"a": account_id, "g": game_id, "w": won, "l": 1 - won},
            )

    async def _settle(
        self,
        asession,
        room_id: int,
        game_id: int,
        winner_id: int,
        pot: int,
        label: str,
    ) -> int:
        """Deterministic, one-time settlement. Cannot ever pay twice."""
        locked = (
            await asession.execute(
                text(
                    "SELECT settled_at FROM game_room WHERE id = :id FOR UPDATE"
                ),
                {"id": room_id},
            )
        ).first()
        if locked is not None and locked[0] is not None:
            return 0
        payable = winner_id if winner_id > 0 else 0
        net = 0
        await asession.execute(
            text(
                """
                UPDATE game_room
                SET status = 'finished', winner_account_id = :w,
                    settled_at = NOW(), finished_at = NOW(),
                    turn_deadline_at = NULL, updated_at = NOW()
                WHERE id = :id
                """
            ),
            {"w": payable or None, "id": room_id},
        )
        await asession.execute(
            text(
                "UPDATE game_room_member SET result = CASE WHEN "
                "account_id = :w THEN 'win' ELSE 'loss' END WHERE room_id = :r"
            ),
            {"w": winner_id, "r": room_id},
        )
        if payable:
            await self._stats(asession, room_id, game_id, payable)
        await self._event(
            asession,
            room_id,
            "settle",
            f"Partie terminee: {label}",
            None,
        )
        return net

    # ------------------------------------------------------------------ load
    @rx.event
    async def load_room(self):
        self.active_id = self._params_room_id()
        self.error = ""
        self.loaded = False
        await self._refresh()
        self.loaded = True
        self.polling = True
        return RoomState.poll

    @rx.event(background=True)
    async def poll(self):
        """Modest polling refresh (no background worker required to play)."""
        while True:
            await asyncio.sleep(3)
            async with self:
                if not self.polling or self.active_id == 0:
                    return
                room_id = self.active_id
            async with self:
                if self.active_id != room_id:
                    return
                await self._refresh()

    @rx.event
    def stop_polling(self):
        self.polling = False

    @rx.event
    async def manual_refresh(self):
        await self._refresh()

    def _domino_bots(self, rules: dict) -> list[dict[str, str | int]]:
        """Normalised bot metadata: stable negative ids + display names."""
        result: list[dict[str, str | int]] = []
        for position, raw in enumerate(rules.get("bots") or []):
            if isinstance(raw, dict):
                try:
                    bot_id = int(raw.get("id", -(position + 1)))
                except (TypeError, ValueError):
                    bot_id = -(position + 1)
                name = str(raw.get("name") or f"Bot {position + 1}")
            else:
                bot_id = -(position + 1)
                name = str(raw) or f"Bot {position + 1}"
            result.append({"id": bot_id, "name": name})
        return result

    def _domino_order(self, rules: dict, humans: list[int]) -> list[int]:
        """Persisted participant order (humans + negative-id bots)."""
        stored = []
        for raw in rules.get("order") or []:
            try:
                stored.append(int(raw))
            except (TypeError, ValueError):
                continue
        if not stored:
            return list(humans)
        order = [p for p in stored if p < 0 or p in humans]
        for human in humans:
            if human not in order:
                order.append(human)
        return order or list(humans)

    async def _refresh(self, allow_bots: bool = True) -> None:
        auth = await self.get_state(AuthState)
        me = auth.account_id
        room_id = self.active_id or self._params_room_id()
        self.active_id = room_id
        self.my_account_id = me
        if room_id == 0 or me == 0:
            self.error = "Salle introuvable."
            return
        async with rx.asession() as asession:
            room = await self._ctx(asession, room_id)
            if room is None:
                self.error = "Cette salle n'existe plus."
                return
            state = json.loads(str(room[0]) or "{}")
            rules = json.loads(str(room[1]) or "{}")
            self.slug = str(room[7])
            self.game_name = str(room[13])
            self.room_name = str(room[12]) or f"Salle {room[11]}"
            self.code = str(room[11])
            self.status = str(room[2])
            self.status_label = {
                "open": "Ouverte",
                "waiting": "Salle d'attente",
                "active": "En cours",
                "in_progress": "En cours",
                "finished": "Terminee",
                "closed": "Fermee",
            }.get(self.status, self.status)
            self.state_version = int(room[3] or 0)
            self.turn_account_id = int(room[4] or 0)
            self.round_number = int(room[5] or 0)
            self.is_host = int(room[8]) == me
            self.max_players = int(room[10] or 0)
            self.is_private = bool(room[14])
            self.player_count = int(room[19] or 0)
            self.my_turn = self.turn_account_id == me
            self.last_note = str(state.get("last", ""))

            deadline = room[17]
            if deadline is not None:
                seconds = (
                    await asession.execute(
                        text(
                            "SELECT GREATEST(0, CAST(EXTRACT(EPOCH FROM "
                            "(:d - NOW())) AS INTEGER))"
                        ),
                        {"d": deadline},
                    )
                ).first()
                self.seconds_left = int(seconds[0] or 0)
            else:
                self.seconds_left = 0
            self.timer_expired = deadline is not None and self.seconds_left <= 0

            member_rows = (
                await asession.execute(
                    text(
                        """
                        SELECT m.account_id, COALESCE(p.display_name,
                                   a.username),
                               COALESCE(p.avatar_key, ''), a.username,
                               m.is_host, m.is_ready, a.is_online, m.score
                        FROM game_room_member m
                        JOIN account a ON a.id = m.account_id
                        LEFT JOIN profile p ON p.account_id = a.id
                        WHERE m.room_id = :r AND m.left_at IS NULL
                        ORDER BY m.seat, m.id
                        """
                    ),
                    {"r": room_id},
                )
            ).all()
            order = [int(r[0]) for r in member_rows]
            self.is_member = me in order

            card_counts: dict[int, int] = {}
            if self.slug == "loto":
                counts = (
                    await asession.execute(
                        text(
                            "SELECT account_id, COUNT(*) FROM bingo_card "
                            "WHERE room_id = :r AND is_void = false "
                            "GROUP BY account_id"
                        ),
                        {"r": room_id},
                    )
                ).all()
                card_counts = {int(c[0]): int(c[1]) for c in counts}

            hands = state.get("hands", {})
            colors = state.get("colors", {})
            hearts = state.get("hearts", {})
            scores_state = state.get("scores", {})
            players: list[PlayerRow] = []
            for row in member_rows:
                account_id = int(row[0])
                url, remote = avatar_source(str(row[2]), str(row[3]))
                players.append(
                    {
                        "account_id": account_id,
                        "name": str(row[1]),
                        "avatar_url": url,
                        "avatar_remote": remote,
                        "is_host": bool(row[4]),
                        "is_ready": bool(row[5]),
                        "is_online": bool(row[6]),
                        "is_turn": account_id == self.turn_account_id,
                        "score": int(
                            scores_state.get(str(account_id), row[7] or 0)
                        ),
                        "cards": card_counts.get(account_id, 0),
                        "hand_count": len(hands.get(str(account_id), [])),
                        "color": str(colors.get(str(account_id), "")),
                        "hearts": int(hearts.get(str(account_id), 3)),
                        "home_pawns": engine.ludo_home_count(state, account_id)
                        if self.slug == "ludo"
                        else 0,
                        "is_me": account_id == me,
                        "is_bot": False,
                    }
                )
            if self.slug == "domino":
                for bot in self._domino_bots(rules):
                    bot_id = int(bot["id"])
                    bot_name = str(bot["name"])
                    players.append(
                        {
                            "account_id": bot_id,
                            "name": bot_name,
                            "avatar_url": (
                                "https://api.dicebear.com/9.x/bottts/svg"
                                f"?seed={bot_name}"
                            ),
                            "avatar_remote": True,
                            "is_host": False,
                            "is_ready": True,
                            "is_online": True,
                            "is_turn": bot_id == self.turn_account_id,
                            "score": int(scores_state.get(str(bot_id), 0)),
                            "cards": 0,
                            "hand_count": len(hands.get(str(bot_id), [])),
                            "color": "",
                            "hearts": 3,
                            "home_pawns": 0,
                            "is_me": False,
                            "is_bot": True,
                        }
                    )
            self.players = players
            self._build_lobby(rules, me)
            names = {p["account_id"]: p["name"] for p in players}
            self.turn_name = names.get(self.turn_account_id, "")
            winner_id = int(room[15] or 0)
            self.winner_account_id = winner_id
            self.winner_name = names.get(winner_id, "") if winner_id else ""
            winner_row = next(
                (p for p in players if p["account_id"] == winner_id), None
            )
            self.winner_avatar = winner_row["avatar_url"] if winner_row else ""
            self.winner_avatar_remote = (
                bool(winner_row["avatar_remote"]) if winner_row else False
            )

            event_rows = (
                await asession.execute(
                    text(
                        """
                        SELECT id, detail, TO_CHAR(created_at, 'HH24:MI:SS')
                        FROM game_room_event WHERE room_id = :r
                          AND event_type <> 'chat'
                        ORDER BY id DESC LIMIT 18
                        """
                    ),
                    {"r": room_id},
                )
            ).all()
            self.activity = [
                {
                    "id": int(e[0]),
                    "text": str(e[1]),
                    "time_label": str(e[2]),
                }
                for e in event_rows
            ]
            reaction_rows = (
                await asession.execute(
                    text(
                        """
                        SELECT gr.id, gr.emoji, gr.label,
                               COALESCE(p.display_name, a.username)
                        FROM game_reaction gr
                        JOIN account a ON a.id = gr.account_id
                        LEFT JOIN profile p ON p.account_id = a.id
                        WHERE gr.room_id = :r
                        ORDER BY gr.id DESC LIMIT 12
                        """
                    ),
                    {"r": room_id},
                )
            ).all()
            self.reactions = [
                {
                    "id": int(r[0]),
                    "emoji": str(r[1]),
                    "label": str(r[2]),
                    "name": str(r[3]),
                }
                for r in reaction_rows
            ]
            action_rows = (
                await asession.execute(
                    text(
                        """
                        SELECT kind, payload_json FROM game_action
                        WHERE room_id = :r AND kind IN ('claim_quine',
                            'claim_double_quine', 'claim_full_house',
                            'round_end', 'settle')
                        ORDER BY id DESC LIMIT 5
                        """
                    ),
                    {"r": room_id},
                )
            ).all()
            announcements: list[str] = []
            for kind, payload in action_rows:
                try:
                    data = json.loads(str(payload) or "{}")
                except ValueError:
                    data = {}
                label = {
                    "claim_quine": loto_claim_label("quine"),
                    "claim_double_quine": loto_claim_label("double_quine"),
                    "claim_full_house": loto_claim_label("full_house"),
                    "round_end": "Manche",
                    "settle": "Reglement",
                }.get(str(kind), str(kind))
                who = str(data.get("name", ""))
                extra = ""
                announcements.append(f"{label}: {who}{extra}")
            self.announcements = announcements
            await self._load_chat(asession, room_id, me)
            await self._load_history(asession, room_id)
            await self._build_view(asession, room_id, state, rules, me, order)
            self._build_standings(state, me, winner_id)

        if (
            allow_bots
            and self.slug == "loto"
            and self.status in ("active", "in_progress")
            and self.timer_expired
        ):
            drawn_ok, _, _, _ = await self._loto_draw_once(manual=False)
            if drawn_ok:
                await self._refresh(allow_bots=False)
                return

        if (
            allow_bots
            and self.slug == "domino"
            and self.status in ("active", "in_progress")
            and self.turn_account_id < 0
        ):
            if await self._run_bots():
                await self._refresh(allow_bots=False)

    # ---------------------------------------------- chat / history / result
    async def _load_chat(self, asession, room_id: int, me: int) -> None:
        rows = (
            await asession.execute(
                text(
                    """
                    SELECT e.id, e.detail,
                           TO_CHAR(e.created_at, 'HH24:MI'),
                           COALESCE(p.display_name, a.username, 'Systeme'),
                           COALESCE(e.account_id, 0)
                    FROM game_room_event e
                    LEFT JOIN account a ON a.id = e.account_id
                    LEFT JOIN profile p ON p.account_id = a.id
                    WHERE e.room_id = :r AND e.event_type = 'chat'
                    ORDER BY e.id DESC LIMIT 40
                    """
                ),
                {"r": room_id},
            )
        ).all()
        messages = [
            {
                "id": int(r[0]),
                "text": str(r[1]),
                "time_label": str(r[2]),
                "name": str(r[3]),
                "is_me": int(r[4] or 0) == me,
            }
            for r in rows
        ]
        messages.reverse()
        self.chat_messages = messages

    def _action_summary(self, kind: str, data: dict) -> tuple[str, str]:
        """Honest, hidden-hand-free summary of one persisted action."""
        labels = {
            "start": "Debut",
            "place_tile": "Pose",
            "draw_tile": "Pioche",
            "pass_turn": "Passe",
            "bot_move": "Bot",
            "roll_dice": "De",
            "move_piece": "Deplacement",
            "capture": "Capture",
            "draw": "Tirage",
            "timeout": "Temps ecoule",
            "round_end": "Fin de manche",
            "settle": "Partie terminee",
            "claim_quine": loto_claim_label("quine"),
            "claim_double_quine": loto_claim_label("double_quine"),
            "claim_full_house": loto_claim_label("full_house"),
            "buy_card": "Cartons",
            "system": "Systeme",
        }
        label = labels.get(kind, kind)
        if kind == "place_tile":
            side = str(data.get("side", ""))
            side_label = {"left": "a gauche", "right": "a droite"}.get(
                side, "cote resolu par le serveur"
            )
            return label, f"Tuile posee {side_label}"
        if kind == "draw_tile":
            return label, "Une tuile piochee (contenu prive)"
        if kind == "pass_turn":
            return label, "Tour passe: aucune pose possible"
        if kind == "bot_move":
            return label, str(data.get("note", "coup du bot"))
        if kind == "roll_dice":
            return label, f"De {data.get('dice', 0)}"
        if kind == "move_piece":
            return label, f"Pion {int(data.get('pawn', 0)) + 1} avance"
        if kind == "capture":
            return label, "Pion adverse renvoye a la base"
        if kind == "draw":
            return label, f"Boule {data.get('number', '-')}"
        if kind in (
            "claim_quine",
            "claim_double_quine",
            "claim_full_house",
        ):
            return (label, f"{data.get('name', '')} - achievement valide")
        if kind == "round_end":
            return label, "Score de manche valide"
        if kind == "timeout":
            return label, "Le serveur a fait avancer le tour"
        if kind == "start":
            return label, f"{data.get('players', 0)} joueur(s) en lice"
        return label, ""

    async def _load_history(self, asession, room_id: int) -> None:
        rows = (
            await asession.execute(
                text(
                    """
                    SELECT ga.sequence, ga.kind, ga.payload_json,
                           ga.round_number,
                           TO_CHAR(ga.created_at, 'HH24:MI:SS'),
                           COALESCE(p.display_name, a.username, 'Serveur')
                    FROM game_action ga
                    LEFT JOIN account a ON a.id = ga.account_id
                    LEFT JOIN profile p ON p.account_id = a.id
                    WHERE ga.room_id = :r
                    ORDER BY ga.sequence LIMIT 400
                    """
                ),
                {"r": room_id},
            )
        ).all()
        history: list[HistoryRow] = []
        for row in rows:
            try:
                data = json.loads(str(row[2]) or "{}")
            except ValueError:
                data = {}
            if not isinstance(data, dict):
                data = {}
            label, summary = self._action_summary(str(row[1]), data)
            history.append(
                {
                    "sequence": int(row[0] or 0),
                    "kind_label": label,
                    "actor": str(row[5]),
                    "summary": summary,
                    "round_number": int(row[3] or 0),
                    "time_label": str(row[4]),
                }
            )
        self.history_rows = history

    def _build_standings(self, state: dict, me: int, winner_id: int) -> None:
        rows: list[StandingRow] = []
        scores_state = state.get("scores", {})
        for player in self.players:
            account_id = int(player["account_id"])
            score = int(scores_state.get(str(account_id), player["score"]))
            if self.slug == "loto":
                detail = f"{player['cards']} carton(s)"
            elif self.slug == "ludo":
                detail = f"{player['home_pawns']}/4 pions a la maison"
            else:
                detail = f"{score} score"
            rows.append(
                {
                    "account_id": account_id,
                    "name": player["name"],
                    "avatar_url": player["avatar_url"],
                    "avatar_remote": player["avatar_remote"],
                    "score": score,
                    "detail": detail,
                    "is_winner": account_id == winner_id and winner_id != 0,
                    "is_me": account_id == me,
                }
            )
        rows.sort(key=lambda r: (0 if r["is_winner"] else 1, -r["score"]))
        self.standings = rows
        if self.status == "finished":
            if winner_id and winner_id == me:
                self.result_headline = "Victoire"
            elif winner_id:
                self.result_headline = "Defaite"
            else:
                self.result_headline = "Partie terminee"
            if self.slug == "loto":
                self.result_detail = (
                    f"{loto_claim_label('full_house')} remporte"
                )
            elif self.slug == "ludo":
                self.result_detail = (
                    "Quatre pions a la maison - achievement valide"
                )
            else:
                self.result_detail = (
                    f"Objectif Maty {self.maty_target} atteint - score valide"
                )
        else:
            self.result_headline = ""
            self.result_detail = ""
            self.result_dismissed = False

    # ------------------------------------------------- per-game view builder
    async def _build_view(
        self,
        asession,
        room_id: int,
        state: dict,
        rules: dict,
        me: int,
        order: list[int],
    ) -> None:
        slug = self.slug
        if slug == "loto":
            tier = tier_by_key(str(rules.get("tier", "bronze")))
            self.tier_key = str(tier["key"])
            self.tier_label = str(tier["label"])
            self.tier_max_cards = LOTO_MAX_CARDS
            drawn = [int(n) for n in state.get("drawn", [])]
            self.drawn = list(reversed(drawn))
            self.last_number = drawn[-1] if drawn else 0
            rows = (
                await asession.execute(
                    text(
                        """
                        SELECT bc.card_index, bc.grid_json, bc.account_id,
                               COALESCE(p.display_name, a.username)
                        FROM bingo_card bc
                        JOIN account a ON a.id = bc.account_id
                        LEFT JOIN profile p ON p.account_id = a.id
                        WHERE bc.room_id = :r AND bc.is_void = false
                        ORDER BY bc.account_id, bc.card_index
                        """
                    ),
                    {"r": room_id},
                )
            ).all()
            mine: list[LotoCard] = []
            spectators: list[SpectatorRow] = []
            drawn_set = set(drawn)
            for card_index, grid_json, account_id, name in rows:
                grid = json.loads(str(grid_json) or "[]")
                _, marked, remaining = engine.loto_card_progress(grid, drawn)
                if int(account_id) == me:
                    mine.append(
                        {
                            "card_index": int(card_index),
                            "tier": self.tier_label,
                            "remaining": remaining,
                            "marked": marked,
                            "rows": [
                                [
                                    {
                                        "value": int(value),
                                        "marked": int(value) in drawn_set,
                                    }
                                    for value in row
                                ]
                                for row in grid
                            ],
                        }
                    )
                spectators.append(
                    {
                        "name": str(name),
                        "card_index": int(card_index),
                        "remaining": remaining,
                        "low": remaining <= 3,
                    }
                )
            self.my_cards = mine
            self.my_card_count = len(mine)
            self.spectators = sorted(spectators, key=lambda s: s["remaining"])[
                :24
            ]
        elif slug == "domino":
            self.maty_target = engine.domino_target_score(rules)
            self.domino_mode_name = engine.domino_mode_label(rules)
            self.domino_mode_key = engine.domino_mode(rules)
            self.domino_bot_count = len(self._domino_bots(rules))
            variants = []
            if rules.get("no_double_six"):
                variants.append("Sans Double-Six")
            if rules.get("one_on_blank"):
                variants.append("Un sur Blanc")
            self.domino_variants = " • ".join(variants) or "Regles standard"
            ends = state.get("ends", [-1, -1])
            self.left_end = int(ends[0])
            self.right_end = int(ends[1])
            hand = state.get("hands", {}).get(str(me), [])
            tiles: list[TileRow] = []
            for index, tile in enumerate(hand):
                if state.get("hands"):
                    can_left, can_right = engine.domino_playable_sides(
                        state, me, index
                    )
                else:
                    can_left, can_right = False, False
                tiles.append(
                    {
                        "index": index,
                        "a": int(tile[0]),
                        "b": int(tile[1]),
                        "playable": can_left or can_right,
                        "can_left": can_left,
                        "can_right": can_right,
                    }
                )
            self.my_tiles = tiles
            self.chain = [
                {
                    "index": index,
                    "a": int(tile[0]),
                    "b": int(tile[1]),
                    "playable": False,
                    "can_left": False,
                    "can_right": False,
                }
                for index, tile in enumerate(state.get("chain", []))
            ]
            self.domino_can_draw = bool(
                self.my_turn
                and self.is_playing
                and engine.domino_can_draw(state, me)
            )
            self.domino_can_pass = bool(
                self.my_turn
                and self.is_playing
                and engine.domino_can_pass(state, me)
            )
            self.boneyard_count = len(state.get("boneyard", []))
            names = {p["account_id"]: p["name"] for p in self.players}
            self.scores = [
                {
                    "name": names.get(int(a), f"#{a}"),
                    "score": int(v),
                }
                for a, v in state.get("scores", {}).items()
            ]
        elif slug == "ludo":
            self.ludo_goal = engine.LUDO_PAWNS
            self.dice_value = int(state.get("dice", 0))
            self.dice_rolled = bool(state.get("rolled", False))
            pawns = [int(p) for p in state.get("pawns", {}).get(str(me), [])]
            while len(pawns) < engine.LUDO_PAWNS and state.get("pawns"):
                pawns.append(-1)
            self.my_pawns = pawns
            self.my_home_pawns = sum(1 for p in pawns if p >= engine.LUDO_HOME)
            self.legal_pawns = (
                engine.ludo_legal_pawns(state, me) if state.get("pawns") else []
            )
            self.ludo_rows = self._ludo_grid(state)
            corners = ["tl", "tr", "br", "bl"]
            palette = ["red", "green", "yellow", "blue"]
            zones: list[LudoZone] = []
            for position, player in enumerate(
                [p for p in self.players if p["account_id"] > 0]
            ):
                account_id = player["account_id"]
                raw = [
                    int(p)
                    for p in state.get("pawns", {}).get(str(account_id), [])
                ]
                while len(raw) < engine.LUDO_PAWNS:
                    raw.append(-1)
                zones.append(
                    {
                        "color": str(player["color"]) or palette[position % 4],
                        "name": player["name"],
                        "base": sum(1 for p in raw if p < 0),
                        "home": sum(1 for p in raw if p >= engine.LUDO_HOME),
                        "is_turn": account_id == self.turn_account_id,
                        "corner": corners[position % 4],
                    }
                )
            self.ludo_zones = zones
        elif slug == "faritany":
            cells = state.get("cells", [""] * 25)
            self.faritany_rows = [
                [
                    {
                        "index": row * 5 + col,
                        "owner": str(cells[row * 5 + col]),
                        "mine": str(cells[row * 5 + col]) == str(me),
                        "selected": self.selected_node == row * 5 + col,
                        "empty": str(cells[row * 5 + col]) == "",
                    }
                    for col in range(5)
                ]
                for row in range(5)
            ]
        elif slug == "points":
            self.points_grid = self._points_grid(state)
            names = {p["account_id"]: p["name"] for p in self.players}
            self.scores = [
                {"name": names.get(int(a), f"#{a}"), "score": int(v)}
                for a, v in state.get("scores", {}).items()
            ]
        elif slug in ("rami", "tri"):
            hand = state.get("hands", {}).get(str(me), [])
            self.my_hand = [
                {
                    "index": index,
                    "label": engine.card_label(int(code)),
                    "red": int(code) % 10 in (1, 2),
                    "selected": index in self.selected_cards,
                }
                for index, code in enumerate(hand)
            ]
            discard = state.get("discard", [])
            self.discard_label = (
                engine.card_label(int(discard[-1])) if discard else ""
            )
            self.stock_count = len(state.get("stock", []))
            self.has_drawn = bool(state.get("drawn", False))
            names = {p["account_id"]: p["name"] for p in self.players}
            melds: list[MeldRow] = []
            for account_id, groups in state.get("melds", {}).items():
                for group in groups:
                    melds.append(
                        {
                            "name": names.get(
                                int(account_id), f"#{account_id}"
                            ),
                            "label": " ".join(
                                engine.card_label(int(c)) for c in group
                            ),
                        }
                    )
            self.melds = melds
        elif slug == "billard":
            groups = state.get("groups", {})
            self.my_group = {
                "solids": "Pleines",
                "stripes": "Rayees",
            }.get(str(groups.get(str(me), "")), "Non assigne")
            self.billard_note = str(state.get("last", ""))
            balls: list[BallRow] = []
            for ball in state.get("balls", []):
                ball_id = int(ball["id"])
                balls.append(
                    {
                        "id": ball_id,
                        "label": "" if ball_id == 0 else str(ball_id),
                        "left": float(ball["x"]) / engine.TABLE_W * 100.0,
                        "top": float(ball["y"]) / engine.TABLE_H * 100.0,
                        "color": self._ball_color(ball_id),
                        "stripe": ball_id > 8,
                    }
                )
            self.balls = [
                b
                for b, raw in zip(balls, state.get("balls", []))
                if not bool(raw.get("potted"))
            ]

    def _ball_color(self, ball_id: int) -> str:
        palette = {
            0: "#F8FAFC",
            8: "#0B0F14",
            1: "#FBBF24",
            2: "#2563EB",
            3: "#DC2626",
            4: "#7C3AED",
            5: "#F97316",
            6: "#059669",
            7: "#7F1D1D",
        }
        return palette.get(ball_id if ball_id <= 8 else ball_id - 8, "#FBBF24")

    def _ludo_grid(self, state: dict) -> list[list[LudoCell]]:
        colors = ["red", "green", "yellow", "blue"]
        path = engine.ludo_path()
        occupancy: dict[tuple[int, int], str] = {}
        for account_id, pawns in state.get("pawns", {}).items():
            color = str(state.get("colors", {}).get(account_id, "red"))
            start = int(state.get("starts", {}).get(account_id, 0))
            for pos in pawns:
                pos = int(pos)
                if pos < 0 or pos >= 58:
                    continue
                if pos < engine.LUDO_TRACK:
                    cell = path[(start + pos) % len(path)]
                else:
                    step = min(4, pos - engine.LUDO_TRACK)
                    cell = {
                        "red": (7, 1 + step),
                        "green": (1 + step, 7),
                        "yellow": (7, 13 - step),
                        "blue": (13 - step, 7),
                    }[color]
                occupancy[(cell[0], cell[1])] = color
        path_set = {cell: index for index, cell in enumerate(path)}
        grid: list[list[LudoCell]] = []
        for row in range(15):
            line: list[LudoCell] = []
            for col in range(15):
                kind = "empty"
                color = ""
                arrow = ""
                safe = False
                if row < 6 and col < 6:
                    kind, color = "home", colors[0]
                elif row < 6 and col > 8:
                    kind, color = "home", colors[1]
                elif row > 8 and col > 8:
                    kind, color = "home", colors[2]
                elif row > 8 and col < 6:
                    kind, color = "home", colors[3]
                elif 6 <= row <= 8 and 6 <= col <= 8:
                    kind, color = "center", "gold"
                elif (row, col) in path_set:
                    kind = "path"
                    index = path_set[(row, col)]
                    safe = index in engine.LUDO_SAFE
                    if index == 0:
                        arrow = "arrow-right"
                    elif index == 13:
                        arrow = "arrow-down"
                    elif index == 25:
                        arrow = "arrow-left"
                    elif index == 38:
                        arrow = "arrow-up"
                elif row == 7 and 1 <= col <= 5:
                    kind, color = "lane", colors[0]
                elif col == 7 and 1 <= row <= 5:
                    kind, color = "lane", colors[1]
                elif row == 7 and 9 <= col <= 13:
                    kind, color = "lane", colors[2]
                elif col == 7 and 9 <= row <= 13:
                    kind, color = "lane", colors[3]
                line.append(
                    {
                        "kind": kind,
                        "color": color,
                        "pawn": occupancy.get((row, col), ""),
                        "safe": safe,
                        "arrow": arrow,
                    }
                )
            grid.append(line)
        return grid

    def _points_grid(self, state: dict) -> list[list[PointCell]]:
        size = engine.DOT_SIZE
        boxes = engine.BOX_SIZE
        horizontal = state.get("h", [""] * (size * boxes))
        vertical = state.get("v", [""] * (boxes * size))
        owned = state.get("boxes", [""] * (boxes * boxes))
        grid: list[list[PointCell]] = []
        for grid_row in range(size * 2 - 1):
            line: list[PointCell] = []
            for grid_col in range(size * 2 - 1):
                if grid_row % 2 == 0 and grid_col % 2 == 0:
                    line.append(
                        {
                            "kind": "dot",
                            "index": -1,
                            "owner": "",
                            "claimable": False,
                        }
                    )
                elif grid_row % 2 == 0:
                    index = (grid_row // 2) * boxes + (grid_col // 2)
                    owner = (
                        str(horizontal[index])
                        if index < len(horizontal)
                        else ""
                    )
                    line.append(
                        {
                            "kind": "h",
                            "index": index,
                            "owner": owner,
                            "claimable": owner == "",
                        }
                    )
                elif grid_col % 2 == 0:
                    index = (grid_row // 2) * size + (grid_col // 2)
                    owner = (
                        str(vertical[index]) if index < len(vertical) else ""
                    )
                    line.append(
                        {
                            "kind": "v",
                            "index": index,
                            "owner": owner,
                            "claimable": owner == "",
                        }
                    )
                else:
                    index = (grid_row // 2) * boxes + (grid_col // 2)
                    line.append(
                        {
                            "kind": "box",
                            "index": index,
                            "owner": str(owned[index])
                            if index < len(owned)
                            else "",
                            "claimable": False,
                        }
                    )
            grid.append(line)
        return grid

    # ------------------------------------------------------- lobby projection
    def _lobby_capacity(self, rules: dict) -> tuple[int, int]:
        """Return (configured capacity, minimum humans) for this game."""
        try:
            wanted = int(
                rules.get("number_of_players") or self.max_players or 2
            )
        except (TypeError, ValueError):
            wanted = 2
        if self.slug == "domino":
            return (3 if wanted >= 3 else 2), 1
        if self.slug == "ludo":
            return max(2, min(4, max(wanted, int(self.max_players or 2)))), 2
        if self.slug == "loto":
            return max(2, min(80, int(self.max_players or wanted or 2))), 1
        return max(2, wanted), 2

    def _empty_slot(self, seat: int) -> LobbySlot:
        return {
            "seat": seat,
            "kind": "empty",
            "account_id": 0,
            "name": "En attente...",
            "avatar_url": "",
            "avatar_remote": False,
            "is_host": False,
            "is_online": False,
            "is_ready": False,
            "is_me": False,
            "can_remove": False,
            "cards": 0,
            "color": "",
        }

    def _build_lobby(self, rules: dict, me: int) -> None:
        """Project persisted room settings + seated members into seat rows."""
        self.lobby_mode = str(rules.get("game_mode", "classic"))
        target_score = rules.get("target_score") or rules.get("maty") or 50
        try:
            self.lobby_target_score = int(target_score)
        except (TypeError, ValueError):
            self.lobby_target_score = 50
        capacity, minimum = self._lobby_capacity(rules)
        self.lobby_target_players = capacity
        self.lobby_min_players = minimum
        specials: list[str] = []
        if rules.get("no_double_six"):
            specials.append("Sans Double-Six")
        if rules.get("one_on_blank"):
            specials.append("Un sur Blanc")
        self.lobby_special_rules = specials
        self.lobby_fill_bots = self.slug == "domino" and bool(
            rules.get("fill_with_bots")
        )
        # Ludo is always standard four pawns, whatever legacy rules stored.
        self.lobby_goal_pawns = engine.LUDO_PAWNS
        try:
            self.lobby_draw_seconds = max(
                5, min(120, int(rules.get("draw_seconds", 12)))
            )
        except (TypeError, ValueError):
            self.lobby_draw_seconds = 12
        if self.slug == "loto":
            tier = tier_by_key(str(rules.get("tier", "bronze")))
            self.lobby_tier_label = str(tier["label"])
            self.lobby_tier_max_cards = LOTO_MAX_CARDS

        # True persistent seat ordering: self.players already comes back
        # ordered by game_room_member.seat, id.
        humans = [p for p in self.players if p["account_id"] > 0]
        slots: list[LobbySlot] = []
        for index, player in enumerate(humans):
            slots.append(
                {
                    "seat": index + 1,
                    "kind": "player",
                    "account_id": player["account_id"],
                    "name": player["name"],
                    "avatar_url": player["avatar_url"],
                    "avatar_remote": player["avatar_remote"],
                    "is_host": player["is_host"],
                    "is_online": player["is_online"],
                    "is_ready": player["is_ready"],
                    "is_me": player["account_id"] == me,
                    "can_remove": (
                        self.is_host
                        and not player["is_host"]
                        and player["account_id"] != me
                    ),
                    "cards": int(player["cards"]),
                    "color": str(player["color"]),
                }
            )
        bot_used = 0
        if self.lobby_fill_bots:
            names = [str(b["name"]) for b in self._domino_bots(rules)]
            while len(slots) < capacity:
                bot_used += 1
                label = (
                    names[bot_used - 1]
                    if bot_used <= len(names)
                    else f"Bot {bot_used}"
                )
                slots.append(
                    {
                        "seat": len(slots) + 1,
                        "kind": "bot",
                        "account_id": 0,
                        "name": label,
                        "avatar_url": "",
                        "avatar_remote": False,
                        "is_host": False,
                        "is_online": True,
                        "is_ready": True,
                        "is_me": False,
                        "can_remove": False,
                        "cards": 0,
                        "color": "",
                    }
                )
        while len(slots) < capacity:
            slots.append(self._empty_slot(len(slots) + 1))
        self.lobby_slots = slots
        self.lobby_bot_count = bot_used
        self.lobby_human_count = len(humans)
        self.lobby_occupied = len(humans) + bot_used
        self.lobby_unready_count = sum(
            1 for p in humans if not p["is_ready"] and not p["is_host"]
        )
        self.lobby_ticket_total = sum(int(p["cards"]) for p in humans)
        self.lobby_my_tickets = sum(
            int(p["cards"]) for p in humans if p["account_id"] == me
        )
        self.lobby_host_name = next(
            (p["name"] for p in self.players if p["is_host"]), ""
        )
        self.my_ready = any(
            p["account_id"] == me and p["is_ready"] for p in self.players
        )

    # ---------------------------------------------------------------- sharing
    @rx.var
    def room_url(self) -> str:
        return str(self.router.url)

    @rx.event
    def copy_code(self):
        if not self.code:
            return rx.toast("Code indisponible.")
        yield rx.set_clipboard(self.code)
        yield rx.toast(f"Code {self.code} copie.")

    @rx.event
    def invite_players(self):
        url = str(self.router.url)
        code = self.code
        game = (self.game_name or "TATA").replace('"', "")
        script = (
            "(async () => {"
            f'  const url = "{url}";'
            f'  const code = "{code}";'
            f'  const game = "{game}";'
            '  const text = "Rejoins ma partie " + game + " TATA (code "'
            '    + code + ").";'
            "  try {"
            "    if (navigator.share) {"
            '      await navigator.share({title: game + " TATA", '
            "text: text, url: url});"
            "      return;"
            "    }"
            "  } catch (e) {}"
            "  try {"
            '    await navigator.clipboard.writeText(text + " " + url);'
            "  } catch (e) {}"
            "})()"
        )
        yield rx.call_script(script)
        yield rx.toast(
            "Invitation prete: lien de la salle partage ou copie.",
            duration=4000,
        )

    # ---------------------------------------------------------- room actions
    @rx.event
    async def toggle_ready(self):
        """Only an active member of a waiting/open room may toggle Pret."""
        auth = await self.get_state(AuthState)
        room_id = self.active_id
        async with rx.asession() as asession:
            room = (
                await asession.execute(
                    text("SELECT status FROM game_room WHERE id = :r"),
                    {"r": room_id},
                )
            ).first()
            if room is None:
                return rx.toast("Cette salle n'existe plus.")
            if str(room[0]) not in ("open", "waiting"):
                return rx.toast(
                    "Le statut Pret n'est modifiable qu'avant le lancement."
                )
            result = await asession.execute(
                text(
                    "UPDATE game_room_member SET is_ready = NOT is_ready "
                    "WHERE room_id = :r AND account_id = :a "
                    "AND left_at IS NULL"
                ),
                {"r": room_id, "a": auth.account_id},
            )
            if int(result.rowcount or 0) == 0:
                return rx.toast("Vous n'etes plus dans cette salle.")
            await self._event(
                asession,
                room_id,
                "ready",
                f"{auth.display_name} a change son statut Pret",
                auth.account_id,
            )
            await asession.commit()
        await self._refresh()
        return None

    @rx.event
    async def remove_player(self, account_id: int):
        """Host-only removal of a seated guest, before the match starts."""
        auth = await self.get_state(AuthState)
        me = auth.account_id
        room_id = self.active_id
        target = int(account_id)
        if target == me:
            return rx.toast("Utilisez Quitter pour sortir de la salle.")
        async with rx.asession() as asession:
            room = (
                await asession.execute(
                    text(
                        "SELECT status, host_id FROM game_room "
                        "WHERE id = :r FOR UPDATE"
                    ),
                    {"r": room_id},
                )
            ).first()
            if room is None:
                return rx.toast("Cette salle n'existe plus.")
            if int(room[1] or 0) != me:
                return rx.toast("Seul l'hote peut retirer un joueur.")
            if str(room[0]) not in ("open", "waiting"):
                return rx.toast(
                    "Impossible de retirer un joueur apres le lancement."
                )
            member = (
                await asession.execute(
                    text(
                        """
                        SELECT m.is_host,
                               COALESCE(p.display_name, a.username)
                        FROM game_room_member m
                        JOIN account a ON a.id = m.account_id
                        LEFT JOIN profile p ON p.account_id = a.id
                        WHERE m.room_id = :r AND m.account_id = :a
                          AND m.left_at IS NULL
                        """
                    ),
                    {"r": room_id, "a": target},
                )
            ).first()
            if member is None:
                return rx.toast("Ce joueur n'est plus dans la salle.")
            if bool(member[0]) or target == int(room[1] or 0):
                return rx.toast("L'hote ne peut pas etre retire.")
            name = str(member[1])
            await asession.execute(
                text(
                    "UPDATE game_room_member SET left_at = NOW(), "
                    "is_ready = false "
                    "WHERE room_id = :r AND account_id = :a "
                    "AND left_at IS NULL"
                ),
                {"r": room_id, "a": target},
            )
            await asession.execute(
                text(
                    """
                    UPDATE game_room SET player_count = (
                        SELECT COUNT(*) FROM game_room_member
                        WHERE room_id = :r AND left_at IS NULL),
                        updated_at = NOW()
                    WHERE id = :r
                    """
                ),
                {"r": room_id},
            )
            await self._event(
                asession,
                room_id,
                "leave",
                f"{name} a ete retire de la salle par l'hote",
                me,
            )
            await asession.commit()
        await self._refresh()
        return rx.toast(f"{name} a ete retire de la salle.")

    @rx.event
    async def leave_room(self):
        """Leave safely: a waiting host closes the room, never orphaning it."""
        auth = await self.get_state(AuthState)
        me = auth.account_id
        room_id = self.active_id
        slug = self.slug or "domino"
        closed = False
        async with rx.asession() as asession:
            room = (
                await asession.execute(
                    text(
                        "SELECT status, host_id FROM game_room "
                        "WHERE id = :r FOR UPDATE"
                    ),
                    {"r": room_id},
                )
            ).first()
            if room is None:
                self.polling = False
                yield rx.toast("Cette salle n'existe plus.")
                yield rx.redirect(f"/games/{slug}")
                return
            status = str(room[0])
            host_leaving = int(room[1] or 0) == me
            waiting = status in ("open", "waiting")
            if waiting and host_leaving:
                await asession.execute(
                    text(
                        "UPDATE game_room_member SET left_at = NOW() "
                        "WHERE room_id = :r AND left_at IS NULL"
                    ),
                    {"r": room_id},
                )
                await asession.execute(
                    text(
                        "UPDATE game_room SET status = 'closed', "
                        "player_count = 0, updated_at = NOW() "
                        "WHERE id = :r"
                    ),
                    {"r": room_id},
                )
                await self._event(
                    asession,
                    room_id,
                    "leave",
                    f"{auth.display_name} (hote) a ferme la salle d'attente",
                    me,
                )
                closed = True
            else:
                await asession.execute(
                    text(
                        "UPDATE game_room_member SET left_at = NOW(), "
                        "is_ready = false "
                        "WHERE room_id = :r AND account_id = :a "
                        "AND left_at IS NULL"
                    ),
                    {"r": room_id, "a": me},
                )
                await asession.execute(
                    text(
                        """
                        UPDATE game_room SET player_count = (
                            SELECT COUNT(*) FROM game_room_member
                            WHERE room_id = :r AND left_at IS NULL),
                            updated_at = NOW()
                        WHERE id = :r
                        """
                    ),
                    {"r": room_id},
                )
                detail = (
                    f"{auth.display_name} a quitte la partie en cours"
                    if not waiting
                    else f"{auth.display_name} a quitte la salle"
                )
                await self._event(asession, room_id, "leave", detail, me)
            await asession.commit()
        self.polling = False
        self.active_id = 0
        if closed:
            yield rx.toast(
                "Salle d'attente fermee: tous les joueurs ont ete liberes."
            )
        else:
            yield rx.toast("Vous avez quitte la partie.")
        yield rx.redirect(f"/games/{slug}")

    @rx.event
    async def send_reaction(self, emoji: str, label: str):
        auth = await self.get_state(AuthState)
        async with rx.asession() as asession:
            await asession.execute(
                text(
                    """
                    INSERT INTO game_reaction (room_id, account_id, emoji,
                        label, round_number, expires_at, created_at)
                    VALUES (:r, :a, :e, :l, :n,
                        NOW() + INTERVAL '20 seconds', NOW())
                    """
                ),
                {
                    "r": self.active_id,
                    "a": auth.account_id,
                    "e": emoji,
                    "l": label,
                    "n": self.round_number,
                },
            )
            await asession.commit()
        await self._refresh()

    @rx.event
    def set_reaction_tab(self, tab: str):
        self.reaction_tab = tab

    @rx.event
    async def start_match(self):
        auth = await self.get_state(AuthState)
        me = auth.account_id
        async with rx.asession() as asession:
            room = await self._ctx(asession, self.active_id, lock=True)
            if room is None:
                return rx.toast("Salle introuvable.")
            if int(room[8]) != me:
                return rx.toast("Seul l'hote peut lancer la partie.")
            if str(room[2]) not in ("open", "waiting"):
                return rx.toast("La partie a deja commence.")
            order = await self._order(asession, self.active_id)
            slug = str(room[7])
            rules = json.loads(str(room[1]) or "{}")
            minimum = 1 if slug in ("loto", "domino") else 2
            if len(order) < minimum:
                return rx.toast(f"Il faut au moins {minimum} joueur(s).")
            members = (
                await asession.execute(
                    text(
                        "SELECT account_id, is_ready, is_host "
                        "FROM game_room_member "
                        "WHERE room_id = :r AND left_at IS NULL"
                    ),
                    {"r": self.active_id},
                )
            ).all()
            unready = [
                int(m[0])
                for m in members
                if not bool(m[1]) and int(m[0]) != me and not bool(m[2])
            ]
            if unready and slug in ("domino", "ludo", "loto"):
                return rx.toast(
                    f"{len(unready)} joueur(s) ne sont pas prets: "
                    "attendez leur confirmation ou retirez-les."
                )
            version = int(room[3] or 0)
            rules_update: dict | None = None
            if slug == "loto":
                cards = (
                    await asession.execute(
                        text(
                            "SELECT COUNT(*) FROM bingo_card "
                            "WHERE room_id = :r AND is_void = false"
                        ),
                        {"r": self.active_id},
                    )
                ).first()
                if int(cards[0] or 0) == 0:
                    return rx.toast(
                        "Achetez au moins un carton avant le tirage."
                    )
                holders = (
                    await asession.execute(
                        text(
                            "SELECT COUNT(DISTINCT account_id) "
                            "FROM bingo_card WHERE room_id = :r "
                            "AND is_void = false"
                        ),
                        {"r": self.active_id},
                    )
                ).first()
                if int(holders[0] or 0) == 0:
                    return rx.toast("Aucun joueur ne detient de carton valide.")
                state = engine.loto_initial_state()
                state["phase"] = "playing"
                seconds = int(rules.get("draw_seconds", 12))
            elif slug == "domino":
                try:
                    wanted = int(
                        rules.get("number_of_players") or int(room[10] or 2)
                    )
                except (TypeError, ValueError):
                    wanted = 2
                wanted = 3 if wanted >= 3 else 2
                fill = bool(rules.get("fill_with_bots"))
                humans = list(order)
                if len(humans) > wanted:
                    return rx.toast(
                        f"Trop de joueurs: {wanted} place(s) configuree(s)."
                    )
                missing = wanted - len(humans)
                if missing > 0 and not fill:
                    return rx.toast(
                        f"Il manque {missing} joueur(s): activez les bots "
                        "ou attendez les joueurs manquants."
                    )
                bots = [
                    {"id": -(index + 1), "name": f"Bot {index + 1}"}
                    for index in range(missing)
                ]
                participants = humans + [int(b["id"]) for b in bots]
                if len(participants) != wanted:
                    return rx.toast("Configuration de joueurs invalide.")
                target = engine.domino_target_score(rules)
                state = engine.domino_initial_state(participants, rules)
                seconds = engine.domino_turn_seconds(rules)
                created = room[20]
                rules_update = {
                    **rules,
                    "game_mode": engine.domino_mode(rules),
                    "target_score": target,
                    "maty": target,
                    "number_of_players": wanted,
                    "no_double_six": bool(rules.get("no_double_six")),
                    "one_on_blank": bool(rules.get("one_on_blank")),
                    "fill_with_bots": fill,
                    "bots": bots,
                    "order": participants,
                    "game_state": "playing",
                    "created_at": created.isoformat()
                    if created is not None
                    else str(rules.get("created_at", "")),
                }
            elif slug == "ludo":
                try:
                    capacity = int(
                        rules.get("number_of_players") or int(room[10] or 4)
                    )
                except (TypeError, ValueError):
                    capacity = 4
                capacity = max(2, min(4, capacity))
                if len(order) < 2:
                    return rx.toast("Ludo demande au moins 2 joueurs humains.")
                if len(order) > capacity:
                    return rx.toast(
                        f"Trop de joueurs: {capacity} place(s) configuree(s)."
                    )
                # Normalise legacy goal_pawns to the standard four pawns
                # in both rules and state, without any schema migration.
                rules = engine.ludo_normalize_rules(rules)
                rules_update = rules
                state = engine.ludo_initial_state(order, rules)
                seconds = 30
            elif slug == "faritany":
                state = engine.faritany_initial_state(order)
                seconds = 15
            elif slug == "points":
                state = engine.points_initial_state(order)
                seconds = 15
            elif slug == "rami":
                state = engine.cards_initial_state(order, 2, 7)
                seconds = 30
            elif slug == "tri":
                state = engine.cards_initial_state(order, 7, 5)
                seconds = 30
            else:
                state = engine.billard_initial_state(order)
                seconds = 45
            turn = 0 if slug == "loto" else int(state.get("turn", order[0]))
            ok = await self._write(
                asession,
                self.active_id,
                version,
                state,
                status="active",
                turn=turn or None,
                deadline_seconds=seconds,
                round_number=1,
                rules=rules_update,
                kind="start",
                payload={"players": len(order)},
                actor=me,
            )
            if not ok:
                return rx.toast("Etat modifie entre-temps, reessayez.")
            await self._event(
                asession,
                self.active_id,
                "start",
                f"Partie lancee par {auth.display_name}",
                me,
            )
            await asession.commit()
        if slug == "domino":
            await self._run_bots()
        await self._refresh()
        return rx.toast("La partie commence !")

    # ------------------------------------------------------------------ LOTO
    @rx.event
    def set_buy_count(self, value: float | int):
        """Server-side clamp: every tier allows exactly 1 to 5 tickets."""
        try:
            self.buy_count = max(
                LOTO_MIN_CARDS, min(LOTO_MAX_CARDS, int(value))
            )
        except (TypeError, ValueError):
            self.buy_count = LOTO_MIN_CARDS

    @rx.event
    async def buy_cards(self):
        auth = await self.get_state(AuthState)
        me = auth.account_id
        count = max(LOTO_MIN_CARDS, min(LOTO_MAX_CARDS, self.buy_count))
        async with rx.asession() as asession:
            room = await self._ctx(asession, self.active_id, lock=True)
            if room is None or str(room[7]) != "loto":
                return rx.toast("Achat indisponible.")
            if str(room[2]) not in ("open", "waiting"):
                return rx.toast("Les cartons se prennent avant le tirage.")
            rules = json.loads(str(room[1]) or "{}")
            tier = tier_by_key(str(rules.get("tier", "bronze")))
            price = 0
            allowance = LOTO_MAX_CARDS
            existing = (
                await asession.execute(
                    text(
                        "SELECT COALESCE(MAX(card_index), 0), COUNT(*) "
                        "FROM bingo_card WHERE room_id = :r "
                        "AND account_id = :a AND is_void = false"
                    ),
                    {"r": self.active_id, "a": me},
                )
            ).first()
            owned = int(existing[1] or 0)
            if owned + count > allowance:
                return rx.toast(
                    f"Maximum {allowance} carton(s) par joueur "
                    f"({tier['label']})."
                )
            total = 0
            rng = random.Random()
            next_index = int(existing[0] or 0)
            for offset in range(count):
                next_index += 1
                grid = engine.generate_loto_card(rng)
                await asession.execute(
                    text(
                        """
                        INSERT INTO bingo_card (room_id, account_id,
                            card_index, grid_json, marked_json, marked_count,
                            row_progress_json, price_coins, tier,
                            claimed_quine, claimed_double_quine,
                            claimed_full_house, is_void, created_at,
                            updated_at)
                        VALUES (:r, :a, :i, :grid, '[]', 0, '[0, 0, 0]',
                            :price, :tier, false, false, false, false,
                            NOW(), NOW())
                        """
                    ),
                    {
                        "r": self.active_id,
                        "a": me,
                        "i": next_index,
                        "grid": json.dumps(grid),
                        "price": price,
                        "tier": str(tier["key"]),
                    },
                )
            await self._event(
                asession,
                self.active_id,
                "buy_card",
                f"{auth.display_name} a pris {count} carton(s)",
                me,
            )
            await asession.commit()
        await self._refresh()
        return rx.toast(f"{count} carton(s) ajoute(s).")

    async def _loto_draw_once(
        self, manual: bool
    ) -> tuple[bool, list[str], int, str]:
        """Draw exactly one ball, concurrency-safe under polling.

        The room row is locked FOR UPDATE, the state write is guarded by the
        optimistic state_version and every payout uses an idempotent key, so
        only one caller can ever win a given draw or award.
        """
        auth = await self.get_state(AuthState)
        me = auth.account_id
        async with rx.asession() as asession:
            room = await self._ctx(asession, self.active_id, lock=True)
            if room is None or str(room[7]) != "loto":
                return False, [], 0, "Tirage indisponible."
            if str(room[2]) not in ("active", "in_progress"):
                return False, [], 0, "La partie n'est pas en cours."
            deadline = room[17]
            if deadline is not None:
                left = (
                    await asession.execute(
                        text(
                            "SELECT CAST(EXTRACT(EPOCH FROM (:d - NOW())) "
                            "AS INTEGER)"
                        ),
                        {"d": deadline},
                    )
                ).first()
                if int(left[0] or 0) > 0:
                    host_override = manual and int(room[8] or 0) == me
                    if not host_override:
                        return False, [], 0, "Attendez la fin du minuteur."
            state = json.loads(str(room[0]) or "{}")
            rules = json.loads(str(room[1]) or "{}")
            version = int(room[3] or 0)
            pot = int(room[6] or 0)
            try:
                state, number = engine.loto_draw(state)
            except engine.MoveError as exc:
                logging.exception("Loto draw exhausted")
                return False, [], 0, str(exc)
            drawn = state["drawn"]
            claims = list(state.get("claims", []))

            cards = (
                await asession.execute(
                    text(
                        """
                        SELECT bc.id, bc.account_id, bc.grid_json,
                               bc.claimed_quine, bc.claimed_double_quine,
                               bc.claimed_full_house,
                               COALESCE(p.display_name, a.username)
                        FROM bingo_card bc
                        JOIN account a ON a.id = bc.account_id
                        LEFT JOIN profile p ON p.account_id = a.id
                        WHERE bc.room_id = :r AND bc.is_void = false
                        ORDER BY bc.id
                        """
                    ),
                    {"r": self.active_id},
                )
            ).all()
            net_pot = 0
            winner_id = 0
            announcements: list[str] = []
            for card in cards:
                card_id = int(card[0])
                account_id = int(card[1])
                grid = json.loads(str(card[2]) or "[]")
                rows, marked, remaining = engine.loto_card_progress(grid, drawn)
                complete_rows = sum(1 for r in rows if r == 5)
                await asession.execute(
                    text(
                        """
                        UPDATE bingo_card
                        SET marked_json = :marked, marked_count = :count,
                            row_progress_json = :rows, updated_at = NOW()
                        WHERE id = :id
                        """
                    ),
                    {
                        "marked": json.dumps(
                            [
                                v
                                for row in grid
                                for v in row
                                if v and v in set(drawn)
                            ]
                        ),
                        "count": marked,
                        "rows": json.dumps(rows),
                        "id": card_id,
                    },
                )
                tiers_hit: list[tuple[str, str, int, int]] = []
                if complete_rows >= 1 and not bool(card[3]):
                    tiers_hit.append(("quine", "claimed_quine", 20, card_id))
                if complete_rows >= 2 and not bool(card[4]):
                    tiers_hit.append(
                        ("double_quine", "claimed_double_quine", 30, card_id)
                    )
                if marked == 15 and not bool(card[5]):
                    tiers_hit.append(
                        ("full_house", "claimed_full_house", 50, card_id)
                    )
                for key, column, share, cid in tiers_hit:
                    amount = 0
                    await asession.execute(
                        text(
                            f"UPDATE bingo_card SET {column} = true, "
                            f"{column}_at = NOW() WHERE id = :id"
                        ),
                        {"id": cid},
                    )
                    label = loto_claim_label(key)
                    claims.append(
                        {
                            "kind": key,
                            "name": str(card[6]),
                            "amount": 0,
                        }
                    )
                    announcements.append(f"{label}: {card[6]}")
                    await self._log(
                        asession,
                        self.active_id,
                        f"claim_{key}",
                        {
                            "name": str(card[6]),
                            "amount": 0,
                            "card": cid,
                        },
                        version + 1,
                        int(room[5] or 0),
                        account_id,
                    )
                    await self._event(
                        asession,
                        self.active_id,
                        "claim",
                        f"{label} pour {card[6]}",
                        account_id,
                    )
                    if key == "full_house":
                        winner_id = account_id
            state["claims"] = claims
            exhausted = engine.loto_exhausted(state)
            if not winner_id and exhausted:
                best = (
                    await asession.execute(
                        text(
                            "SELECT account_id FROM bingo_card "
                            "WHERE room_id = :r AND is_void = false "
                            "ORDER BY marked_count DESC, id LIMIT 1"
                        ),
                        {"r": self.active_id},
                    )
                ).first()
                winner_id = int(best[0]) if best is not None else 0
            ok = await self._write(
                asession,
                self.active_id,
                version,
                state,
                deadline_seconds=int(rules.get("draw_seconds", 12)),
                kind="draw",
                payload={"number": number},
                actor=None,
            )
            if not ok:
                return False, [], 0, "Tirage concurrent detecte, reessayez."
            await self._event(
                asession, self.active_id, "draw", f"Boule {number}", None
            )
            if winner_id or exhausted:
                await asession.execute(
                    text(
                        """
                        UPDATE game_room
                        SET status = 'finished', winner_account_id = :w,
                            settled_at = NOW(), finished_at = NOW(),
                            turn_deadline_at = NULL, updated_at = NOW()
                        WHERE id = :r
                        """
                    ),
                    {"w": winner_id, "r": self.active_id},
                )
                if winner_id:
                    await self._stats(
                        asession, self.active_id, int(room[16]), winner_id
                    )
                await self._event(
                    asession,
                    self.active_id,
                    "settle",
                    (
                        f"{loto_claim_label('full_house')} remporte: tirage "
                        "termine"
                        if not exhausted
                        else "90 boules tirees: tirage termine"
                    ),
                    None,
                )
            await asession.commit()
        return True, announcements, number, ""

    @rx.event
    async def draw_number(self):
        """Guarded manual fallback: the host may advance the draw early."""
        ok, announcements, number, message = await self._loto_draw_once(
            manual=True
        )
        if not ok:
            return rx.toast(message or "Tirage impossible.")
        await self._refresh(allow_bots=False)
        if announcements:
            return rx.toast(" | ".join(announcements), duration=6000)
        return rx.toast(f"Boule {number}")

    # ---------------------------------------------------------------- DOMINO
    async def _next_turn(
        self, order: list[int], current: int, skip: int = 1
    ) -> int:
        if not order:
            return 0
        if current not in order:
            return order[0]
        return order[(order.index(current) + skip) % len(order)]

    @rx.event
    async def domino_play(self, index: int, side: str):
        return await RoomState._domino_action("place", index, side)

    @rx.event
    async def domino_auto_play(self, index: int):
        """Rush Auto: the server resolves the legal side deterministically."""
        return await RoomState._domino_action("place", index, "auto")

    @rx.event
    async def domino_draw(self):
        return await RoomState._domino_action("draw", 0, "")

    @rx.event
    async def domino_pass(self):
        return await RoomState._domino_action("pass", 0, "")

    async def _domino_progress(
        self,
        asession,
        room,
        state: dict,
        actor: int,
        order: list[int],
        rules: dict,
        version: int,
        kind: str,
        payload: dict[str, Any],
        drew: bool = False,
    ) -> tuple[bool, str, bool]:
        """Persist one accepted Domino step: turn, round, target, settlement.

        Returns (written, round_note, match_finished).
        """
        room_id = self.active_id
        target = engine.domino_target_score(rules)
        seconds = engine.domino_turn_seconds(rules)
        round_over = engine.domino_round_over(state, order)
        extra = bool(state.get("extra_turn"))
        if drew and not round_over:
            turn = actor
        elif extra and not round_over:
            turn = actor
        else:
            turn = engine.domino_next(order, actor)
        note = ""
        winner_id = 0
        finished = False
        if round_over:
            winner_id, points = engine.domino_round_result(state, order)
            scores = dict(state.get("scores", {}))
            scores[str(winner_id)] = int(scores.get(str(winner_id), 0)) + points
            state = dict(state)
            state["scores"] = scores
            state["extra_turn"] = False
            note = f"Manche gagnee: +{points} score (objectif {target})"
            await self._log(
                asession,
                room_id,
                "round_end",
                {"name": str(winner_id), "amount": points},
                version + 1,
                int(room[5] or 0),
                winner_id if winner_id > 0 else None,
            )
            if int(scores[str(winner_id)]) >= target:
                state["phase"] = "finished"
                state["target"] = target
                turn = winner_id
                finished = True
            else:
                carried = scores
                state = engine.domino_initial_state(order, rules, carried)
                state["round"] = int(room[5] or 0) + 1
                turn = int(state["turn"])
        ok = await self._write(
            asession,
            room_id,
            version,
            state,
            turn=turn,
            deadline_seconds=seconds,
            round_number=(int(room[5] or 0) + 1) if round_over else None,
            kind=kind,
            payload=payload,
            actor=actor if actor > 0 else None,
        )
        if not ok:
            return False, "", False
        if note:
            await self._event(
                asession,
                room_id,
                "round_end",
                note,
                actor if actor > 0 else None,
            )
        if finished and winner_id:
            await self._settle(
                asession,
                room_id,
                int(room[16]),
                winner_id,
                int(room[6] or 0),
                "DOMINO",
            )
        return True, note, finished

    async def _run_bots(self, limit: int = 24) -> bool:
        """Authoritative bounded bot runner: plays every pending bot turn."""
        acted = False
        for _ in range(limit):
            async with rx.asession() as asession:
                room = await self._ctx(asession, self.active_id, lock=True)
                if room is None or str(room[7]) != "domino":
                    return acted
                if str(room[2]) not in ("active", "in_progress"):
                    return acted
                actor = int(room[4] or 0)
                if actor >= 0:
                    return acted
                state = json.loads(str(room[0]) or "{}")
                rules = json.loads(str(room[1]) or "{}")
                humans = await self._order(asession, self.active_id)
                order = self._domino_order(rules, humans)
                version = int(room[3] or 0)
                if actor not in order:
                    return acted
                try:
                    state, note = engine.domino_bot_turn(state, actor, rules)
                except engine.MoveError:
                    logging.exception("Bot turn failed")
                    return acted
                ok, _, finished = await self._domino_progress(
                    asession,
                    room,
                    state,
                    actor,
                    order,
                    rules,
                    version,
                    "bot_move",
                    {"bot": actor, "note": note},
                )
                if not ok:
                    return acted
                await self._event(
                    asession, self.active_id, "bot_move", note, None
                )
                await asession.commit()
                acted = True
                if finished:
                    return acted
            await asyncio.sleep(0)
        return acted

    async def _domino_action(self, mode: str, index: int, side: str):
        auth = await self.get_state(AuthState)
        me = auth.account_id
        note = ""
        async with rx.asession() as asession:
            room = await self._ctx(asession, self.active_id, lock=True)
            if room is None or str(room[7]) != "domino":
                return rx.toast("Action indisponible.")
            if str(room[2]) not in ("active", "in_progress"):
                return rx.toast("La partie n'est pas en cours.")
            if int(room[4] or 0) != me:
                return rx.toast("Ce n'est pas votre tour.")
            state = json.loads(str(room[0]) or "{}")
            rules = json.loads(str(room[1]) or "{}")
            humans = await self._order(asession, self.active_id)
            order = self._domino_order(rules, humans)
            version = int(room[3] or 0)
            game_mode = engine.domino_mode(rules)
            try:
                if mode == "place":
                    chosen = side
                    if game_mode == "rush_auto" and side not in (
                        "left",
                        "right",
                    ):
                        chosen = "auto"
                    state = engine.domino_place(state, me, index, chosen, rules)
                elif mode == "draw":
                    state = engine.domino_draw(state, me)
                else:
                    state = engine.domino_pass(state, me)
            except engine.MoveError as exc:
                logging.exception("Invalid domino move")
                return rx.toast(str(exc))
            ok, note, _ = await self._domino_progress(
                asession,
                room,
                state,
                me,
                order,
                rules,
                version,
                "place_tile"
                if mode == "place"
                else ("draw_tile" if mode == "draw" else "pass_turn"),
                {"index": index, "side": side},
                drew=mode == "draw",
            )
            if not ok:
                return rx.toast("Plateau modifie entre-temps, reessayez.")
            await asession.commit()
        await self._run_bots()
        await self._refresh()
        if note:
            self.round_result_open = True
            self.round_result_text = note
        return None

    @rx.event
    def close_round_result(self):
        self.round_result_open = False

    # ------------------------------------------ chat / audio / history tools
    @rx.event
    async def send_chat(self, form_data: dict[str, Any]):
        """Compact room chat stored as game_room_event(event_type='chat')."""
        auth = await self.get_state(AuthState)
        body = " ".join(str(form_data.get("message", "")).split())[:240]
        if not body:
            return rx.toast("Ecrivez un message avant d'envoyer.")
        if self.active_id == 0:
            return rx.toast("Salle introuvable.")
        async with rx.asession() as asession:
            member = (
                await asession.execute(
                    text(
                        "SELECT 1 FROM game_room_member "
                        "WHERE room_id = :r AND account_id = :a "
                        "AND left_at IS NULL"
                    ),
                    {"r": self.active_id, "a": auth.account_id},
                )
            ).first()
            if member is None:
                return rx.toast("Seuls les joueurs de la salle peuvent ecrire.")
            await self._event(
                asession, self.active_id, "chat", body, auth.account_id
            )
            await asession.commit()
        await self._refresh(allow_bots=False)
        return None

    @rx.event
    def toggle_audio(self):
        self.audio_on = not self.audio_on

    @rx.event
    def toggle_history(self):
        self.history_open = not self.history_open
        if self.history_open:
            self.replay_open = False

    @rx.event
    def open_replay(self):
        self.replay_open = True
        self.history_open = True
        self.result_dismissed = True

    @rx.event
    def close_replay(self):
        self.replay_open = False

    @rx.event
    def dismiss_result(self):
        self.result_dismissed = True

    @rx.event
    async def rematch(self):
        """Open a brand new waiting room with identical settings.

        The finished room is never reset and never settled twice: a new room
        is created with a fresh unique code and the caller joins it as host
        through the normal room lifecycle, so nobody is charged silently.
        """
        auth = await self.get_state(AuthState)
        me = auth.account_id
        if me == 0:
            yield rx.redirect("/login")
            return
        new_id = 0
        new_code = ""
        async with rx.asession() as asession:
            room = await self._ctx(asession, self.active_id)
            if room is None:
                yield rx.toast("Cette salle n'existe plus.")
                return
            if str(room[2]) != "finished":
                yield rx.toast("La revanche s'ouvre apres la fin de la partie.")
                return
            rules = json.loads(str(room[1]) or "{}")
            for volatile in ("bots", "order", "game_state", "created_at"):
                rules.pop(volatile, None)
            base_name = str(room[12]) or str(room[13])
            for _ in range(10):
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
                            INSERT INTO game_room (game_id, host_id, code,
                                name, status, is_private, password_hash,
                                max_players, player_count, entry_coins,
                                rules_json, state_json, round_number,
                                pot_coins, state_version, created_at,
                                updated_at)
                            VALUES (:g, :h, :code, :name, 'waiting', false,
                                '', :max_players, 0, :entry, :rules, '{}', 0,
                                0, 0, NOW(), NOW())
                            RETURNING id
                            """
                        ),
                        {
                            "g": int(room[16]),
                            "h": me,
                            "code": code,
                            "name": f"Revanche - {base_name}"[:80],
                            "max_players": max(2, int(room[10] or 2)),
                            "entry": int(room[9] or 0),
                            "rules": json.dumps(rules),
                        },
                    )
                ).first()
                new_id = int(inserted[0])
                new_code = code
                break
            if not new_id:
                await asession.rollback()
                yield rx.toast("Impossible de creer la revanche. Reessayez.")
                return
            await self._event(
                asession,
                self.active_id,
                "system",
                f"{auth.display_name} a ouvert une revanche (code {new_code})",
                me,
            )
            await asession.commit()
        from app.states.games_state import GamesState

        self.polling = False
        self.active_id = 0
        yield rx.toast(
            f"Salle de revanche {new_code} creee: invitez vos adversaires.",
            duration=6000,
        )
        yield GamesState.join_room(new_id, "")

    # ------------------------------------------------------------------ LUDO
    @rx.event
    async def ludo_roll(self):
        auth = await self.get_state(AuthState)
        me = auth.account_id
        async with rx.asession() as asession:
            room = await self._ctx(asession, self.active_id, lock=True)
            if room is None or int(room[4] or 0) != me:
                return rx.toast("Ce n'est pas votre tour.")
            state = json.loads(str(room[0]) or "{}")
            version = int(room[3] or 0)
            try:
                state = engine.ludo_roll(state, me)
            except engine.MoveError as exc:
                logging.exception("Unexpected error")
                return rx.toast(str(exc))
            order = await self._order(asession, self.active_id)
            turn = me
            if not engine.ludo_legal_pawns(state, me):
                state["dice"] = 0
                state["rolled"] = False
                state["last"] = "aucun coup possible"
                turn = await self._next_turn(order, me)
            ok = await self._write(
                asession,
                self.active_id,
                version,
                state,
                turn=turn,
                deadline_seconds=30,
                kind="roll_dice",
                payload={"dice": state.get("dice", 0)},
                actor=me,
            )
            if not ok:
                return rx.toast("Reessayez.")
            await asession.commit()
        await self._refresh()
        return None

    @rx.event
    async def ludo_move(self, pawn_index: int):
        auth = await self.get_state(AuthState)
        me = auth.account_id
        async with rx.asession() as asession:
            room = await self._ctx(asession, self.active_id, lock=True)
            if room is None or int(room[4] or 0) != me:
                return rx.toast("Ce n'est pas votre tour.")
            state = json.loads(str(room[0]) or "{}")
            version = int(room[3] or 0)
            dice = int(state.get("dice", 0))
            try:
                state, note = engine.ludo_move(state, me, pawn_index)
            except engine.MoveError as exc:
                logging.exception("Unexpected error")
                return rx.toast(str(exc))
            order = await self._order(asession, self.active_id)
            winner_id = engine.ludo_winner(state)
            turn = (
                me
                if dice == 6 and not winner_id
                else await self._next_turn(order, me)
            )
            ok = await self._write(
                asession,
                self.active_id,
                version,
                state,
                turn=turn,
                deadline_seconds=30,
                kind="capture" if note else "move_piece",
                payload={"pawn": pawn_index},
                actor=me,
            )
            if not ok:
                return rx.toast("Reessayez.")
            if note:
                await self._event(
                    asession, self.active_id, "capture", "Capture !", me
                )
            if winner_id:
                await self._settle(
                    asession,
                    self.active_id,
                    int(room[16]),
                    winner_id,
                    int(room[6] or 0),
                    "LUDO",
                )
            await asession.commit()
            await self._refresh()
        return None

    # -------------------------------------------------------------- FARITANY
    @rx.event
    async def faritany_click(self, index: int):
        auth = await self.get_state(AuthState)
        me = auth.account_id
        if self.turn_account_id != me:
            return rx.toast("Ce n'est pas votre tour.")
        cells: list[str] = []
        for row in self.faritany_rows:
            for node in row:
                cells.append(node["owner"])
        if self.selected_node < 0:
            if index < len(cells) and cells[index] == str(me):
                self.selected_node = index
                await self._refresh()
                return None
            return rx.toast("Selectionnez un de vos pions.")
        origin = self.selected_node
        self.selected_node = -1
        async with rx.asession() as asession:
            room = await self._ctx(asession, self.active_id, lock=True)
            if room is None or int(room[4] or 0) != me:
                return rx.toast("Ce n'est pas votre tour.")
            state = json.loads(str(room[0]) or "{}")
            version = int(room[3] or 0)
            try:
                state = engine.faritany_move(state, me, origin, index)
            except engine.MoveError as exc:
                logging.exception("Unexpected error")
                return rx.toast(str(exc))
            order = await self._order(asession, self.active_id)
            opponent = await self._next_turn(order, me)
            remaining = sum(1 for c in state["cells"] if c == str(opponent))
            winner_id = 0
            if remaining == 0 or not engine.faritany_has_moves(state, opponent):
                winner_id = me
            ok = await self._write(
                asession,
                self.active_id,
                version,
                state,
                turn=opponent,
                deadline_seconds=15,
                kind="move_piece",
                payload={"from": origin, "to": index},
                actor=me,
            )
            if not ok:
                return rx.toast("Reessayez.")
            if winner_id:
                await self._settle(
                    asession,
                    self.active_id,
                    int(room[16]),
                    winner_id,
                    int(room[6] or 0),
                    "FARITANY",
                )
            await asession.commit()
        await self._refresh()
        return None

    # ---------------------------------------------------------------- POINTS
    @rx.event
    async def points_claim(self, kind: str, index: int):
        auth = await self.get_state(AuthState)
        me = auth.account_id
        async with rx.asession() as asession:
            room = await self._ctx(asession, self.active_id, lock=True)
            if room is None or int(room[4] or 0) != me:
                return rx.toast("Ce n'est pas votre tour.")
            state = json.loads(str(room[0]) or "{}")
            version = int(room[3] or 0)
            try:
                state, closed = engine.points_claim(state, me, kind, index)
            except engine.MoveError as exc:
                logging.exception("Unexpected error")
                return rx.toast(str(exc))
            order = await self._order(asession, self.active_id)
            turn = me if closed else await self._next_turn(order, me)
            winner_id = 0
            if engine.points_finished(state):
                scores = state.get("scores", {})
                best = max(scores, key=lambda k: int(scores[k]))
                winner_id = int(best)
            ok = await self._write(
                asession,
                self.active_id,
                version,
                state,
                turn=turn,
                deadline_seconds=15,
                kind="close_box" if closed else "draw_line",
                payload={"kind": kind, "index": index},
                actor=me,
            )
            if not ok:
                return rx.toast("Reessayez.")
            if winner_id:
                await self._settle(
                    asession,
                    self.active_id,
                    int(room[16]),
                    winner_id,
                    int(room[6] or 0),
                    "JEUX DE POINT",
                )
            await asession.commit()
        await self._refresh()
        return None

    # ------------------------------------------------------------ RAMI / TRI
    @rx.event
    def toggle_card(self, index: int):
        selected = list(self.selected_cards)
        if index in selected:
            selected.remove(index)
        else:
            selected.append(index)
        self.selected_cards = selected
        self.my_hand = [
            {
                "index": card["index"],
                "label": card["label"],
                "red": card["red"],
                "selected": card["index"] in selected,
            }
            for card in self.my_hand
        ]

    @rx.event
    async def cards_draw(self, source: str):
        auth = await self.get_state(AuthState)
        me = auth.account_id
        async with rx.asession() as asession:
            room = await self._ctx(asession, self.active_id, lock=True)
            if room is None or int(room[4] or 0) != me:
                return rx.toast("Ce n'est pas votre tour.")
            state = json.loads(str(room[0]) or "{}")
            version = int(room[3] or 0)
            try:
                state = engine.cards_draw(state, me, source)
            except engine.MoveError as exc:
                logging.exception("Unexpected error")
                return rx.toast(str(exc))
            ok = await self._write(
                asession,
                self.active_id,
                version,
                state,
                turn=me,
                deadline_seconds=30,
                kind="draw",
                payload={"source": source},
                actor=me,
            )
            if not ok:
                return rx.toast("Reessayez.")
            await asession.commit()
        self.selected_cards = []
        await self._refresh()
        return None

    @rx.event
    async def cards_discard(self):
        auth = await self.get_state(AuthState)
        me = auth.account_id
        if not self.selected_cards:
            return rx.toast("Selectionnez une carte a defausser.")
        index = self.selected_cards[0]
        async with rx.asession() as asession:
            room = await self._ctx(asession, self.active_id, lock=True)
            if room is None or int(room[4] or 0) != me:
                return rx.toast("Ce n'est pas votre tour.")
            state = json.loads(str(room[0]) or "{}")
            version = int(room[3] or 0)
            try:
                state = engine.cards_discard(state, me, index)
            except engine.MoveError as exc:
                logging.exception("Unexpected error")
                return rx.toast(str(exc))
            order = await self._order(asession, self.active_id)
            winner_id = me if len(state["hands"].get(str(me), [])) == 0 else 0
            ok = await self._write(
                asession,
                self.active_id,
                version,
                state,
                turn=await self._next_turn(order, me),
                deadline_seconds=30,
                kind="discard",
                payload={"index": index},
                actor=me,
            )
            if not ok:
                return rx.toast("Reessayez.")
            if winner_id:
                await self._settle(
                    asession,
                    self.active_id,
                    int(room[16]),
                    winner_id,
                    int(room[6] or 0),
                    self.game_name,
                )
            await asession.commit()
            self.selected_cards = []
        await self._refresh()
        return None

    @rx.event
    async def cards_meld(self):
        auth = await self.get_state(AuthState)
        me = auth.account_id
        if len(self.selected_cards) < 3:
            return rx.toast("Selectionnez au moins 3 cartes.")
        async with rx.asession() as asession:
            room = await self._ctx(asession, self.active_id, lock=True)
            if room is None or int(room[4] or 0) != me:
                return rx.toast("Ce n'est pas votre tour.")
            state = json.loads(str(room[0]) or "{}")
            version = int(room[3] or 0)
            try:
                state = engine.cards_meld(state, me, list(self.selected_cards))
            except engine.MoveError as exc:
                logging.exception("Unexpected error")
                return rx.toast(str(exc))
            winner_id = me if len(state["hands"].get(str(me), [])) == 0 else 0
            ok = await self._write(
                asession,
                self.active_id,
                version,
                state,
                turn=me,
                deadline_seconds=30,
                kind="meld",
                payload={"cards": list(self.selected_cards)},
                actor=me,
            )
            if not ok:
                return rx.toast("Reessayez.")
            if winner_id:
                await self._settle(
                    asession,
                    self.active_id,
                    int(room[16]),
                    winner_id,
                    int(room[6] or 0),
                    "RAMI",
                )
            await asession.commit()
        self.selected_cards = []
        await self._refresh()
        return rx.toast("Combinaison validee.")

    @rx.event
    async def tri_play(self, index: int):
        auth = await self.get_state(AuthState)
        me = auth.account_id
        async with rx.asession() as asession:
            room = await self._ctx(asession, self.active_id, lock=True)
            if room is None or int(room[4] or 0) != me:
                return rx.toast("Ce n'est pas votre tour.")
            state = json.loads(str(room[0]) or "{}")
            version = int(room[3] or 0)
            try:
                state = engine.tri_play(state, me, index)
            except engine.MoveError as exc:
                logging.exception("Unexpected error")
                return rx.toast(str(exc))
            order = await self._order(asession, self.active_id)
            winner_id = me if len(state["hands"].get(str(me), [])) == 0 else 0
            ok = await self._write(
                asession,
                self.active_id,
                version,
                state,
                turn=await self._next_turn(order, me),
                deadline_seconds=30,
                kind="discard",
                payload={"index": index},
                actor=me,
            )
            if not ok:
                return rx.toast("Reessayez.")
            if winner_id:
                await self._settle(
                    asession,
                    self.active_id,
                    int(room[16]),
                    winner_id,
                    int(room[6] or 0),
                    "TRI",
                )
            await asession.commit()
        self.selected_cards = []
        await self._refresh()
        return None

    @rx.event
    async def tri_play_selected(self):
        if not self.selected_cards:
            return rx.toast("Selectionnez une carte.")
        return RoomState.tri_play(self.selected_cards[0])

    @rx.event
    async def tri_pass(self):
        auth = await self.get_state(AuthState)
        me = auth.account_id
        async with rx.asession() as asession:
            room = await self._ctx(asession, self.active_id, lock=True)
            if room is None or int(room[4] or 0) != me:
                return rx.toast("Ce n'est pas votre tour.")
            state = json.loads(str(room[0]) or "{}")
            version = int(room[3] or 0)
            state = dict(state)
            state["drawn"] = False
            state["last"] = "tour passe"
            order = await self._order(asession, self.active_id)
            ok = await self._write(
                asession,
                self.active_id,
                version,
                state,
                turn=await self._next_turn(order, me),
                deadline_seconds=30,
                kind="pass_turn",
                payload={},
                actor=me,
            )
            if not ok:
                return rx.toast("Reessayez.")
            await asession.commit()
        await self._refresh()
        return None

    # --------------------------------------------------------------- BILLARD
    @rx.event
    def set_angle(self, value: str):
        try:
            self.aim_angle = max(-180, min(180, int(float(value))))
        except ValueError:
            self.aim_angle = 0

    @rx.event
    def set_power(self, value: str):
        try:
            self.aim_power = max(5, min(100, int(float(value))))
        except ValueError:
            self.aim_power = 55

    @rx.event
    async def billard_shoot(self):
        auth = await self.get_state(AuthState)
        me = auth.account_id
        async with rx.asession() as asession:
            room = await self._ctx(asession, self.active_id, lock=True)
            if room is None or int(room[4] or 0) != me:
                return rx.toast("Ce n'est pas votre tour.")
            state = json.loads(str(room[0]) or "{}")
            version = int(room[3] or 0)
            try:
                state, potted, cue_potted = engine.billard_shoot(
                    state, me, float(self.aim_angle), float(self.aim_power)
                )
            except engine.MoveError as exc:
                logging.exception("Unexpected error")
                return rx.toast(str(exc))
            order = await self._order(asession, self.active_id)
            groups = dict(state.get("groups", {}))
            opponent = await self._next_turn(order, me)
            legal_pot = [b for b in potted if b != 8]
            if legal_pot and not groups:
                mine = engine.billard_group_of(legal_pot[0])
                groups[str(me)] = mine
                groups[str(opponent)] = (
                    "stripes" if mine == "solids" else "solids"
                )
            state["groups"] = groups
            winner_id = 0
            if 8 in potted:
                my_group = groups.get(str(me), "")
                remaining = [
                    int(b["id"])
                    for b in state["balls"]
                    if not b["potted"]
                    and engine.billard_group_of(int(b["id"])) == my_group
                ]
                winner_id = me if my_group and not remaining else opponent
            keep_turn = bool(legal_pot) and not cue_potted and not winner_id
            ok = await self._write(
                asession,
                self.active_id,
                version,
                state,
                turn=me if keep_turn else opponent,
                deadline_seconds=45,
                kind="foul"
                if cue_potted
                else ("pot_ball" if potted else "shoot"),
                payload={
                    "angle": self.aim_angle,
                    "power": self.aim_power,
                    "potted": potted,
                },
                actor=me,
            )
            if not ok:
                return rx.toast("Reessayez.")
            await self._event(
                asession,
                self.active_id,
                "shoot",
                f"Tir {self.aim_angle}° / {self.aim_power}% - {state['last']}",
                me,
            )
            if winner_id:
                await self._settle(
                    asession,
                    self.active_id,
                    int(room[16]),
                    winner_id,
                    int(room[6] or 0),
                    "BILLARD",
                )
            await asession.commit()
        await self._refresh()
        return None

    # ----------------------------------------------------- turn timer expiry
    @rx.event
    async def advance_timeout(self):
        """Any player may push an expired turn forward (no worker needed)."""
        auth = await self.get_state(AuthState)
        me = auth.account_id
        async with rx.asession() as asession:
            room = await self._ctx(asession, self.active_id, lock=True)
            if room is None:
                return rx.toast("Salle introuvable.")
            deadline = room[17]
            if deadline is None:
                return rx.toast("Aucun minuteur actif.")
            left = (
                await asession.execute(
                    text(
                        "SELECT CAST(EXTRACT(EPOCH FROM (:d - NOW())) "
                        "AS INTEGER)"
                    ),
                    {"d": deadline},
                )
            ).first()
            if int(left[0] or 0) > 0:
                return rx.toast("Le minuteur tourne encore.")
            slug = str(room[7])
            if slug == "loto":
                await asession.commit()
                return RoomState.draw_number
            if slug == "domino":
                state = json.loads(str(room[0]) or "{}")
                rules = json.loads(str(room[1]) or "{}")
                humans = await self._order(asession, self.active_id)
                order = self._domino_order(rules, humans)
                current = int(room[4] or 0)
                version = int(room[3] or 0)
                if current < 0:
                    await asession.commit()
                    await self._run_bots()
                    await self._refresh()
                    return None
                state = dict(state)
                state["passes"] = int(state.get("passes", 0)) + 1
                state["extra_turn"] = False
                state["last"] = "temps ecoule"
                ok, _, _ = await self._domino_progress(
                    asession,
                    room,
                    state,
                    current,
                    order,
                    rules,
                    version,
                    "timeout",
                    {"skipped": current},
                )
                if not ok:
                    return rx.toast("Reessayez.")
                await self._event(
                    asession, self.active_id, "timeout", "Temps ecoule", None
                )
                await asession.commit()
                await self._run_bots()
                await self._refresh()
                return None
            state = json.loads(str(room[0]) or "{}")
            version = int(room[3] or 0)
            order = await self._order(asession, self.active_id)
            current = int(room[4] or 0)
            state = dict(state)
            state["dice"] = 0
            state["rolled"] = False
            state["drawn"] = False
            state["last"] = "temps ecoule"
            ok = await self._write(
                asession,
                self.active_id,
                version,
                state,
                turn=await self._next_turn(order, current),
                deadline_seconds=int(
                    json.loads(str(room[1]) or "{}").get("turn_seconds", 30)
                ),
                kind="timeout",
                payload={"skipped": current},
                actor=None,
            )
            if not ok:
                return rx.toast("Reessayez.")
            await self._event(
                asession, self.active_id, "timeout", "Temps ecoule", None
            )
            await asession.commit()
        await self._refresh()
        return None
