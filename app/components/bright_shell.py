"""Bright sky/navy discovery shell used only by the /games home page.

Gameplay routes keep the dark hall shell in app/components/game_shell.py.
All coin values shown here are internal TATA points: no purchase, no deposit,
no withdrawal and no monetary value.
"""

from __future__ import annotations

import reflex as rx

from app.components.game_shell import NO_PURCHASE_COPY, referral_panel
from app.states.auth_state import AuthState
from app.states.games_state import GamesState


def brand_mark() -> rx.Component:
    return rx.el.a(
        rx.el.div(
            rx.icon("dices", class_name="h-5 w-5 text-white"),
            class_name=(
                "flex size-9 items-center justify-center rounded-lg "
                "bg-[#1E9EF5]"
            ),
        ),
        rx.el.div(
            rx.el.p(
                "TATA",
                class_name=(
                    "text-sm font-bold leading-none tracking-[0.22em] "
                    "text-[#071A33]"
                ),
            ),
            rx.el.p(
                "GAMES",
                class_name=(
                    "mt-0.5 text-[10px] font-semibold leading-none "
                    "tracking-[0.32em] text-[#1E9EF5]"
                ),
            ),
            class_name="min-w-0",
        ),
        href="/games",
        aria_label="TATA Games",
        class_name="flex items-center gap-2",
    )


def bright_coin_chip() -> rx.Component:
    return rx.el.button(
        rx.icon("coins", class_name="h-4 w-4 text-[#1E9EF5]"),
        rx.el.span(
            f"{AuthState.coin_balance}",
            class_name="text-sm font-bold tabular-nums text-[#071A33]",
        ),
        rx.el.span(
            "pts",
            class_name="text-[10px] font-semibold uppercase text-slate-500",
        ),
        on_click=rx.toast(NO_PURCHASE_COPY, duration=7000),
        title=NO_PURCHASE_COPY,
        aria_label="Points internes TATA",
        class_name=(
            "flex items-center gap-1.5 rounded-lg border border-slate-200 "
            "bg-[#F5FAFF] px-2.5 py-1.5 active:bg-[#E4F2FE] "
            "hover:border-[#1E9EF5]/50"
        ),
    )


def _icon_link(icon: str, href: str, label: str) -> rx.Component:
    return rx.el.a(
        rx.icon(icon, class_name="h-4 w-4 text-[#071A33]"),
        href=href,
        title=label,
        aria_label=label,
        class_name=(
            "flex size-9 items-center justify-center rounded-lg border "
            "border-slate-200 bg-white active:bg-slate-100 "
            "hover:border-[#1E9EF5]/50"
        ),
    )


def bright_header() -> rx.Component:
    return rx.el.header(
        rx.el.div(
            rx.el.a(
                rx.icon("chevron-left", class_name="h-5 w-5 text-[#071A33]"),
                href="/",
                title="Retour au reseau social",
                aria_label="Retour au reseau social",
                class_name=(
                    "flex size-9 shrink-0 items-center justify-center "
                    "rounded-lg border border-slate-200 bg-white "
                    "active:bg-slate-100 hover:border-[#1E9EF5]/50"
                ),
            ),
            brand_mark(),
            rx.el.div(
                bright_coin_chip(),
                _icon_link("bell", "/messages", "Notifications"),
                _icon_link("user", "/profile", "Profil"),
                class_name="ml-auto flex items-center gap-2",
            ),
            class_name=(
                "mx-auto flex h-14 w-full max-w-5xl items-center gap-2 px-3 "
                "sm:gap-3 sm:px-4"
            ),
        ),
        class_name=(
            "sticky top-0 z-30 w-full border-b border-slate-200 bg-white/95 "
            "backdrop-blur"
        ),
    )


def _bright_nav_link(
    icon: str, label: str, href: str, active: bool = False
) -> rx.Component:
    return rx.el.a(
        rx.icon(
            icon,
            class_name=rx.cond(
                active,
                "h-5 w-5 text-[#22D3EE]",
                "h-5 w-5 text-slate-400",
            ),
        ),
        rx.el.span(
            label,
            class_name=rx.cond(
                active,
                "text-[10px] font-semibold text-[#22D3EE]",
                "text-[10px] font-semibold text-slate-400",
            ),
        ),
        href=href,
        class_name=(
            "flex flex-1 flex-col items-center gap-0.5 py-2 active:bg-white/5"
        ),
    )


def bright_bottom_nav(active: str = "jeux") -> rx.Component:
    return rx.el.nav(
        _bright_nav_link("gamepad-2", "Jeux", "/games", active == "jeux"),
        _bright_nav_link(
            "trophy", "Classement", "/leaderboard", active == "classement"
        ),
        _bright_nav_link(
            "receipt-text",
            "Points",
            "/transactions",
            active == "transactions",
        ),
        _bright_nav_link(
            "message-circle", "Chat", "/messages", active == "chat"
        ),
        rx.el.button(
            rx.icon("gift", class_name="h-5 w-5 text-slate-400"),
            rx.el.span(
                "Parrainage",
                class_name="text-[10px] font-semibold text-slate-400",
            ),
            on_click=GamesState.toggle_referral,
            class_name=(
                "flex flex-1 flex-col items-center gap-0.5 py-2 "
                "active:bg-white/5"
            ),
        ),
        class_name=(
            "fixed bottom-0 left-0 right-0 z-30 flex border-t "
            "border-[#0B2647] bg-[#071A33]"
        ),
    )


def bright_page(body: rx.Component, active: str = "jeux") -> rx.Component:
    return rx.el.main(
        bright_header(),
        rx.el.div(
            body,
            class_name="mx-auto w-full max-w-5xl px-3 pb-24 pt-3 sm:px-4",
        ),
        referral_panel(),
        bright_bottom_nav(active),
        class_name=(
            "min-h-dvh w-full bg-[#F7FBFF] font-['Inter'] text-[#071A33]"
        ),
    )
