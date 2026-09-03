"""Route-driven authoritative play room: /game/room/[room_id]."""

from __future__ import annotations

import reflex as rx

from app.components.boards import (
    domino_result_modal,
    game_board,
    loto_controls,
    panel,
    section_title,
)
from app.components.game_shell import dark_page, jewel_tag
from app.components.ui import avatar
from app.states.room_state import ActivityRow, PlayerRow, ReactionRow, RoomState


def player_tile(player: PlayerRow) -> rx.Component:
    return rx.el.div(
        rx.el.div(
            avatar(player["avatar_url"], player["avatar_remote"], "size-9"),
            rx.cond(
                player["is_online"],
                rx.el.span(
                    class_name=(
                        "absolute -bottom-0.5 -right-0.5 size-3 rounded-full "
                        "border-2 border-[#0C0D10] bg-emerald-500"
                    )
                ),
                rx.fragment(),
            ),
            class_name="relative shrink-0",
        ),
        rx.el.div(
            rx.el.p(
                player["name"],
                class_name="truncate text-xs font-bold text-white",
            ),
            rx.el.div(
                rx.cond(
                    player["is_host"],
                    rx.el.span(
                        "Hote",
                        class_name="text-[10px] font-bold text-amber-300",
                    ),
                    rx.fragment(),
                ),
                rx.cond(
                    player["is_ready"],
                    rx.el.span(
                        "Pret",
                        class_name="text-[10px] font-bold text-emerald-400",
                    ),
                    rx.el.span(
                        "En attente",
                        class_name="text-[10px] font-semibold text-zinc-500",
                    ),
                ),
                rx.cond(
                    player["cards"] > 0,
                    rx.el.span(
                        f"{player['cards']} carton(s)",
                        class_name="text-[10px] font-semibold text-cyan-300",
                    ),
                    rx.fragment(),
                ),
                rx.cond(
                    player["hand_count"] > 0,
                    rx.el.span(
                        f"{player['hand_count']} en main",
                        class_name="text-[10px] font-semibold text-cyan-300",
                    ),
                    rx.fragment(),
                ),
                class_name="flex flex-wrap items-center gap-2",
            ),
            class_name="min-w-0 flex-1",
        ),
        rx.el.div(
            rx.icon("heart", class_name="h-3 w-3 text-rose-500"),
            rx.icon(
                "heart",
                class_name=rx.cond(
                    player["hearts"] > 1,
                    "h-3 w-3 text-rose-500",
                    "h-3 w-3 text-zinc-700",
                ),
            ),
            rx.icon(
                "heart",
                class_name=rx.cond(
                    player["hearts"] > 2,
                    "h-3 w-3 text-rose-500",
                    "h-3 w-3 text-zinc-700",
                ),
            ),
            class_name="flex items-center gap-0.5",
        ),
        class_name=rx.cond(
            player["is_turn"],
            "flex items-center gap-2 rounded-xl border border-emerald-500/60 bg-emerald-500/5 p-2",
            "flex items-center gap-2 rounded-xl border border-zinc-800 bg-[#0A0B0E] p-2",
        ),
    )


def activity_row(row: ActivityRow) -> rx.Component:
    return rx.el.div(
        rx.el.span(
            row["time_label"],
            class_name="shrink-0 font-mono text-[10px] text-zinc-600",
        ),
        rx.el.span(row["text"], class_name="text-[11px] text-zinc-300"),
        class_name="flex items-start gap-2 py-1",
    )


def reaction_bubble(row: ReactionRow) -> rx.Component:
    return rx.el.div(
        rx.el.span(row["emoji"], class_name="text-base"),
        rx.el.span(
            row["name"], class_name="text-[10px] font-semibold text-zinc-400"
        ),
        class_name=(
            "flex items-center gap-1 rounded-full border border-zinc-800 "
            "bg-[#0A0B0E] px-2 py-1"
        ),
    )


def reaction_panel() -> rx.Component:
    return panel(
        section_title("smile", "Reactions"),
        rx.el.div(
            rx.el.button(
                "Emoji",
                on_click=lambda: RoomState.set_reaction_tab("emoji"),
                class_name=rx.cond(
                    RoomState.reaction_tab == "emoji",
                    "flex-1 rounded-lg bg-zinc-800 py-1.5 text-xs font-bold text-white",
                    "flex-1 rounded-lg py-1.5 text-xs font-bold text-zinc-500",
                ),
            ),
            rx.el.button(
                "Gestes",
                on_click=lambda: RoomState.set_reaction_tab("geste"),
                class_name=rx.cond(
                    RoomState.reaction_tab == "geste",
                    "flex-1 rounded-lg bg-zinc-800 py-1.5 text-xs font-bold text-white",
                    "flex-1 rounded-lg py-1.5 text-xs font-bold text-zinc-500",
                ),
            ),
            class_name="mb-2 flex gap-1 rounded-xl border border-zinc-800 p-1",
        ),
        rx.el.div(
            rx.foreach(
                RoomState.reaction_choices,
                lambda choice: rx.cond(
                    choice["group"] == RoomState.reaction_tab,
                    rx.el.button(
                        rx.el.span(choice["emoji"], class_name="text-lg"),
                        rx.el.span(
                            choice["label"],
                            class_name="text-[10px] font-semibold text-zinc-400",
                        ),
                        on_click=lambda: RoomState.send_reaction(
                            choice["emoji"], choice["label"]
                        ),
                        class_name=(
                            "flex flex-col items-center gap-0.5 rounded-xl "
                            "border border-zinc-800 py-2 "
                            "hover:border-emerald-500/60"
                        ),
                    ),
                    rx.fragment(),
                ),
            ),
            class_name="grid grid-cols-4 gap-2",
        ),
        rx.cond(
            RoomState.reactions.length() > 0,
            rx.el.div(
                rx.foreach(RoomState.reactions, reaction_bubble),
                class_name="mt-3 flex flex-wrap gap-1.5",
            ),
            rx.fragment(),
        ),
    )


def room_head() -> rx.Component:
    return panel(
        rx.el.div(
            rx.el.div(
                rx.el.h1(
                    RoomState.room_name,
                    class_name="text-lg font-black tracking-tight text-white",
                ),
                rx.el.p(
                    f"{RoomState.game_name} • code {RoomState.code} • "
                    f"{RoomState.player_count}/{RoomState.max_players} joueurs",
                    class_name="text-[11px] text-zinc-500",
                ),
                class_name="min-w-0 flex-1",
            ),
            rx.el.div(
                jewel_tag(RoomState.status_label, "emerald"),
                jewel_tag(f"Pot {RoomState.pot_coins} pts", "gold"),
                jewel_tag(f"Net {RoomState.net_prize} pts", "cyan"),
                class_name="flex flex-wrap gap-1.5",
            ),
            class_name="flex flex-col gap-3 sm:flex-row sm:items-start",
        ),
        rx.el.div(
            rx.cond(
                RoomState.is_playing,
                rx.el.div(
                    rx.icon("timer", class_name="h-4 w-4 text-amber-300"),
                    rx.el.span(
                        rx.cond(
                            RoomState.seconds_left > 0,
                            f"{RoomState.seconds_left}s",
                            "Temps ecoule",
                        ),
                        class_name="text-xs font-bold text-amber-200",
                    ),
                    rx.el.span(
                        rx.cond(
                            RoomState.my_turn,
                            "A vous de jouer",
                            f"Tour de {RoomState.turn_name}",
                        ),
                        class_name="text-xs font-semibold text-zinc-400",
                    ),
                    class_name="flex items-center gap-2",
                ),
                rx.el.span(
                    "La partie n'a pas encore commence.",
                    class_name="text-xs text-zinc-500",
                ),
            ),
            rx.el.div(
                rx.cond(
                    RoomState.is_waiting,
                    rx.el.button(
                        rx.icon("check", class_name="h-4 w-4"),
                        "Pret",
                        on_click=RoomState.toggle_ready,
                        class_name=(
                            "flex items-center gap-2 rounded-xl border "
                            "border-zinc-700 px-3 py-2 text-xs font-bold "
                            "text-zinc-100 hover:border-emerald-400"
                        ),
                    ),
                    rx.fragment(),
                ),
                rx.cond(
                    RoomState.is_waiting & RoomState.is_host,
                    rx.el.button(
                        rx.icon("play", class_name="h-4 w-4"),
                        "JOUER",
                        on_click=RoomState.start_match,
                        class_name=(
                            "flex items-center gap-2 rounded-xl "
                            "bg-emerald-500 px-4 py-2 text-xs font-black "
                            "text-black hover:bg-emerald-400"
                        ),
                    ),
                    rx.fragment(),
                ),
                rx.cond(
                    RoomState.is_playing & RoomState.timer_expired,
                    rx.el.button(
                        rx.icon("fast-forward", class_name="h-4 w-4"),
                        "Avancer le tour",
                        on_click=RoomState.advance_timeout,
                        class_name=(
                            "flex items-center gap-2 rounded-xl border "
                            "border-amber-400/50 px-3 py-2 text-xs font-bold "
                            "text-amber-200 hover:bg-amber-400/10"
                        ),
                    ),
                    rx.fragment(),
                ),
                rx.el.button(
                    rx.icon("refresh-cw", class_name="h-4 w-4"),
                    on_click=RoomState.manual_refresh,
                    aria_label="Rafraichir",
                    class_name=(
                        "flex size-9 items-center justify-center rounded-xl "
                        "border border-zinc-800 text-zinc-300 "
                        "hover:border-zinc-600"
                    ),
                ),
                rx.el.button(
                    rx.icon("log-out", class_name="h-4 w-4"),
                    "Quitter",
                    on_click=RoomState.leave_room,
                    class_name=(
                        "flex items-center gap-2 rounded-xl border "
                        "border-zinc-800 px-3 py-2 text-xs font-bold "
                        "text-zinc-400 hover:border-rose-500/60 "
                        "hover:text-rose-300"
                    ),
                ),
                class_name="flex flex-wrap items-center gap-2",
            ),
            class_name=(
                "mt-3 flex flex-col gap-3 border-t border-zinc-800 pt-3 "
                "sm:flex-row sm:items-center sm:justify-between"
            ),
        ),
        rx.cond(
            RoomState.is_finished,
            rx.el.div(
                rx.icon("trophy", class_name="h-5 w-5 text-amber-300"),
                rx.el.p(
                    rx.cond(
                        RoomState.winner_name != "",
                        f"Vainqueur: {RoomState.winner_name} • "
                        f"{RoomState.net_prize} points nets, frais deduits",
                        "Partie terminee.",
                    ),
                    class_name="text-sm font-bold text-amber-200",
                ),
                class_name=(
                    "mt-3 flex items-center gap-2 rounded-xl border "
                    "border-amber-400/40 bg-amber-400/5 px-3 py-2"
                ),
            ),
            rx.fragment(),
        ),
    )


def room_body() -> rx.Component:
    return rx.el.div(
        rx.cond(
            RoomState.error != "",
            rx.el.div(
                rx.icon("triangle-alert", class_name="h-5 w-5 text-rose-400"),
                rx.el.p(
                    RoomState.error,
                    class_name="text-sm font-semibold text-rose-300",
                ),
                class_name=(
                    "flex items-center gap-2 rounded-2xl border "
                    "border-rose-500/40 bg-rose-500/5 p-4"
                ),
            ),
            rx.fragment(),
        ),
        rx.cond(
            RoomState.loaded,
            rx.el.div(
                room_head(),
                rx.el.div(
                    rx.el.div(
                        game_board(),
                        rx.cond(
                            RoomState.slug == "loto",
                            rx.el.div(loto_controls(), class_name="mt-4"),
                            rx.fragment(),
                        ),
                        class_name="min-w-0 flex-1",
                    ),
                    rx.el.div(
                        panel(
                            section_title("users", "Joueurs"),
                            rx.cond(
                                RoomState.players.length() > 0,
                                rx.el.div(
                                    rx.foreach(RoomState.players, player_tile),
                                    class_name="flex flex-col gap-2",
                                ),
                                rx.el.p(
                                    "Salle vide.",
                                    class_name="text-sm text-zinc-500",
                                ),
                            ),
                        ),
                        reaction_panel(),
                        panel(
                            section_title("activity", "Activite"),
                            rx.cond(
                                RoomState.activity.length() > 0,
                                rx.el.div(
                                    rx.foreach(
                                        RoomState.activity, activity_row
                                    ),
                                    class_name=(
                                        "flex max-h-64 flex-col "
                                        "overflow-y-auto divide-y "
                                        "divide-zinc-800/60"
                                    ),
                                ),
                                rx.el.p(
                                    "Aucune activite.",
                                    class_name="text-sm text-zinc-500",
                                ),
                            ),
                        ),
                        rx.cond(
                            RoomState.announcements.length() > 0,
                            panel(
                                section_title("megaphone", "Annonces"),
                                rx.foreach(
                                    RoomState.announcements,
                                    lambda item: rx.el.p(
                                        item,
                                        class_name=(
                                            "text-[11px] font-semibold "
                                            "text-emerald-300"
                                        ),
                                    ),
                                ),
                            ),
                            rx.fragment(),
                        ),
                        class_name="flex w-full flex-col gap-4 lg:w-80 shrink-0",
                    ),
                    class_name="mt-4 flex flex-col gap-4 lg:flex-row",
                ),
                class_name="w-full",
            ),
            rx.el.div(
                rx.el.div(
                    class_name="h-24 animate-pulse rounded-2xl bg-zinc-900"
                ),
                rx.el.div(
                    class_name="mt-4 h-72 animate-pulse rounded-2xl bg-zinc-900"
                ),
                class_name="w-full",
            ),
        ),
        domino_result_modal(),
        class_name="flex w-full flex-col gap-4",
    )


def game_room_page() -> rx.Component:
    return dark_page(RoomState.game_name, room_body(), "jeux", "/games")
