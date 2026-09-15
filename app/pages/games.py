"""Bright TATA Games discovery home: Domino, Ludo and Loto only."""

from __future__ import annotations

import reflex as rx

from app.components.bright_shell import bright_page
from app.states.auth_state import AuthState
from app.states.games_state import GameCard, GamesState, RoomRow


def live_dot(is_live: bool | rx.Var, label: str | rx.Var) -> rx.Component:
    return rx.el.div(
        rx.el.span(
            class_name=rx.cond(
                is_live,
                "size-2 shrink-0 rounded-full bg-[#22D3EE]",
                "size-2 shrink-0 rounded-full bg-slate-300",
            )
        ),
        rx.el.span(
            label,
            class_name=rx.cond(
                is_live,
                "text-[11px] font-semibold text-[#0E7FC4]",
                "text-[11px] font-semibold text-slate-400",
            ),
        ),
        class_name="flex min-w-0 items-center gap-1.5",
    )


def meta_pill(label: str | rx.Var, icon: str) -> rx.Component:
    return rx.el.span(
        rx.icon(icon, class_name="h-3 w-3 text-[#1E9EF5]"),
        rx.el.span(label, class_name="text-[11px] font-semibold"),
        class_name=(
            "flex w-fit items-center gap-1 rounded-md border "
            "border-slate-200 bg-white px-2 py-1 text-[#071A33]"
        ),
    )


def play_link(slug: str | rx.Var, compact: bool = False) -> rx.Component:
    return rx.el.a(
        rx.el.span("Jouer"),
        rx.icon("play", class_name="h-3.5 w-3.5"),
        href=f"/games/{slug}",
        class_name=(
            "flex w-fit shrink-0 items-center gap-1 rounded-lg bg-[#1E9EF5] "
            "text-xs font-bold text-white active:bg-[#0E7FC4] "
            "hover:bg-[#1789DA] "
            + (rx.cond(compact, "px-3 py-1.5", "px-4 py-2 text-sm"))
        ),
    )


def solo_badge() -> rx.Component:
    return rx.el.span(
        "SOLO",
        class_name=(
            "w-fit rounded-sm border border-[#22D3EE]/60 bg-[#ECFEFF] "
            "px-1 py-px text-[9px] font-bold tracking-wider text-[#0E7490]"
        ),
    )


def solo_button(slug: str | rx.Var, compact: bool = False) -> rx.Component:
    """Secondary cyan outlined one-click practice entry."""
    busy = GamesState.solo_busy & (GamesState.solo_slug == slug)
    return rx.el.button(
        rx.cond(
            busy,
            rx.icon("loader-circle", class_name="h-3.5 w-3.5 animate-spin"),
            rx.icon("flask-conical", class_name="h-3.5 w-3.5"),
        ),
        rx.el.span(rx.cond(busy, "Ouverture...", "Tester seul")),
        solo_badge(),
        on_click=lambda: GamesState.start_solo_test(slug),
        disabled=GamesState.solo_busy,
        title="Mode test solo: partie d'entrainement immediate",
        class_name=(
            "flex w-fit shrink-0 items-center gap-1 rounded-lg border "
            "border-[#22D3EE] bg-white font-bold text-[#0E7490] "
            "hover:bg-[#ECFEFF] disabled:opacity-60 "
            + (
                rx.cond(
                    compact, "px-2.5 py-1.5 text-[11px]", "px-3 py-2 text-xs"
                )
            )
        ),
    )


def solo_banner() -> rx.Component:
    return rx.el.div(
        rx.el.div(
            rx.icon("flask-conical", class_name="h-4 w-4 text-[#0E7490]"),
            class_name=(
                "flex size-8 shrink-0 items-center justify-center rounded-lg "
                "border border-[#22D3EE]/60 bg-[#ECFEFF]"
            ),
        ),
        rx.el.div(
            rx.el.div(
                rx.el.p(
                    "Mode test solo",
                    class_name="text-xs font-bold text-[#071A33]",
                ),
                solo_badge(),
                class_name="flex items-center gap-1.5",
            ),
            rx.el.p(
                "Ouvrez une partie instantanement, sans attendre d'autres "
                "joueurs. Session d'entrainement privee: elle n'affecte pas "
                "les salles publiques ni vos statistiques.",
                class_name=(
                    "mt-0.5 text-[11px] font-medium leading-relaxed "
                    "text-slate-600"
                ),
            ),
            class_name="min-w-0 flex-1",
        ),
        class_name=(
            "flex items-start gap-2 rounded-xl border border-[#22D3EE]/40 "
            "bg-[#F5FEFF] px-3 py-2.5"
        ),
    )


# ------------------------------------------------------------------ header row
def welcome_row() -> rx.Component:
    return rx.el.div(
        rx.el.div(
            rx.el.p(
                f"Salut {AuthState.display_name}",
                class_name="text-lg font-bold leading-tight text-[#071A33]",
            ),
            rx.el.p(
                f"{GamesState.total_open_rooms} salles ouvertes • "
                f"{GamesState.total_live_players} joueurs en direct",
                class_name="mt-0.5 text-xs font-medium text-slate-500",
            ),
            class_name="min-w-0 flex-1",
        ),
        rx.el.a(
            rx.icon("trophy", class_name="h-4 w-4 text-[#1E9EF5]"),
            rx.el.span("Classement", class_name="text-xs font-bold"),
            href="/leaderboard",
            title="Statistiques et classement des joueurs",
            class_name=(
                "flex w-fit shrink-0 items-center gap-1.5 rounded-lg border "
                "border-slate-200 bg-white px-3 py-2 text-[#071A33] "
                "active:bg-slate-100 hover:border-[#1E9EF5]/60"
            ),
        ),
        class_name="flex items-center gap-3",
    )


def search_row() -> rx.Component:
    return rx.el.div(
        rx.el.div(
            rx.icon(
                "search",
                class_name=(
                    "pointer-events-none absolute left-3 top-1/2 h-4 w-4 "
                    "-translate-y-1/2 text-slate-400"
                ),
            ),
            rx.el.input(
                placeholder="Rechercher un jeu, un mode...",
                default_value=GamesState.search_text,
                on_change=GamesState.set_search_text.debounce(200),
                aria_label="Rechercher un jeu",
                class_name=(
                    "w-full rounded-lg border border-slate-200 bg-white "
                    "py-2.5 pl-9 pr-9 text-sm font-medium text-[#071A33] "
                    "outline-hidden placeholder:text-slate-400 "
                    "focus:border-[#1E9EF5] focus:ring-2 "
                    "focus:ring-[#1E9EF5]/20"
                ),
            ),
            rx.cond(
                GamesState.search_text != "",
                rx.el.button(
                    rx.icon("x", class_name="h-4 w-4"),
                    on_click=GamesState.clear_search,
                    aria_label="Effacer la recherche",
                    class_name=(
                        "absolute right-2 top-1/2 flex size-6 -translate-y-1/2 "
                        "items-center justify-center rounded-md text-slate-400 "
                        "hover:text-[#071A33]"
                    ),
                ),
            ),
            class_name="relative min-w-0 flex-1",
        ),
        class_name="flex items-center gap-2",
    )


def category_chip(item: dict[str, str]) -> rx.Component:
    return rx.el.button(
        item["label"],
        on_click=lambda: GamesState.set_category(item["value"]),
        class_name=rx.cond(
            GamesState.category == item["value"],
            "shrink-0 rounded-lg bg-[#071A33] px-3.5 py-1.5 text-xs "
            "font-bold text-white",
            "shrink-0 rounded-lg border border-slate-200 bg-white px-3.5 "
            "py-1.5 text-xs font-semibold text-slate-600 "
            "active:bg-slate-100 hover:border-[#1E9EF5]/60",
        ),
    )


def category_row() -> rx.Component:
    return rx.el.div(
        rx.el.div(
            rx.foreach(GamesState.categories, category_chip),
            class_name="flex items-center gap-2",
        ),
        class_name="-mx-3 overflow-x-auto px-3 pb-1 sm:mx-0 sm:px-0",
    )


def join_code_row() -> rx.Component:
    return rx.el.div(
        rx.el.div(
            rx.icon("key-round", class_name="h-4 w-4 text-[#1E9EF5]"),
            rx.el.span(
                "Salle privee",
                class_name="text-xs font-bold text-[#071A33]",
            ),
            class_name="flex shrink-0 items-center gap-1.5",
        ),
        rx.el.input(
            placeholder="CODE",
            default_value=GamesState.join_code,
            on_change=GamesState.set_join_code.debounce(250),
            aria_label="Code de salle privee",
            class_name=(
                "w-24 min-w-0 flex-1 rounded-lg border border-slate-200 "
                "bg-white px-3 py-2 font-mono text-sm font-bold uppercase "
                "tracking-widest text-[#071A33] outline-hidden "
                "focus:border-[#1E9EF5] sm:w-36 sm:flex-none"
            ),
        ),
        rx.el.button(
            "Rejoindre",
            on_click=GamesState.join_by_code,
            class_name=(
                "shrink-0 rounded-lg bg-[#22D3EE] px-3 py-2 text-xs "
                "font-bold text-[#071A33] active:bg-[#0FB6D0] "
                "hover:bg-[#14C4DE]"
            ),
        ),
        class_name=(
            "flex items-center gap-2 border-y border-slate-200 bg-white "
            "px-3 py-2"
        ),
    )


# --------------------------------------------------------------- game sections
def section_title(label: str, hint: str | rx.Var) -> rx.Component:
    return rx.el.div(
        rx.el.h2(
            label,
            class_name=(
                "text-xs font-bold uppercase tracking-[0.14em] text-[#071A33]"
            ),
        ),
        rx.el.span(
            hint,
            class_name="text-[11px] font-medium text-slate-400",
        ),
        class_name="flex items-baseline justify-between gap-2",
    )


def featured_lead(card: GameCard) -> rx.Component:
    return rx.el.div(
        rx.el.div(
            rx.image(
                src=card["cover"],
                alt=card["name"],
                class_name="h-full w-full object-cover",
            ),
            rx.el.span(
                "A la une",
                class_name=(
                    "absolute left-2 top-2 rounded-md bg-[#071A33]/85 px-2 "
                    "py-1 text-[10px] font-bold uppercase tracking-wider "
                    "text-white"
                ),
            ),
            class_name=(
                "relative h-36 w-full overflow-hidden bg-[#E4F2FE] "
                "sm:h-full sm:w-48 sm:shrink-0"
            ),
        ),
        rx.el.div(
            rx.el.div(
                rx.el.p(
                    card["name"],
                    class_name="text-base font-bold text-[#071A33]",
                ),
                rx.el.p(
                    card["subtitle"],
                    class_name="mt-0.5 text-xs font-medium text-slate-500",
                ),
                class_name="min-w-0",
            ),
            rx.el.div(
                meta_pill(card["mode"], "gamepad-2"),
                meta_pill(card["player_range"], "users"),
                class_name="mt-2 flex flex-wrap gap-1.5",
            ),
            rx.el.div(
                live_dot(card["is_live"], card["live_label"]),
                rx.el.div(
                    solo_button(card["slug"], True),
                    play_link(card["slug"]),
                    class_name="flex items-center gap-2",
                ),
                class_name="mt-3 flex flex-wrap items-center justify-between gap-2",
            ),
            class_name="flex min-w-0 flex-1 flex-col justify-center p-3",
        ),
        class_name=(
            "flex w-full flex-col overflow-hidden rounded-xl border "
            "border-slate-200 bg-white sm:flex-row"
        ),
    )


def supporting_tile(card: GameCard) -> rx.Component:
    return rx.el.a(
        rx.image(
            src=card["cover"],
            alt=card["name"],
            class_name=("h-20 w-full rounded-lg object-cover bg-[#E4F2FE]"),
        ),
        rx.el.p(
            card["name"],
            class_name="mt-2 text-xs font-bold text-[#071A33]",
        ),
        rx.el.p(
            card["mode"],
            class_name="text-[11px] font-medium text-slate-500",
        ),
        live_dot(card["is_live"], card["live_label"]),
        href=f"/games/{card['slug']}",
        class_name=(
            "flex min-w-0 flex-col gap-0.5 rounded-xl border "
            "border-slate-200 bg-white p-2 active:bg-slate-50 "
            "hover:border-[#1E9EF5]/60"
        ),
    )


def popular_card(card: GameCard) -> rx.Component:
    return rx.el.div(
        rx.image(
            src=card["cover"],
            alt=card["name"],
            class_name="h-24 w-full rounded-lg object-cover bg-[#E4F2FE]",
        ),
        rx.el.p(
            card["name"],
            class_name="mt-2 text-xs font-bold text-[#071A33]",
        ),
        rx.el.p(
            card["player_range"],
            class_name="text-[11px] font-medium text-slate-500",
        ),
        live_dot(card["is_live"], card["live_label"]),
        play_link(card["slug"], True),
        solo_button(card["slug"], True),
        class_name=(
            "flex w-40 shrink-0 flex-col gap-1 rounded-xl border "
            "border-slate-200 bg-white p-2"
        ),
    )


def all_games_row(card: GameCard) -> rx.Component:
    return rx.el.div(
        rx.image(
            src=card["cover"],
            alt=card["name"],
            class_name=(
                "size-14 shrink-0 rounded-lg object-cover bg-[#E4F2FE]"
            ),
        ),
        rx.el.div(
            rx.el.div(
                rx.el.p(
                    card["name"],
                    class_name="text-sm font-bold text-[#071A33]",
                ),
                rx.el.span(
                    card["category_label"],
                    class_name=(
                        "w-fit rounded-md bg-[#E4F2FE] px-1.5 py-0.5 "
                        "text-[10px] font-bold uppercase tracking-wide "
                        "text-[#0E7FC4]"
                    ),
                ),
                class_name="flex flex-wrap items-center gap-2",
            ),
            rx.el.p(
                f"{card['mode']} • {card['player_range']}",
                class_name="mt-0.5 text-[11px] font-medium text-slate-500",
            ),
            live_dot(card["is_live"], card["live_label"]),
            class_name="min-w-0 flex-1",
        ),
        rx.el.div(
            play_link(card["slug"], True),
            solo_button(card["slug"], True),
            class_name="flex shrink-0 flex-col items-end gap-1.5",
        ),
        class_name=(
            "flex items-center gap-3 border-b border-slate-200 bg-white "
            "px-3 py-3 last:border-b-0 active:bg-slate-50"
        ),
    )


def empty_search() -> rx.Component:
    return rx.el.div(
        rx.icon("search-x", class_name="h-6 w-6 text-slate-300"),
        rx.el.p(
            "Aucun jeu ne correspond a cette recherche.",
            class_name="mt-2 text-sm font-semibold text-[#071A33]",
        ),
        rx.el.p(
            "Essayez Domino, Ludo ou Loto.",
            class_name="text-xs font-medium text-slate-500",
        ),
        rx.el.button(
            "Reinitialiser",
            on_click=[
                GamesState.clear_search,
                lambda: GamesState.set_category("tous"),
            ],
            class_name=(
                "mt-3 w-fit rounded-lg border border-slate-200 bg-white "
                "px-3 py-1.5 text-xs font-bold text-[#071A33] "
                "active:bg-slate-100"
            ),
        ),
        class_name=(
            "flex flex-col items-center border border-slate-200 bg-white "
            "px-4 py-8 text-center"
        ),
    )


# ------------------------------------------------------------------- my rooms
def my_room_row(room: RoomRow) -> rx.Component:
    return rx.el.div(
        rx.el.div(
            rx.el.div(
                rx.el.p(
                    room["game_name"],
                    class_name="text-xs font-bold text-[#071A33]",
                ),
                rx.el.span(
                    room["status_label"],
                    class_name=(
                        "w-fit rounded-md bg-[#E4F2FE] px-1.5 py-0.5 "
                        "text-[10px] font-bold uppercase text-[#0E7FC4]"
                    ),
                ),
                class_name="flex flex-wrap items-center gap-2",
            ),
            rx.el.p(
                f"{room['name']} • code {room['code']}",
                class_name="mt-0.5 truncate text-[11px] text-slate-500",
            ),
            rx.el.div(
                rx.el.div(
                    class_name=(
                        "h-1.5 rounded-full bg-[#1E9EF5] transition-all"
                    ),
                    style={
                        "width": rx.cond(
                            room["max_players"] > 0,
                            f"{room['player_count'] * 100 / room['max_players']}%",
                            "0%",
                        )
                    },
                ),
                class_name="mt-2 h-1.5 w-full rounded-full bg-slate-100",
            ),
            class_name="min-w-0 flex-1",
        ),
        rx.el.div(
            rx.el.span(
                f"{room['player_count']}/{room['max_players']}",
                class_name=(
                    "text-[11px] font-bold tabular-nums text-[#071A33]"
                ),
            ),
            rx.el.a(
                "Reprendre",
                href=f"/game/room/{room['id']}",
                class_name=(
                    "w-fit rounded-lg bg-[#071A33] px-3 py-1.5 text-xs "
                    "font-bold text-white active:bg-[#0B2647]"
                ),
            ),
            class_name="flex shrink-0 flex-col items-end gap-1.5",
        ),
        class_name=(
            "flex items-center gap-3 border-b border-slate-200 bg-white "
            "px-3 py-3 last:border-b-0"
        ),
    )


def my_rooms_section() -> rx.Component:
    return rx.el.section(
        section_title("Mes salles actives", "Domino • Ludo • Loto"),
        rx.cond(
            GamesState.my_rooms.length() > 0,
            rx.el.div(
                rx.foreach(GamesState.my_rooms, my_room_row),
                class_name=(
                    "mt-2 overflow-hidden rounded-xl border border-slate-200"
                ),
            ),
            rx.el.div(
                rx.icon("door-open", class_name="h-5 w-5 text-slate-300"),
                rx.el.p(
                    "Vous n'avez aucune salle en cours.",
                    class_name="mt-1.5 text-sm font-semibold text-[#071A33]",
                ),
                rx.el.p(
                    "Choisissez un jeu ci-dessus ou entrez un code de salle.",
                    class_name="text-xs font-medium text-slate-500",
                ),
                class_name=(
                    "mt-2 flex flex-col items-center rounded-xl border "
                    "border-dashed border-slate-200 bg-white px-4 py-6 "
                    "text-center"
                ),
            ),
        ),
        class_name="w-full",
    )


# ------------------------------------------------------------------ skeletons
def skeleton() -> rx.Component:
    return rx.el.div(
        rx.el.div(class_name="h-10 animate-pulse rounded-lg bg-slate-200"),
        rx.el.div(class_name="h-8 animate-pulse rounded-lg bg-slate-200"),
        rx.el.div(class_name="h-40 animate-pulse rounded-xl bg-slate-200"),
        rx.el.div(
            rx.el.div(class_name="h-28 animate-pulse rounded-xl bg-slate-200"),
            rx.el.div(class_name="h-28 animate-pulse rounded-xl bg-slate-200"),
            class_name="grid grid-cols-2 gap-2",
        ),
        rx.el.div(class_name="h-48 animate-pulse rounded-xl bg-slate-200"),
        class_name="flex w-full flex-col gap-3",
    )


def discovery_body() -> rx.Component:
    return rx.el.div(
        welcome_row(),
        search_row(),
        category_row(),
        solo_banner(),
        rx.cond(
            GamesState.solo_error != "",
            rx.el.p(
                GamesState.solo_error,
                class_name="text-xs font-semibold text-rose-500",
            ),
        ),
        join_code_row(),
        rx.cond(
            GamesState.error != "",
            rx.el.p(
                GamesState.error,
                class_name="text-xs font-semibold text-rose-500",
            ),
        ),
        rx.cond(
            GamesState.has_results,
            rx.el.div(
                rx.el.section(
                    section_title("A la une", "Selection TATA"),
                    rx.el.div(
                        rx.foreach(GamesState.featured_card, featured_lead),
                        class_name="mt-2",
                    ),
                    rx.el.div(
                        rx.foreach(
                            GamesState.supporting_cards, supporting_tile
                        ),
                        class_name="mt-2 grid grid-cols-2 gap-2",
                    ),
                    class_name="w-full",
                ),
                rx.el.section(
                    section_title("Populaire maintenant", "Compte en direct"),
                    rx.el.div(
                        rx.el.div(
                            rx.foreach(GamesState.popular_cards, popular_card),
                            class_name="flex items-stretch gap-2",
                        ),
                        class_name=(
                            "-mx-3 mt-2 overflow-x-auto px-3 pb-1 sm:mx-0 "
                            "sm:px-0"
                        ),
                    ),
                    class_name="w-full",
                ),
                rx.el.section(
                    section_title("Tous les jeux", "3 jeux disponibles"),
                    rx.el.div(
                        rx.foreach(GamesState.filtered_cards, all_games_row),
                        class_name=(
                            "mt-2 overflow-hidden rounded-xl border "
                            "border-slate-200"
                        ),
                    ),
                    class_name="w-full",
                ),
                class_name="flex w-full flex-col gap-5",
            ),
            empty_search(),
        ),
        my_rooms_section(),
        class_name="flex w-full flex-col gap-3",
    )


def games_page() -> rx.Component:
    return bright_page(
        rx.cond(GamesState.loading, skeleton(), discovery_body()),
        "jeux",
    )
