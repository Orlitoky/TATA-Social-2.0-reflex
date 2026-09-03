"""Per-game lobby: open rooms, room creation with per-game options."""

from __future__ import annotations

import reflex as rx

from app.components.game_shell import dark_page, jewel_tag, medallion
from app.states.games_state import GamesState, RoomRow


def room_card(room: RoomRow) -> rx.Component:
    return rx.el.div(
        rx.el.div(
            rx.el.div(
                rx.el.p(
                    room["name"],
                    class_name="truncate text-sm font-bold text-white",
                ),
                rx.el.p(
                    f"Hote {room['host_name']} • code {room['code']}",
                    class_name="text-[11px] text-zinc-500",
                ),
                class_name="min-w-0 flex-1",
            ),
            rx.cond(
                room["host_online"],
                rx.el.span(
                    class_name=(
                        "size-2.5 rounded-full bg-emerald-500 "
                        "shadow-[0_0_8px_#10B981]"
                    )
                ),
                rx.el.span(class_name="size-2.5 rounded-full bg-zinc-700"),
            ),
            class_name="flex items-start gap-2",
        ),
        rx.el.div(
            jewel_tag(room["status_label"], "emerald"),
            rx.cond(
                room["tier_label"] != "",
                jewel_tag(room["tier_label"], "gold"),
                rx.fragment(),
            ),
            jewel_tag(f"{room['entry_coins']} pts", "cyan"),
            rx.cond(
                room["is_private"],
                jewel_tag("Privee", "ruby"),
                rx.fragment(),
            ),
            class_name="mt-2 flex flex-wrap gap-1.5",
        ),
        rx.el.div(
            rx.el.span(
                f"{room['player_count']}/{room['max_players']} joueurs • pot "
                f"{room['pot_coins']} pts",
                class_name="text-[11px] font-semibold text-zinc-400",
            ),
            rx.cond(
                room["is_private"] & ~room["joined"],
                rx.el.div(
                    rx.el.input(
                        placeholder="Code",
                        default_value="",
                        on_change=GamesState.set_join_code.debounce(300),
                        aria_label="Code de la salle privee",
                        class_name=(
                            "w-20 rounded-lg border border-zinc-800 "
                            "bg-[#0A0B0E] px-2 py-1.5 text-xs text-white "
                            "outline-hidden focus:border-emerald-500"
                        ),
                    ),
                    rx.el.button(
                        "JOUER",
                        on_click=lambda: GamesState.join_room(
                            room["id"], GamesState.join_code
                        ),
                        class_name=(
                            "rounded-lg bg-emerald-500 px-3 py-1.5 text-xs "
                            "font-black text-black hover:bg-emerald-400"
                        ),
                    ),
                    class_name="flex items-center gap-1.5",
                ),
                rx.el.button(
                    rx.cond(room["joined"], "REPRENDRE", "JOUER"),
                    on_click=lambda: GamesState.join_room(room["id"], ""),
                    disabled=room["full"] & ~room["joined"],
                    class_name=(
                        "rounded-lg bg-emerald-500 px-4 py-1.5 text-xs "
                        "font-black tracking-wide text-black "
                        "hover:bg-emerald-400 disabled:opacity-40"
                    ),
                ),
            ),
            class_name="mt-3 flex items-center justify-between gap-2",
        ),
        class_name=(
            "flex flex-col rounded-2xl border border-zinc-800 "
            "bg-[linear-gradient(160deg,#111317,#0A0B0E)] p-4"
        ),
    )


def field_label(label: str) -> rx.Component:
    return rx.el.label(label, class_name="text-[11px] font-bold text-zinc-400")


INPUT_CLASS = (
    "mt-1 w-full rounded-xl border border-zinc-800 bg-[#0A0B0E] px-3 py-2 "
    "text-sm text-white outline-hidden focus:border-emerald-500"
)


def loto_options() -> rx.Component:
    return rx.el.div(
        field_label("Niveau"),
        rx.el.div(
            rx.el.select(
                rx.foreach(
                    GamesState.tier_options,
                    lambda tier: rx.el.option(
                        f"{tier['label']} - {tier['price']} pts / carton "
                        f"(max {tier['max']})",
                        value=tier["key"],
                    ),
                ),
                name="tier",
                default_value="bronze_lite",
                class_name=f"{INPUT_CLASS} appearance-none pr-8",
            ),
            rx.icon(
                "chevron-down",
                class_name="pointer-events-none absolute right-3 top-3.5 h-4 w-4 text-zinc-500",
            ),
            class_name="relative",
        ),
        class_name="w-full",
    )


def domino_options() -> rx.Component:
    return rx.el.div(
        field_label("Objectif Maty"),
        rx.el.div(
            rx.el.select(
                rx.foreach(
                    GamesState.maty_targets,
                    lambda target: rx.el.option(
                        f"Maty {target}", value=target.to_string()
                    ),
                ),
                name="maty",
                default_value="50",
                class_name=f"{INPUT_CLASS} appearance-none pr-8",
            ),
            rx.icon(
                "chevron-down",
                class_name="pointer-events-none absolute right-3 top-3.5 h-4 w-4 text-zinc-500",
            ),
            class_name="relative",
        ),
        rx.el.label(
            rx.el.input(
                type="checkbox",
                name="no_double_six",
                class_name="size-4 accent-emerald-500",
            ),
            rx.el.span(
                "Sans Double-Six",
                class_name="text-xs font-semibold text-zinc-300",
            ),
            class_name="mt-3 flex items-center gap-2",
        ),
        rx.el.label(
            rx.el.input(
                type="checkbox",
                name="one_on_blank",
                class_name="size-4 accent-emerald-500",
            ),
            rx.el.span(
                "Un sur Blanc",
                class_name="text-xs font-semibold text-zinc-300",
            ),
            class_name="mt-2 flex items-center gap-2",
        ),
        class_name="w-full",
    )


def create_form() -> rx.Component:
    return rx.cond(
        GamesState.create_open,
        rx.el.div(
            rx.el.div(
                rx.el.div(
                    rx.el.h2(
                        "Creer une salle",
                        class_name="text-base font-bold text-white",
                    ),
                    rx.el.button(
                        rx.icon("x", class_name="h-4 w-4"),
                        on_click=GamesState.toggle_create,
                        aria_label="Fermer",
                        class_name="text-zinc-500 hover:text-white",
                    ),
                    class_name=(
                        "flex items-center justify-between border-b "
                        "border-zinc-800 px-4 py-3"
                    ),
                ),
                rx.el.form(
                    field_label("Nom de la salle"),
                    rx.el.input(
                        name="name",
                        placeholder="Ma salle",
                        class_name=INPUT_CLASS,
                    ),
                    rx.el.div(
                        rx.el.div(
                            field_label("Joueurs max"),
                            rx.el.input(
                                name="max_players",
                                type="number",
                                min=2,
                                default_value="4",
                                class_name=INPUT_CLASS,
                            ),
                            class_name="flex-1",
                        ),
                        rx.el.div(
                            field_label("Mise (points)"),
                            rx.el.input(
                                name="entry_coins",
                                type="number",
                                min=0,
                                default_value="100",
                                class_name=INPUT_CLASS,
                            ),
                            class_name="flex-1",
                        ),
                        class_name="mt-3 flex gap-3",
                    ),
                    rx.cond(GamesState.is_loto, loto_options(), rx.fragment()),
                    rx.cond(
                        GamesState.is_domino, domino_options(), rx.fragment()
                    ),
                    rx.el.div(
                        field_label("Code prive (optionnel)"),
                        rx.el.input(
                            name="room_code",
                            placeholder="Laisser vide pour une salle publique",
                            class_name=INPUT_CLASS,
                        ),
                        class_name="mt-3",
                    ),
                    rx.el.p(
                        "La mise est prelevee en points internes uniquement. "
                        "Aucun achat, depot ou retrait n'existe.",
                        class_name="mt-3 text-[11px] text-zinc-500",
                    ),
                    rx.el.button(
                        "Creer et rejoindre",
                        type="submit",
                        class_name=(
                            "mt-4 w-full rounded-xl bg-emerald-500 py-2.5 "
                            "text-sm font-bold text-black hover:bg-emerald-400"
                        ),
                    ),
                    on_submit=GamesState.create_room,
                    class_name="p-4",
                ),
                class_name=(
                    "w-full max-w-md overflow-hidden rounded-2xl border "
                    "border-zinc-800 bg-[#0C0D10]"
                ),
            ),
            class_name=(
                "fixed inset-0 z-50 flex items-center justify-center "
                "overflow-y-auto bg-black/70 p-4"
            ),
        ),
    )


def lobby_body() -> rx.Component:
    return rx.el.div(
        rx.el.div(
            medallion("gamepad-2", "size-16"),
            rx.el.div(
                rx.el.h1(
                    GamesState.active_game_name,
                    class_name="text-xl font-black tracking-tight text-white",
                ),
                rx.el.p(
                    GamesState.active_game_description,
                    class_name="mt-1 text-xs text-zinc-400",
                ),
                class_name="min-w-0 flex-1",
            ),
            rx.el.button(
                rx.icon("plus", class_name="h-4 w-4"),
                "Creer une salle",
                on_click=GamesState.toggle_create,
                class_name=(
                    "flex items-center gap-2 rounded-xl bg-emerald-500 px-4 "
                    "py-2.5 text-xs font-black text-black "
                    "hover:bg-emerald-400"
                ),
            ),
            class_name=(
                "flex flex-col gap-3 rounded-2xl border border-zinc-800 "
                "bg-[#0C0D10] p-4 sm:flex-row sm:items-center"
            ),
        ),
        rx.cond(
            GamesState.loading,
            rx.el.div(
                rx.el.div(
                    class_name="h-32 animate-pulse rounded-2xl bg-zinc-900"
                ),
                rx.el.div(
                    class_name="h-32 animate-pulse rounded-2xl bg-zinc-900"
                ),
                class_name="grid gap-4 sm:grid-cols-2 lg:grid-cols-3",
            ),
            rx.cond(
                GamesState.rooms.length() > 0,
                rx.el.div(
                    rx.foreach(GamesState.rooms, room_card),
                    class_name="grid gap-4 sm:grid-cols-2 lg:grid-cols-3",
                ),
                rx.el.div(
                    rx.icon("door-open", class_name="h-8 w-8 text-zinc-700"),
                    rx.el.p(
                        "Aucune salle ouverte. Creez la premiere.",
                        class_name="mt-2 text-sm text-zinc-500",
                    ),
                    class_name=(
                        "flex flex-col items-center justify-center "
                        "rounded-2xl border border-dashed border-zinc-800 "
                        "py-12"
                    ),
                ),
            ),
        ),
        create_form(),
        class_name="flex w-full flex-col gap-4",
    )


def game_lobby_page() -> rx.Component:
    return dark_page(
        GamesState.active_game_name, lobby_body(), "jeux", "/games"
    )
