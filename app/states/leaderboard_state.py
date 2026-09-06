"""Player statistics & leaderboard computed live from finished game rooms.

Truth is derived only from game_room rows with status='finished' joined to
game_room_member (real account-backed memberships only: server bots have no
membership rows) and game. The cached player_game_stat table is deliberately
never read. Nothing is seeded, inserted or updated here.
"""

from __future__ import annotations

import logging
from typing import TypedDict

import reflex as rx
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError

from app.media import avatar_source
from app.states.auth_state import AuthState


class LeaderRow(TypedDict):
    rank: int
    account_id: int
    display_name: str
    username: str
    avatar_url: str
    avatar_remote: bool
    games: int
    wins: int
    losses: int
    win_rate: float
    win_rate_display: str
    favorite_game: str
    is_me: bool


class GameOption(TypedDict):
    slug: str
    name: str


RANGE_DAYS: dict[str, int] = {"all": 0, "30d": 30, "7d": 7}
RANGE_LABELS: dict[str, str] = {
    "all": "Depuis toujours",
    "30d": "30 derniers jours",
    "7d": "7 derniers jours",
}


def _base_cte(slug: str, days: int) -> str:
    """Return the shared CTE block; values are always bound parameters."""
    clauses = ""
    if slug != "all":
        clauses += " AND g.slug = :slug"
    if days > 0:
        clauses += (
            " AND COALESCE(r.finished_at, r.updated_at) >= "
            "NOW() - CAST(:days || ' days' AS INTERVAL)"
        )
    return f"""
        WITH parts AS (
            SELECT m.account_id AS aid,
                   r.id AS rid,
                   g.name AS gname,
                   CASE WHEN r.winner_account_id = m.account_id
                        THEN 1 ELSE 0 END AS is_win,
                   CASE WHEN r.winner_account_id IS NOT NULL
                             AND r.winner_account_id <> m.account_id
                             AND EXISTS (SELECT 1 FROM account w
                                         WHERE w.id = r.winner_account_id
                                           AND w.status <> 'deleted')
                        THEN 1 ELSE 0 END AS is_loss
            FROM game_room_member m
            JOIN game_room r ON r.id = m.room_id
            JOIN game g ON g.id = r.game_id
            JOIN account a ON a.id = m.account_id
                          AND a.status <> 'deleted'
            WHERE r.status = 'finished'{clauses}
        ),
        totals AS (
            SELECT aid,
                   COUNT(DISTINCT rid) AS games,
                   COALESCE(SUM(is_win), 0) AS wins,
                   COALESCE(SUM(is_loss), 0) AS losses
            FROM parts
            GROUP BY aid
        ),
        fav AS (
            SELECT aid, gname,
                   ROW_NUMBER() OVER (
                       PARTITION BY aid
                       ORDER BY COUNT(DISTINCT rid) DESC,
                                COALESCE(SUM(is_win), 0) DESC,
                                gname ASC
                   ) AS rn
            FROM parts
            GROUP BY aid, gname
        ),
        ranked AS (
            SELECT t.aid, t.games, t.wins, t.losses,
                   CASE WHEN t.games > 0
                        THEN CAST(t.wins AS DOUBLE PRECISION)
                             / CAST(t.games AS DOUBLE PRECISION)
                        ELSE 0 END AS wr,
                   COALESCE(p.display_name, a.username) AS dname,
                   a.username AS uname,
                   COALESCE(p.avatar_key, '') AS akey,
                   COALESCE(f.gname, '') AS fav_name,
                   ROW_NUMBER() OVER (
                       ORDER BY t.wins DESC,
                                CASE WHEN t.games > 0
                                     THEN CAST(t.wins AS DOUBLE PRECISION)
                                          / CAST(t.games AS DOUBLE PRECISION)
                                     ELSE 0 END DESC,
                                t.games DESC,
                                COALESCE(p.display_name, a.username) ASC,
                                t.aid ASC
                   ) AS position
            FROM totals t
            JOIN account a ON a.id = t.aid
            LEFT JOIN profile p ON p.account_id = a.id
            LEFT JOIN fav f ON f.aid = t.aid AND f.rn = 1
        )
    """


class LeaderboardState(rx.State):
    loading: bool = True
    error: str = ""

    game_options: list[GameOption] = [{"slug": "all", "name": "Tous les jeux"}]
    active_game: str = "all"
    active_range: str = "all"

    rows: list[LeaderRow] = []
    total_finished_rooms: int = 0

    my_games: int = 0
    my_wins: int = 0
    my_losses: int = 0
    my_win_rate: float = 0.0
    my_rank: int = 0
    my_favorite_game: str = ""

    @rx.var
    def range_label(self) -> str:
        return RANGE_LABELS.get(self.active_range, RANGE_LABELS["all"])

    @rx.var
    def game_label(self) -> str:
        for option in self.game_options:
            if option["slug"] == self.active_game:
                return str(option["name"])
        return "Tous les jeux"

    @rx.var
    def my_win_rate_display(self) -> str:
        return f"{self.my_win_rate * 100:.1f}%"

    @rx.var
    def has_personal_history(self) -> bool:
        return self.my_games > 0

    @rx.var
    def has_rows(self) -> bool:
        return len(self.rows) > 0

    @rx.var
    def podium(self) -> list[LeaderRow]:
        return self.rows[:3]

    @rx.var
    def rank_context(self) -> str:
        if self.my_rank > 0 and self.my_rank <= len(self.rows):
            return f"#{self.my_rank} sur {len(self.rows)} joueurs classes"
        if self.my_rank > 0:
            return f"#{self.my_rank} (hors du top 50 affiche)"
        return "Pas encore classe"

    # ------------------------------------------------------------- filters
    @rx.event
    async def set_game_filter(self, slug: str):
        allowed = {str(o["slug"]) for o in self.game_options}
        if slug not in allowed:
            return
        self.active_game = slug
        return LeaderboardState.load_leaderboard

    @rx.event
    async def set_range_filter(self, key: str):
        if key not in RANGE_DAYS:
            return
        self.active_range = key
        return LeaderboardState.load_leaderboard

    # ---------------------------------------------------------------- load
    @rx.event
    async def load_leaderboard(self):
        auth = await self.get_state(AuthState)
        me = auth.account_id
        if not me:
            return
        self.loading = True
        self.error = ""
        try:
            async with rx.asession() as asession:
                options = (
                    await asession.execute(
                        text(
                            "SELECT slug, name FROM game WHERE is_active = "
                            "true ORDER BY name"
                        )
                    )
                ).all()
                self.game_options = [
                    {"slug": "all", "name": "Tous les jeux"}
                ] + [{"slug": str(o[0]), "name": str(o[1])} for o in options]
                if self.active_game not in {
                    str(o["slug"]) for o in self.game_options
                }:
                    self.active_game = "all"
                if self.active_range not in RANGE_DAYS:
                    self.active_range = "all"

                slug = self.active_game
                days = RANGE_DAYS[self.active_range]
                params: dict[str, str | int] = {}
                if slug != "all":
                    params["slug"] = slug
                if days > 0:
                    params["days"] = str(days)

                cte = _base_cte(slug, days)
                rows = (
                    await asession.execute(
                        text(
                            cte
                            + """
                            SELECT position, aid, dname, uname, akey,
                                   games, wins, losses, wr, fav_name
                            FROM ranked
                            ORDER BY position
                            LIMIT 50
                            """
                        ),
                        params,
                    )
                ).all()
                mine = (
                    await asession.execute(
                        text(
                            cte
                            + """
                            SELECT position, games, wins, losses, wr, fav_name
                            FROM ranked WHERE aid = :me
                            """
                        ),
                        {**params, "me": me},
                    )
                ).first()
                counted = (
                    await asession.execute(
                        text(cte + "SELECT COUNT(DISTINCT rid) FROM parts"),
                        params,
                    )
                ).first()
        except SQLAlchemyError as exc:
            logging.exception(f"Error: {exc}")
            self.loading = False
            self.error = (
                "Impossible de charger le classement. Reessayez plus tard."
            )
            return

        built: list[LeaderRow] = []
        for r in rows:
            url, remote = avatar_source(str(r[4] or ""), str(r[3]))
            rate = float(r[8] or 0.0)
            built.append(
                {
                    "rank": int(r[0]),
                    "account_id": int(r[1]),
                    "display_name": str(r[2]),
                    "username": str(r[3]),
                    "avatar_url": url,
                    "avatar_remote": remote,
                    "games": int(r[5] or 0),
                    "wins": int(r[6] or 0),
                    "losses": int(r[7] or 0),
                    "win_rate": rate,
                    "win_rate_display": f"{rate * 100:.1f}%",
                    "favorite_game": str(r[9] or "") or "—",
                    "is_me": int(r[1]) == me,
                }
            )
        self.rows = built
        self.total_finished_rooms = int(counted[0] or 0) if counted else 0
        if mine is not None:
            self.my_rank = int(mine[0] or 0)
            self.my_games = int(mine[1] or 0)
            self.my_wins = int(mine[2] or 0)
            self.my_losses = int(mine[3] or 0)
            self.my_win_rate = float(mine[4] or 0.0)
            self.my_favorite_game = str(mine[5] or "") or "—"
        else:
            self.my_rank = 0
            self.my_games = 0
            self.my_wins = 0
            self.my_losses = 0
            self.my_win_rate = 0.0
            self.my_favorite_game = "—"
        self.loading = False
