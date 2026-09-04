"""Dark game-hall shell: header, coin chip, medallions, tags, bottom nav.

Only used on game/wallet/settings routes so the light social identity of
Home, Friends, Messages and Profile stays untouched.
"""

from __future__ import annotations

import reflex as rx

from app.states.auth_state import AuthState
from app.states.games_state import GamesState

NO_PURCHASE_COPY = (
    "Les points TATA sont virtuels et internes: aucun achat, aucun depot, "
    "aucun retrait, aucune valeur monetaire et aucune conversion possible."
)


def medallion(icon: str, size: str = "size-14") -> rx.Component:
    """Warm gold round illustrated medallion drawn purely with CSS."""
    return rx.el.div(
        rx.el.div(
            rx.icon(icon, class_name="h-6 w-6 text-[#3B2606]"),
            class_name=(
                "flex h-full w-full items-center justify-center rounded-full "
                "bg-[radial-gradient(circle_at_30%_25%,#FFE9A8_0%,#F2C14E_45%,"
                "#B98518_100%)] ring-1 ring-[#7A5714]"
            ),
        ),
        class_name=(
            f"{size} shrink-0 rounded-full p-[3px] "
            "bg-[linear-gradient(140deg,#FFF3CB,#C9962C_60%,#6F4F12)] "
            "shadow-[0_0_0_1px_rgba(0,0,0,0.6)]"
        ),
    )


def jewel_tag(label: str | rx.Var, tone: str = "cyan") -> rx.Component:
    tones = {
        "cyan": "bg-cyan-500/15 text-cyan-300 ring-cyan-400/30",
        "gold": "bg-amber-500/15 text-amber-300 ring-amber-400/30",
        "emerald": "bg-emerald-500/15 text-emerald-300 ring-emerald-400/30",
        "ruby": "bg-rose-500/15 text-rose-300 ring-rose-400/30",
        "violet": "bg-indigo-500/15 text-indigo-300 ring-indigo-400/30",
        "blue": "bg-blue-500/15 text-blue-300 ring-blue-400/30",
    }
    return rx.el.span(
        label,
        class_name=(
            "w-fit rounded-full px-2.5 py-1 text-[11px] font-semibold "
            "uppercase tracking-wide ring-1 " + tones.get(tone, tones["cyan"])
        ),
    )


def coin_chip() -> rx.Component:
    return rx.el.div(
        rx.icon("coins", class_name="h-4 w-4 text-amber-300"),
        rx.el.span(
            f"{AuthState.coin_balance}",
            class_name="text-sm font-bold text-amber-200 tabular-nums",
        ),
        rx.el.span(
            "pts",
            class_name="text-[10px] font-semibold uppercase text-amber-500/80",
        ),
        rx.el.button(
            rx.icon("plus", class_name="h-3.5 w-3.5"),
            on_click=rx.toast(NO_PURCHASE_COPY, duration=7000),
            title=NO_PURCHASE_COPY,
            aria_label="Information sur les points TATA",
            class_name=(
                "ml-1 flex size-6 items-center justify-center rounded-full "
                "border border-amber-400/40 text-amber-300 "
                "hover:bg-amber-400/10"
            ),
        ),
        class_name=(
            "flex items-center gap-1.5 rounded-full border border-amber-400/25 "
            "bg-[#141108] px-3 py-1.5"
        ),
    )


def game_header(title: str | rx.Var, back_href: str = "/games") -> rx.Component:
    return rx.el.header(
        rx.el.div(
            rx.el.a(
                rx.icon("chevron-left", class_name="h-5 w-5 text-zinc-300"),
                href=back_href,
                aria_label="Retour",
                class_name=(
                    "flex size-9 items-center justify-center rounded-xl "
                    "border border-zinc-800 bg-zinc-900 hover:border-zinc-600"
                ),
            ),
            rx.el.div(
                rx.el.p(
                    title,
                    class_name="text-base font-bold tracking-tight text-white",
                ),
                rx.el.p(
                    "Points internes uniquement",
                    class_name="text-[11px] font-medium text-zinc-500",
                ),
                class_name="min-w-0",
            ),
            rx.el.div(
                coin_chip(),
                rx.el.a(
                    rx.icon("house", class_name="h-4 w-4 text-zinc-300"),
                    href="/",
                    title="Retour au reseau social",
                    aria_label="Accueil social",
                    class_name=(
                        "hidden sm:flex size-9 items-center justify-center "
                        "rounded-xl border border-zinc-800 bg-zinc-900 "
                        "hover:border-zinc-600"
                    ),
                ),
                class_name="flex items-center gap-2",
            ),
            class_name=(
                "mx-auto flex h-16 w-full max-w-6xl items-center gap-3 px-4"
            ),
        ),
        class_name=(
            "sticky top-0 z-30 w-full border-b border-zinc-800/80 "
            "bg-[#08090B]/95 backdrop-blur"
        ),
    )


def _nav_item(
    icon: str, label: str, href: str, active: bool = False
) -> rx.Component:
    return rx.el.a(
        rx.icon(
            icon,
            class_name=(
                rx.cond(
                    active, "h-5 w-5 text-emerald-400", "h-5 w-5 text-zinc-500"
                )
            ),
        ),
        rx.el.span(
            label,
            class_name=(
                rx.cond(
                    active,
                    "text-[10px] font-semibold text-emerald-400",
                    "text-[10px] font-semibold text-zinc-500",
                )
            ),
        ),
        href=href,
        class_name="flex flex-1 flex-col items-center gap-0.5 py-2",
    )


def game_bottom_nav(active: str = "jeux") -> rx.Component:
    return rx.el.nav(
        _nav_item("gamepad-2", "Jeux", "/games", active == "jeux"),
        _nav_item(
            "receipt-text",
            "Transactions",
            "/transactions",
            active == "transactions",
        ),
        _nav_item("message-circle", "Chat", "/messages", active == "chat"),
        rx.el.button(
            rx.icon("gift", class_name="h-5 w-5 text-zinc-500"),
            rx.el.span(
                "Parrainage",
                class_name="text-[10px] font-semibold text-zinc-500",
            ),
            on_click=GamesState.toggle_referral,
            class_name="flex flex-1 flex-col items-center gap-0.5 py-2",
        ),
        _nav_item("user", "Profil", "/profile", active == "profil"),
        class_name=(
            "fixed bottom-0 left-0 right-0 z-30 flex border-t "
            "border-zinc-800 bg-[#08090B]"
        ),
    )


def referral_panel() -> rx.Component:
    return rx.cond(
        GamesState.referral_open,
        rx.el.div(
            rx.el.div(
                rx.el.div(
                    rx.el.h2(
                        "Parrainage",
                        class_name="text-base font-bold text-white",
                    ),
                    rx.el.button(
                        rx.icon("x", class_name="h-4 w-4"),
                        on_click=GamesState.toggle_referral,
                        aria_label="Fermer",
                        class_name="text-zinc-500 hover:text-white",
                    ),
                    class_name=(
                        "flex items-center justify-between border-b "
                        "border-zinc-800 px-4 py-3"
                    ),
                ),
                rx.el.div(
                    rx.el.p(
                        "Partagez votre code d'invitation. Vos filleuls et vous "
                        "recevez des points internes de bienvenue.",
                        class_name="text-sm text-zinc-400",
                    ),
                    rx.el.div(
                        rx.el.span(
                            GamesState.referral_code,
                            class_name=(
                                "font-mono text-lg font-bold "
                                "tracking-[0.2em] text-amber-300"
                            ),
                        ),
                        class_name=(
                            "mt-3 rounded-xl border border-dashed "
                            "border-amber-400/40 bg-[#141108] px-4 py-3 "
                            "text-center"
                        ),
                    ),
                    rx.el.ul(
                        rx.el.li(
                            "Recompenses versees uniquement en points TATA.",
                            class_name="text-xs text-zinc-500",
                        ),
                        rx.el.li(
                            "Aucun paiement, aucun retrait, aucune valeur "
                            "monetaire.",
                            class_name="text-xs text-zinc-500",
                        ),
                        rx.el.li(
                            "Panneau informatif: rien n'est vendu ici.",
                            class_name="text-xs text-zinc-500",
                        ),
                        class_name="mt-3 flex list-disc flex-col gap-1 pl-4",
                    ),
                    class_name="p-4",
                ),
                class_name=(
                    "w-full max-w-md overflow-hidden rounded-2xl border "
                    "border-zinc-800 bg-[#0C0D10]"
                ),
            ),
            class_name=(
                "fixed inset-0 z-50 flex items-center justify-center "
                "bg-black/70 p-4"
            ),
        ),
    )


def dark_page(
    title: str | rx.Var,
    body: rx.Component,
    active: str = "jeux",
    back_href: str = "/games",
) -> rx.Component:
    return rx.el.main(
        game_header(title, back_href),
        rx.el.div(
            body,
            class_name=("mx-auto w-full max-w-6xl px-4 pb-24 pt-4 md:pb-28"),
        ),
        referral_panel(),
        game_bottom_nav(active),
        class_name=(
            "min-h-dvh w-full bg-[#08090B] font-['Inter'] text-zinc-100 "
            "[background-image:radial-gradient(1000px_500px_at_50%_-10%,"
            "#16181D_0%,#08090B_70%)]"
        ),
    )
