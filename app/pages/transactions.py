"""Transactions: unique balance, lifetime totals, immutable paginated history."""

from __future__ import annotations

import reflex as rx

from app.components.game_shell import NO_PURCHASE_COPY, dark_page, jewel_tag
from app.states.wallet_state import LedgerRow, WalletState


def stat_tile(
    label: str, value: rx.Var | int, icon: str, tone: str
) -> rx.Component:
    return rx.el.div(
        rx.el.div(
            rx.icon(icon, class_name=f"h-4 w-4 {tone}"),
            rx.el.span(
                label,
                class_name=(
                    "text-[10px] font-bold uppercase tracking-wider "
                    "text-zinc-500"
                ),
            ),
            class_name="flex items-center gap-2",
        ),
        rx.el.p(
            value,
            class_name="mt-1 text-2xl font-black tabular-nums text-white",
        ),
        rx.el.span(
            "points internes",
            class_name="text-[10px] font-medium text-zinc-600",
        ),
        class_name=(
            "w-full rounded-2xl border border-zinc-800 bg-[#0C0D10] p-4"
        ),
    )


def filter_button(label: str, kind: str) -> rx.Component:
    return rx.el.button(
        label,
        on_click=lambda: WalletState.set_filter(kind),
        class_name=rx.cond(
            WalletState.filter_kind == kind,
            "rounded-xl bg-emerald-500 px-3 py-1.5 text-xs font-bold text-black",
            "rounded-xl border border-zinc-800 px-3 py-1.5 text-xs font-bold text-zinc-400 hover:border-zinc-600",
        ),
    )


def entry_row(entry: LedgerRow) -> rx.Component:
    return rx.el.div(
        rx.el.div(
            rx.cond(
                entry["positive"],
                rx.icon(
                    "arrow-up-right", class_name="h-4 w-4 text-emerald-400"
                ),
                rx.icon("arrow-down-right", class_name="h-4 w-4 text-rose-400"),
            ),
            class_name=rx.cond(
                entry["positive"],
                "flex size-9 shrink-0 items-center justify-center rounded-full bg-emerald-500/10",
                "flex size-9 shrink-0 items-center justify-center rounded-full bg-rose-500/10",
            ),
        ),
        rx.el.div(
            rx.el.p(
                entry["reason_label"],
                class_name="text-xs font-bold text-white",
            ),
            rx.el.p(
                entry["description"],
                class_name="truncate text-[11px] text-zinc-500",
            ),
            rx.el.div(
                rx.cond(
                    entry["game_label"] != "",
                    jewel_tag(entry["game_label"], "violet"),
                    rx.fragment(),
                ),
                rx.el.span(
                    entry["time_label"],
                    class_name="text-[10px] font-medium text-zinc-600",
                ),
                class_name="mt-1 flex flex-wrap items-center gap-2",
            ),
            class_name="min-w-0 flex-1",
        ),
        rx.el.div(
            rx.el.p(
                entry["amount"],
                class_name=rx.cond(
                    entry["positive"],
                    "text-sm font-black tabular-nums text-emerald-400",
                    "text-sm font-black tabular-nums text-rose-400",
                ),
            ),
            rx.el.p(
                f"solde {entry['balance_after']}",
                class_name="text-[10px] text-zinc-600",
            ),
            class_name="shrink-0 text-right",
        ),
        class_name=(
            "flex items-center gap-3 border-b border-zinc-800/60 py-3 "
            "last:border-0"
        ),
    )


def transactions_body() -> rx.Component:
    return rx.el.div(
        rx.el.div(
            stat_tile("Solde", WalletState.balance, "coins", "text-amber-300"),
            stat_tile(
                "Gagnes",
                WalletState.lifetime_earned,
                "trending-up",
                "text-emerald-400",
            ),
            stat_tile(
                "Depenses",
                WalletState.lifetime_spent,
                "trending-down",
                "text-rose-400",
            ),
            stat_tile(
                "Ecritures",
                WalletState.total_entries,
                "list",
                "text-cyan-300",
            ),
            class_name="grid w-full grid-cols-2 gap-4 md:grid-cols-4",
        ),
        rx.el.div(
            rx.icon(
                "shield-alert", class_name="h-5 w-5 shrink-0 text-amber-300"
            ),
            rx.el.div(
                rx.el.p(
                    NO_PURCHASE_COPY,
                    class_name="text-xs font-semibold text-amber-100",
                ),
                rx.el.p(
                    "Aucun depot, aucun retrait, aucune conversion en argent "
                    "reel, aucune valeur monetaire. Les points servent "
                    "uniquement a jouer.",
                    class_name="mt-1 text-[11px] text-amber-200/70",
                ),
            ),
            class_name=(
                "flex items-start gap-3 rounded-2xl border "
                "border-amber-400/30 bg-amber-400/5 p-4"
            ),
        ),
        rx.el.div(
            rx.el.div(
                filter_button("Tout", "all"),
                filter_button("Gains", "gain"),
                filter_button("Depenses", "loss"),
                filter_button("Parties", "games"),
                class_name="flex flex-wrap gap-2",
            ),
            rx.el.div(
                rx.el.button(
                    rx.icon("chevron-left", class_name="h-4 w-4"),
                    on_click=WalletState.prev_page,
                    disabled=~WalletState.has_prev,
                    aria_label="Page precedente",
                    class_name=(
                        "flex size-8 items-center justify-center rounded-lg "
                        "border border-zinc-800 text-zinc-300 "
                        "disabled:opacity-30"
                    ),
                ),
                rx.el.span(
                    WalletState.page_label,
                    class_name="text-xs font-semibold text-zinc-400",
                ),
                rx.el.button(
                    rx.icon("chevron-right", class_name="h-4 w-4"),
                    on_click=WalletState.next_page,
                    disabled=~WalletState.has_next,
                    aria_label="Page suivante",
                    class_name=(
                        "flex size-8 items-center justify-center rounded-lg "
                        "border border-zinc-800 text-zinc-300 "
                        "disabled:opacity-30"
                    ),
                ),
                class_name="flex items-center gap-2",
            ),
            class_name=(
                "flex flex-col gap-3 sm:flex-row sm:items-center "
                "sm:justify-between"
            ),
        ),
        rx.el.div(
            rx.cond(
                WalletState.loading,
                rx.el.div(
                    rx.el.div(
                        class_name="h-14 animate-pulse rounded-xl bg-zinc-900"
                    ),
                    rx.el.div(
                        class_name=(
                            "mt-2 h-14 animate-pulse rounded-xl bg-zinc-900"
                        )
                    ),
                    rx.el.div(
                        class_name=(
                            "mt-2 h-14 animate-pulse rounded-xl bg-zinc-900"
                        )
                    ),
                ),
                rx.cond(
                    WalletState.entries.length() > 0,
                    rx.el.div(
                        rx.foreach(WalletState.entries, entry_row),
                        class_name="flex flex-col",
                    ),
                    rx.el.div(
                        rx.icon("receipt", class_name="h-8 w-8 text-zinc-700"),
                        rx.el.p(
                            "Aucune ecriture pour ce filtre.",
                            class_name="mt-2 text-sm text-zinc-500",
                        ),
                        class_name=(
                            "flex flex-col items-center justify-center py-12"
                        ),
                    ),
                ),
            ),
            class_name=(
                "rounded-2xl border border-zinc-800 bg-[#0C0D10] px-4 py-2"
            ),
        ),
        rx.cond(
            WalletState.error != "",
            rx.el.p(
                WalletState.error,
                class_name="text-sm font-semibold text-rose-400",
            ),
            rx.fragment(),
        ),
        class_name="flex w-full flex-col gap-4",
    )


def transactions_page() -> rx.Component:
    return dark_page(
        "Transactions", transactions_body(), "transactions", "/games"
    )
