"""Protected dark Games hub: eight medallion cards + my live rooms."""

from __future__ import annotations

import reflex as rx

from app.components.game_shell import (
    NO_PURCHASE_COPY,
    dark_page,
    jewel_tag,
    medallion,
)
from app.states.games_state import GameCard, GamesState, RoomRow


def game_card(card: GameCard) -> rx.Component:
    return rx.el.div(
        rx.el.div(
            medallion(card["medallion"]),
            rx.el.div(
                rx.el.p(
                    card["name"],
                    class_name="text-sm font-black tracking-wide text-white",
                ),
                rx.el.p(
                    card["description"],
                    class_name="mt-1 line-clamp-2 text-[11px] text-zinc-400",
                ),
                class_name="min-w-0 flex-1",
            ),
            class_name="flex items-start gap-3",
        ),
        rx.el.div(
            jewel_tag(card["tag"], "gold"),
            jewel_tag(f"{card['entry_coins']} pts", "cyan"),
            jewel_tag(
                f"{card['min_players']}-{card['max_players']} joueurs", "violet"
            ),
            class_name="mt-3 flex flex-wrap gap-1.5",
        ),
        rx.el.div(
            rx.el.div(
                rx.el.span(
                    class_name=(
                        "size-2 rounded-full bg-emerald-500 "
                        "shadow-[0_0_8px_#10B981]"
                    )
                ),
                rx.el.span(
                    f"{card['open_rooms']} salles • {card['live_players']} en ligne",
                    class_name="text-[11px] font-semibold text-emerald-400",
                ),
                class_name="flex items-center gap-1.5",
            ),
            rx.el.a(
                "JOUER",
                href=f"/games/{card['slug']}",
                class_name=(
                    "rounded-xl bg-emerald-500 px-4 py-2 text-xs font-black "
                    "tracking-wider text-black hover:bg-emerald-400"
                ),
            ),
            class_name="mt-4 flex items-center justify-between gap-2",
        ),
        class_name=(
            "flex w-full flex-col rounded-2xl border border-zinc-800 "
            "bg-[linear-gradient(160deg,#111317,#0A0B0E)] p-4 "
            "hover:border-amber-400/40"
        ),
    )


def my_room_row(room: RoomRow) -> rx.Component:
    return rx.el.a(
        rx.el.div(
            rx.el.p(
                room["game_name"],
                class_name="text-xs font-bold text-white",
            ),
            rx.el.p(
                f"{room['name']} • {room['status_label']}",
                class_name="text-[11px] text-zinc-500",
            ),
            class_name="min-w-0 flex-1",
        ),
        rx.el.span(
            f"{room['player_count']}/{room['max_players']}",
            class_name="text-[11px] font-bold text-amber-300",
        ),
        rx.icon("chevron-right", class_name="h-4 w-4 text-zinc-600"),
        href=f"/game/room/{room['id']}",
        class_name=(
            "flex items-center gap-3 rounded-xl border border-zinc-800 "
            "bg-[#0A0B0E] px-3 py-2 hover:border-emerald-500/60"
        ),
    )


def skeleton_tiles() -> rx.Component:
    return rx.el.div(
        rx.el.div(class_name="h-40 animate-pulse rounded-2xl bg-zinc-900"),
        rx.el.div(class_name="h-40 animate-pulse rounded-2xl bg-zinc-900"),
        rx.el.div(class_name="h-40 animate-pulse rounded-2xl bg-zinc-900"),
        rx.el.div(class_name="h-40 animate-pulse rounded-2xl bg-zinc-900"),
        class_name="grid w-full gap-4 sm:grid-cols-2 lg:grid-cols-4",
    )


def hub_body() -> rx.Component:
    return rx.el.div(
        rx.el.div(
            rx.el.div(
                rx.el.h1(
                    "Salle de jeux TATA",
                    class_name="text-xl font-black tracking-tight text-white",
                ),
                rx.el.p(
                    NO_PURCHASE_COPY,
                    class_name="mt-1 max-w-2xl text-xs text-zinc-500",
                ),
                class_name="min-w-0 flex-1",
            ),
            rx.el.div(
                rx.el.input(
                    placeholder="Code de salle",
                    default_value=GamesState.join_code,
                    on_change=GamesState.set_join_code.debounce(300),
                    aria_label="Code de salle privee",
                    class_name=(
                        "w-36 rounded-xl border border-zinc-800 bg-[#0A0B0E] "
                        "px-3 py-2 text-sm text-white outline-hidden "
                        "focus:border-emerald-500"
                    ),
                ),
                rx.el.button(
                    "Rejoindre",
                    on_click=GamesState.join_by_code,
                    class_name=(
                        "rounded-xl border border-emerald-500/60 px-3 py-2 "
                        "text-xs font-bold text-emerald-400 "
                        "hover:bg-emerald-500/10"
                    ),
                ),
                class_name="flex items-center gap-2",
            ),
            class_name="flex flex-col gap-3 sm:flex-row sm:items-center",
        ),
        rx.cond(
            GamesState.loading,
            skeleton_tiles(),
            rx.cond(
                GamesState.cards.length() > 0,
                rx.el.div(
                    rx.foreach(GamesState.cards, game_card),
                    class_name="grid w-full gap-4 sm:grid-cols-2 lg:grid-cols-4",
                ),
                rx.el.p(
                    "Aucun jeu disponible pour le moment.",
                    class_name="text-sm text-zinc-500",
                ),
            ),
        ),
        rx.el.div(
            rx.el.h2(
                "Mes salles",
                class_name=(
                    "mb-2 text-xs font-bold uppercase tracking-wider "
                    "text-zinc-400"
                ),
            ),
            rx.cond(
                GamesState.my_rooms.length() > 0,
                rx.el.div(
                    rx.foreach(GamesState.my_rooms, my_room_row),
                    class_name="grid gap-2 sm:grid-cols-2 lg:grid-cols-3",
                ),
                rx.el.p(
                    "Vous n'avez rejoint aucune salle. Choisissez un jeu "
                    "ci-dessus.",
                    class_name="text-sm text-zinc-500",
                ),
            ),
            class_name="w-full",
        ),
        rx.cond(
            GamesState.error != "",
            rx.el.p(
                GamesState.error,
                class_name="text-sm font-semibold text-rose-400",
            ),
        ),
        class_name="flex w-full flex-col gap-5",
    )


def games_page() -> rx.Component:
    return dark_page("Jeux", hub_body(), "jeux", "/")
