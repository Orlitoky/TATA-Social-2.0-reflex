"""Wallet + immutable transaction history (virtual points only)."""

from __future__ import annotations

from typing import TypedDict

import reflex as rx
from sqlalchemy import text

from app.states.auth_state import AuthState

PAGE_SIZE = 12


class LedgerRow(TypedDict):
    id: int
    amount: int
    balance_after: int
    reason: str
    reason_label: str
    description: str
    game_label: str
    time_label: str
    positive: bool


class WalletState(rx.State):
    loading: bool = True
    error: str = ""
    balance: int = 0
    lifetime_earned: int = 0
    lifetime_spent: int = 0
    entries: list[LedgerRow] = []
    total_entries: int = 0
    page: int = 0
    filter_kind: str = "all"
    info_open: bool = False

    @rx.var
    def total_pages(self) -> int:
        return max(1, (self.total_entries + PAGE_SIZE - 1) // PAGE_SIZE)

    @rx.var
    def page_label(self) -> str:
        return f"Page {self.page + 1} / {self.total_pages}"

    @rx.var
    def has_prev(self) -> bool:
        return self.page > 0

    @rx.var
    def has_next(self) -> bool:
        return self.page + 1 < self.total_pages

    @rx.event
    def toggle_info(self):
        self.info_open = not self.info_open

    @rx.event
    async def set_filter(self, kind: str):
        self.filter_kind = kind
        self.page = 0
        return WalletState.load_wallet

    @rx.event
    async def next_page(self):
        if self.has_next:
            self.page += 1
            return WalletState.load_wallet

    @rx.event
    async def prev_page(self):
        if self.has_prev:
            self.page -= 1
            return WalletState.load_wallet

    @rx.event
    async def load_wallet(self):
        auth = await self.get_state(AuthState)
        if not auth.account_id:
            return
        self.loading = True
        self.error = ""
        where = "WHERE e.account_id = :me"
        params: dict[str, int | str] = {"me": auth.account_id}
        if self.filter_kind == "gain":
            where += " AND e.amount_coins > 0"
        elif self.filter_kind == "loss":
            where += " AND e.amount_coins < 0"
        elif self.filter_kind == "games":
            where += " AND e.reason IN ('game_entry', 'game_win')"
        async with rx.asession() as asession:
            wallet = (
                await asession.execute(
                    text(
                        """
                        SELECT COALESCE(balance_coins, 0),
                               COALESCE(lifetime_earned_coins, 0),
                               COALESCE(lifetime_spent_coins, 0)
                        FROM wallet WHERE account_id = :me
                        """
                    ),
                    {"me": auth.account_id},
                )
            ).first()
            self.balance = int(wallet[0]) if wallet else 0
            self.lifetime_earned = int(wallet[1]) if wallet else 0
            self.lifetime_spent = int(wallet[2]) if wallet else 0
            total = (
                await asession.execute(
                    text(f"SELECT COUNT(*) FROM coin_ledger_entry e {where}"),
                    params,
                )
            ).first()
            self.total_entries = int(total[0] or 0)
            rows = (
                await asession.execute(
                    text(
                        f"""
                        SELECT e.id, e.amount_coins, e.balance_after, e.reason,
                               e.description,
                               COALESCE(g.name, ''),
                               TO_CHAR(e.created_at, 'DD/MM/YYYY HH24:MI')
                        FROM coin_ledger_entry e
                        LEFT JOIN game_room r ON r.id = e.related_room_id
                        LEFT JOIN game g ON g.id = r.game_id
                        {where}
                        ORDER BY e.id DESC
                        LIMIT :limit OFFSET :offset
                        """
                    ),
                    {
                        **params,
                        "limit": PAGE_SIZE,
                        "offset": self.page * PAGE_SIZE,
                    },
                )
            ).all()
        labels = {
            "signup_bonus": "Bonus d'inscription",
            "daily_reward": "Recompense du jour",
            "game_win": "Gain de partie",
            "game_entry": "Entree de partie",
            "gift_sent": "Cadeau envoye",
            "gift_received": "Cadeau recu",
            "achievement": "Trophee",
            "admin_adjustment": "Ajustement",
        }
        self.entries = [
            {
                "id": int(r[0]),
                "amount": int(r[1]),
                "balance_after": int(r[2]),
                "reason": str(r[3]),
                "reason_label": labels.get(str(r[3]), str(r[3])),
                "description": str(r[4]),
                "game_label": str(r[5]),
                "time_label": str(r[6]),
                "positive": int(r[1]) > 0,
            }
            for r in rows
        ]
        auth.coin_balance = self.balance
        self.loading = False
