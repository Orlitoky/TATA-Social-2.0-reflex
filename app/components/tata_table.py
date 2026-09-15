"""Production dark-navy game table for the three TATA games.

Domino, Ludo and Loto share one composition: compact top bar, real player
geometry around a game specific board, a bottom action tray, a persistent
activity rail with chat / history / reactions, and a unified result overlay.
Legacy games keep their own boards untouched.
"""

from __future__ import annotations

import reflex as rx

from app.components.boards import domino_tile
from app.components.ui import avatar
from app.states.room_state import (
    ChatRow,
    HistoryRow,
    LotoCard,
    LotoCell,
    LudoCell,
    LudoZone,
    PlayerRow,
    RoomState,
    ScoreRow,
    StandingRow,
    TileRow,
)

TABLE = "rounded-2xl border border-white/10 bg-[#0B2647]"
FELT = (
    "rounded-2xl border border-white/10 "
    "bg-[radial-gradient(circle_at_50%_0%,#0E3157,#071A33_70%)]"
)
LABEL = "text-[10px] font-bold uppercase tracking-wider text-slate-400"
PILL = "w-fit rounded-full px-2.5 py-1 text-[11px] font-bold"


def tone_pill(label: str | rx.Var, tone: str = "sky") -> rx.Component:
    tones = {
        "sky": "bg-[#1E9EF5]/15 text-[#7DC5FA] ring-1 ring-[#1E9EF5]/30",
        "cyan": "bg-[#22D3EE]/15 text-[#67E8F9] ring-1 ring-[#22D3EE]/30",
        "gold": "bg-amber-400/15 text-amber-200 ring-1 ring-amber-400/30",
        "emerald": "bg-emerald-500/15 text-emerald-300 ring-1 "
        "ring-emerald-400/30",
        "rose": "bg-rose-500/15 text-rose-300 ring-1 ring-rose-400/30",
        "slate": "bg-white/5 text-slate-300 ring-1 ring-white/10",
    }
    return rx.el.span(
        label, class_name=PILL + " " + tones.get(tone, tones["sky"])
    )


def section(icon: str, title: str) -> rx.Component:
    return rx.el.div(
        rx.icon(icon, class_name="h-3.5 w-3.5 text-[#22D3EE]"),
        rx.el.h3(title, class_name=LABEL),
        class_name="mb-2 flex items-center gap-2",
    )


# ------------------------------------------------------------------- top bar
def top_bar() -> rx.Component:
    return rx.el.div(
        rx.el.div(
            rx.el.a(
                rx.icon("chevron-left", class_name="h-4 w-4 text-slate-200"),
                href="/games",
                aria_label="Retour aux jeux",
                class_name=(
                    "flex size-9 shrink-0 items-center justify-center "
                    "rounded-xl border border-white/10 bg-white/5 "
                    "hover:border-[#22D3EE]/60"
                ),
            ),
            rx.el.div(
                rx.el.p(
                    RoomState.room_name,
                    class_name=(
                        "truncate text-sm font-bold tracking-tight text-white"
                    ),
                ),
                rx.el.p(
                    f"{RoomState.game_name} • {RoomState.code} • "
                    f"{RoomState.player_count}/{RoomState.max_players}",
                    class_name="truncate text-[11px] text-slate-400",
                ),
                class_name="min-w-0 flex-1",
            ),
            rx.el.div(
                rx.el.span(
                    class_name=rx.match(
                        RoomState.connection_state,
                        (
                            "live",
                            "size-2 rounded-full bg-emerald-400 animate-pulse",
                        ),
                        ("error", "size-2 rounded-full bg-rose-500"),
                        ("removed", "size-2 rounded-full bg-rose-500"),
                        ("connecting", "size-2 rounded-full bg-amber-300"),
                        "size-2 rounded-full bg-slate-500",
                    )
                ),
                rx.el.span(
                    RoomState.connection_label,
                    class_name="text-[10px] font-bold text-slate-300",
                ),
                class_name=(
                    "hidden sm:flex items-center gap-1.5 rounded-full border "
                    "border-white/10 bg-white/5 px-2.5 py-1"
                ),
            ),
            class_name="flex items-center gap-2",
        ),
        rx.el.div(
            tone_pill(RoomState.status_label, "emerald"),
            rx.cond(
                RoomState.is_solo_test,
                tone_pill("Mode test solo", "cyan"),
                rx.fragment(),
            ),
            rx.cond(
                RoomState.is_solo_test & (RoomState.slug == "ludo"),
                tone_pill("Entrainement solo", "cyan"),
                rx.fragment(),
            ),
            rx.cond(
                RoomState.slug == "loto",
                tone_pill(RoomState.tier_label, "sky"),
                rx.fragment(),
            ),
            rx.cond(
                RoomState.slug == "domino",
                tone_pill(f"Maty {RoomState.maty_target}", "sky"),
                rx.fragment(),
            ),
            rx.cond(
                RoomState.slug == "ludo",
                tone_pill("4 pions a la maison", "sky"),
                rx.fragment(),
            ),
            class_name="mt-2 flex flex-wrap items-center gap-1.5",
        ),
        class_name=TABLE + " p-3",
    )


def turn_strip() -> rx.Component:
    return rx.el.div(
        rx.cond(
            RoomState.is_playing,
            rx.el.div(
                rx.el.div(
                    rx.icon("timer", class_name="h-4 w-4"),
                    rx.el.span(
                        RoomState.timer_label,
                        class_name="text-base font-black tabular-nums",
                    ),
                    class_name=rx.cond(
                        RoomState.urgent,
                        "flex items-center gap-1.5 rounded-xl border "
                        "border-rose-500/60 bg-rose-500/10 px-3 py-1.5 "
                        "text-rose-300 transition-colors duration-300 "
                        "animate-pulse",
                        "flex items-center gap-1.5 rounded-xl border "
                        "border-[#22D3EE]/40 bg-[#22D3EE]/10 px-3 py-1.5 "
                        "text-[#67E8F9] transition-colors duration-300",
                    ),
                ),
                rx.el.div(
                    rx.el.p(
                        rx.cond(
                            RoomState.my_turn,
                            "A vous de jouer",
                            rx.cond(
                                RoomState.slug == "loto",
                                "Tirage automatique en cours",
                                f"Tour de {RoomState.turn_name}",
                            ),
                        ),
                        class_name=rx.cond(
                            RoomState.my_turn,
                            "text-sm font-black text-emerald-300",
                            "text-sm font-bold text-white",
                        ),
                    ),
                    rx.el.p(
                        RoomState.last_note,
                        class_name="text-[11px] text-slate-400",
                    ),
                    class_name="min-w-0 flex-1",
                ),
                class_name="flex items-center gap-3",
            ),
            rx.el.p(
                "La partie n'est pas en cours.",
                class_name="text-xs font-semibold text-slate-400",
            ),
        ),
        rx.el.div(
            rx.el.button(
                rx.icon(
                    rx.cond(RoomState.audio_on, "volume-2", "volume-x"),
                    class_name="h-4 w-4",
                ),
                on_click=RoomState.toggle_audio,
                title=RoomState.audio_label,
                aria_label=RoomState.audio_label,
                class_name=rx.cond(
                    RoomState.audio_on,
                    "flex size-9 items-center justify-center rounded-xl "
                    "border border-[#22D3EE]/40 text-[#67E8F9]",
                    "flex size-9 items-center justify-center rounded-xl "
                    "border border-white/10 text-slate-500",
                ),
            ),
            rx.el.button(
                rx.icon("history", class_name="h-4 w-4"),
                on_click=RoomState.toggle_history,
                title="Historique des actions",
                aria_label="Historique des actions",
                class_name=(
                    "flex size-9 items-center justify-center rounded-xl "
                    "border border-white/10 text-slate-300 "
                    "hover:border-[#1E9EF5]/60"
                ),
            ),
            rx.el.button(
                rx.icon("refresh-cw", class_name="h-4 w-4"),
                on_click=RoomState.manual_refresh,
                aria_label="Rafraichir",
                class_name=(
                    "flex size-9 items-center justify-center rounded-xl "
                    "border border-white/10 text-slate-300 "
                    "hover:border-[#1E9EF5]/60"
                ),
            ),
            rx.el.button(
                rx.icon("log-out", class_name="h-4 w-4"),
                on_click=RoomState.leave_room,
                aria_label="Quitter la salle",
                class_name=(
                    "flex size-9 items-center justify-center rounded-xl "
                    "border border-white/10 text-slate-400 "
                    "hover:border-rose-500/60 hover:text-rose-300"
                ),
            ),
            class_name="flex items-center gap-1.5",
        ),
        class_name=(
            TABLE + " mt-3 flex flex-col gap-3 p-3 sm:flex-row "
            "sm:items-center sm:justify-between"
        ),
    )


# ------------------------------------------------------------ player geometry
def seat_chip(player: PlayerRow) -> rx.Component:
    return rx.el.div(
        rx.el.div(
            avatar(player["avatar_url"], player["avatar_remote"], "size-10"),
            rx.cond(
                player["is_online"],
                rx.el.span(
                    class_name=(
                        "absolute -bottom-0.5 -right-0.5 size-3 rounded-full "
                        "border-2 border-[#0B2647] bg-emerald-400"
                    )
                ),
                rx.el.span(
                    class_name=(
                        "absolute -bottom-0.5 -right-0.5 size-3 rounded-full "
                        "border-2 border-[#0B2647] bg-slate-500"
                    )
                ),
            ),
            class_name=rx.cond(
                player["is_turn"],
                "relative shrink-0 rounded-full ring-2 ring-emerald-400 "
                "ring-offset-2 ring-offset-[#0B2647] transition-all "
                "duration-300",
                "relative shrink-0 rounded-full transition-all duration-300",
            ),
        ),
        rx.el.div(
            rx.el.p(
                player["name"],
                class_name="truncate text-[11px] font-bold text-white",
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
                    player["is_bot"],
                    rx.el.span(
                        "Bot",
                        class_name="text-[10px] font-bold text-[#67E8F9]",
                    ),
                    rx.fragment(),
                ),
                rx.cond(
                    ~player["is_online"] & ~player["is_bot"],
                    rx.el.span(
                        "Deconnecte",
                        class_name="text-[10px] font-bold text-rose-300",
                    ),
                    rx.fragment(),
                ),
                rx.match(
                    RoomState.slug,
                    (
                        "loto",
                        rx.el.span(
                            f"{player['cards']} carton(s)",
                            class_name=("text-[10px] font-bold text-[#7DC5FA]"),
                        ),
                    ),
                    (
                        "ludo",
                        rx.el.span(
                            f"{player['home_pawns']}/4 maison",
                            class_name=("text-[10px] font-bold text-[#7DC5FA]"),
                        ),
                    ),
                    rx.el.span(
                        f"{player['hand_count']} tuile(s) • "
                        f"{player['score']} score",
                        class_name="text-[10px] font-bold text-[#7DC5FA]",
                    ),
                ),
                class_name="flex flex-wrap items-center gap-x-2",
            ),
            class_name="min-w-0 flex-1",
        ),
        class_name=rx.cond(
            player["is_turn"],
            "flex min-w-0 items-center gap-2 rounded-xl border "
            "border-emerald-400/50 bg-emerald-400/5 p-2 transition-colors "
            "duration-300",
            "flex min-w-0 items-center gap-2 rounded-xl border "
            "border-white/10 bg-white/5 p-2 transition-colors duration-300",
        ),
    )


def opponents_row() -> rx.Component:
    return rx.el.div(
        rx.foreach(
            RoomState.players,
            lambda player: rx.cond(
                player["is_me"], rx.fragment(), seat_chip(player)
            ),
        ),
        class_name=(
            "grid grid-cols-1 gap-2 sm:grid-cols-2 lg:grid-cols-3 w-full"
        ),
    )


def my_seat() -> rx.Component:
    return rx.el.div(
        rx.foreach(
            RoomState.players,
            lambda player: rx.cond(
                player["is_me"], seat_chip(player), rx.fragment()
            ),
        ),
        class_name="grid w-full grid-cols-1 gap-2 sm:max-w-sm",
    )


# ---------------------------------------------------------------- DOMINO view
def domino_hand_tile(tile: TileRow) -> rx.Component:
    return rx.el.div(
        domino_tile(tile),
        rx.cond(
            RoomState.domino_is_rush_auto,
            rx.el.button(
                "AUTO",
                on_click=lambda: RoomState.domino_auto_play(tile["index"]),
                disabled=~(RoomState.my_turn & tile["playable"]),
                aria_label="Poser automatiquement",
                class_name=(
                    "mt-1 w-[38px] rounded-md bg-[#1E9EF5] py-1 text-[9px] "
                    "font-black text-[#04121F] hover:bg-[#22D3EE] "
                    "disabled:cursor-not-allowed disabled:opacity-30"
                ),
            ),
            rx.el.div(
                rx.el.button(
                    "G",
                    on_click=lambda: RoomState.domino_play(
                        tile["index"], "left"
                    ),
                    disabled=~(RoomState.my_turn & tile["can_left"]),
                    aria_label="Poser a gauche",
                    class_name=rx.cond(
                        RoomState.my_turn & tile["can_left"],
                        "flex-1 rounded-l-md bg-emerald-500 py-1 text-[10px] "
                        "font-black text-[#04121F] hover:bg-emerald-400",
                        "flex-1 rounded-l-md bg-white/5 py-1 text-[10px] "
                        "font-bold text-slate-500 cursor-not-allowed",
                    ),
                ),
                rx.el.button(
                    "D",
                    on_click=lambda: RoomState.domino_play(
                        tile["index"], "right"
                    ),
                    disabled=~(RoomState.my_turn & tile["can_right"]),
                    aria_label="Poser a droite",
                    class_name=rx.cond(
                        RoomState.my_turn & tile["can_right"],
                        "flex-1 rounded-r-md bg-emerald-500 py-1 text-[10px] "
                        "font-black text-[#04121F] hover:bg-emerald-400",
                        "flex-1 rounded-r-md bg-white/5 py-1 text-[10px] "
                        "font-bold text-slate-500 cursor-not-allowed",
                    ),
                ),
                class_name="mt-1 flex w-[38px] gap-px",
            ),
        ),
        class_name=rx.cond(
            tile["playable"],
            "tata-pop flex flex-col items-center rounded-lg p-0.5 ring-2 "
            "ring-emerald-400/70 transition-transform duration-200 "
            "hover:-translate-y-1",
            "tata-pop flex flex-col items-center rounded-lg p-0.5 opacity-45 "
            "transition-opacity duration-200",
        ),
    )


def score_line(row: ScoreRow) -> rx.Component:
    return rx.el.div(
        rx.el.span(
            row["name"],
            class_name="truncate text-[11px] font-semibold text-slate-200",
        ),
        rx.el.span(
            row["score"],
            class_name="text-sm font-black text-amber-300 tabular-nums",
        ),
        class_name="flex items-center justify-between gap-2 py-1",
    )


def domino_board() -> rx.Component:
    return rx.el.div(
        rx.el.div(
            tone_pill(RoomState.domino_mode_name, "sky"),
            tone_pill(f"Pioche {RoomState.boneyard_count}", "cyan"),
            tone_pill(RoomState.domino_variants, "slate"),
            tone_pill("7 tuiles par joueur", "emerald"),
            rx.cond(
                RoomState.domino_bot_count > 0,
                tone_pill(f"{RoomState.domino_bot_count} bot(s)", "cyan"),
                rx.fragment(),
            ),
            class_name="mb-3 flex flex-wrap gap-1.5",
        ),
        rx.el.div(
            rx.el.div(
                rx.el.span(
                    rx.cond(RoomState.left_end < 0, "-", RoomState.left_end),
                    class_name=(
                        "flex size-9 items-center justify-center rounded-lg "
                        "border border-emerald-400/60 bg-emerald-400/10 "
                        "text-sm font-black text-emerald-300"
                    ),
                ),
                rx.el.span("Gauche", class_name=LABEL),
                class_name="flex shrink-0 flex-col items-center gap-1",
            ),
            rx.el.div(
                rx.cond(
                    RoomState.chain.length() > 0,
                    rx.el.div(
                        rx.foreach(RoomState.chain, domino_tile),
                        class_name=(
                            "flex flex-wrap content-start items-center "
                            "justify-center gap-1.5"
                        ),
                    ),
                    rx.el.p(
                        "Chaine vide: la plus forte tuile ouvre la manche.",
                        class_name="text-xs font-semibold text-slate-400",
                    ),
                ),
                class_name=(
                    "flex min-h-44 flex-1 items-center justify-center p-2"
                ),
            ),
            rx.el.div(
                rx.el.span(
                    rx.cond(RoomState.right_end < 0, "-", RoomState.right_end),
                    class_name=(
                        "flex size-9 items-center justify-center rounded-lg "
                        "border border-emerald-400/60 bg-emerald-400/10 "
                        "text-sm font-black text-emerald-300"
                    ),
                ),
                rx.el.span("Droite", class_name=LABEL),
                class_name="flex shrink-0 flex-col items-center gap-1",
            ),
            class_name=FELT + " flex w-full items-center gap-2 p-3",
        ),
        rx.el.div(
            section("trophy", "Scores et manches"),
            rx.el.p(
                f"Manche {RoomState.round_number} • objectif Maty "
                f"{RoomState.maty_target}",
                class_name="mb-1 text-[11px] font-semibold text-[#7DC5FA]",
            ),
            rx.cond(
                RoomState.scores.length() > 0,
                rx.el.div(
                    rx.foreach(RoomState.scores, score_line),
                    class_name="flex flex-col divide-y divide-white/5",
                ),
                rx.el.p(
                    "Scores a zero.",
                    class_name="text-xs text-slate-500",
                ),
            ),
            class_name=TABLE + " mt-3 p-3",
        ),
        class_name="w-full",
    )


def domino_tray() -> rx.Component:
    return rx.el.div(
        rx.el.div(
            section("hand", "Ma main"),
            rx.cond(
                RoomState.my_tiles.length() > 0,
                rx.el.div(
                    rx.foreach(RoomState.my_tiles, domino_hand_tile),
                    class_name="flex flex-wrap items-end gap-2",
                ),
                rx.el.p("Main vide.", class_name="text-xs text-slate-500"),
            ),
            class_name="min-w-0 flex-1",
        ),
        rx.el.div(
            rx.el.button(
                rx.icon("download", class_name="h-4 w-4"),
                "Piocher",
                on_click=RoomState.domino_draw,
                disabled=~RoomState.domino_can_draw,
                class_name=(
                    "flex items-center justify-center gap-2 rounded-xl "
                    "bg-[#1E9EF5] px-4 py-2.5 text-xs font-black "
                    "text-[#04121F] hover:bg-[#22D3EE] "
                    "disabled:cursor-not-allowed disabled:bg-white/5 "
                    "disabled:text-slate-500"
                ),
            ),
            rx.el.button(
                rx.icon("skip-forward", class_name="h-4 w-4"),
                "Passer",
                on_click=RoomState.domino_pass,
                disabled=~RoomState.domino_can_pass,
                class_name=(
                    "flex items-center justify-center gap-2 rounded-xl "
                    "border border-white/15 px-4 py-2.5 text-xs font-black "
                    "text-slate-200 hover:border-emerald-400 "
                    "disabled:cursor-not-allowed disabled:opacity-30"
                ),
            ),
            rx.el.p(
                "Passer n'est possible qu'avec pioche vide et aucune pose "
                "legale.",
                class_name="text-[10px] leading-relaxed text-slate-500",
            ),
            class_name="flex w-full flex-col gap-2 sm:w-44 shrink-0",
        ),
        class_name=TABLE + " flex flex-col gap-3 p-3 sm:flex-row",
    )


# ------------------------------------------------------------------ LUDO view
def ludo_pawn(color: rx.Var) -> rx.Component:
    return rx.el.span(
        class_name=rx.match(
            color,
            (
                "red",
                "tata-pop size-[70%] rounded-full bg-rose-500 ring-2 "
                "ring-white/80",
            ),
            (
                "green",
                "tata-pop size-[70%] rounded-full bg-emerald-500 ring-2 "
                "ring-white/80",
            ),
            (
                "yellow",
                "tata-pop size-[70%] rounded-full bg-amber-400 ring-2 "
                "ring-white/80",
            ),
            (
                "blue",
                "tata-pop size-[70%] rounded-full bg-[#1E9EF5] ring-2 "
                "ring-white/80",
            ),
            "size-[70%] rounded-full bg-slate-400",
        )
    )


def ludo_cell(cell: LudoCell) -> rx.Component:
    return rx.el.div(
        rx.cond(cell["pawn"] != "", ludo_pawn(cell["pawn"]), rx.fragment()),
        rx.cond(
            cell["safe"] & (cell["pawn"] == ""),
            rx.icon("star", class_name="h-2.5 w-2.5 text-amber-500"),
            rx.fragment(),
        ),
        class_name=rx.match(
            cell["kind"],
            (
                "home",
                rx.match(
                    cell["color"],
                    (
                        "red",
                        "flex aspect-square items-center justify-center "
                        "bg-rose-500/25",
                    ),
                    (
                        "green",
                        "flex aspect-square items-center justify-center "
                        "bg-emerald-500/25",
                    ),
                    (
                        "yellow",
                        "flex aspect-square items-center "
                        "justify-center bg-amber-400/25",
                    ),
                    "flex aspect-square items-center justify-center "
                    "bg-[#1E9EF5]/25",
                ),
            ),
            (
                "lane",
                rx.match(
                    cell["color"],
                    (
                        "red",
                        "flex aspect-square items-center justify-center "
                        "bg-rose-500/70",
                    ),
                    (
                        "green",
                        "flex aspect-square items-center "
                        "justify-center bg-emerald-500/70",
                    ),
                    (
                        "yellow",
                        "flex aspect-square items-center "
                        "justify-center bg-amber-400/70",
                    ),
                    "flex aspect-square items-center justify-center "
                    "bg-[#1E9EF5]/70",
                ),
            ),
            (
                "center",
                "flex aspect-square items-center justify-center "
                "bg-amber-300/80",
            ),
            (
                "path",
                "flex aspect-square items-center justify-center border "
                "border-[#0B2647]/40 bg-white",
            ),
            "aspect-square bg-[#071A33]",
        ),
    )


def ludo_zone(zone: LudoZone) -> rx.Component:
    return rx.el.div(
        rx.el.p(
            zone["name"],
            class_name="truncate text-[10px] font-black text-white",
        ),
        rx.el.div(
            rx.el.span(
                f"Base {zone['base']}",
                class_name="text-[9px] font-bold text-slate-300",
            ),
            rx.el.span(
                f"Maison {zone['home']}/4",
                class_name="text-[9px] font-bold text-emerald-300",
            ),
            class_name="flex items-center gap-1.5",
        ),
        class_name=rx.cond(
            zone["is_turn"],
            "min-w-0 rounded-lg border border-emerald-400/70 "
            "bg-[#071A33]/90 px-2 py-1 transition-colors duration-300",
            "min-w-0 rounded-lg border border-white/10 bg-[#071A33]/90 "
            "px-2 py-1 transition-colors duration-300",
        ),
    )


def ludo_board() -> rx.Component:
    return rx.el.div(
        rx.el.div(
            tone_pill("Quatre pions par joueur", "sky"),
            tone_pill(f"De {RoomState.dice_value}", "cyan"),
            tone_pill(f"{RoomState.my_home_pawns}/4 a la maison", "emerald"),
            class_name="mb-3 flex flex-wrap gap-1.5",
        ),
        rx.el.div(
            rx.el.div(
                rx.foreach(
                    RoomState.ludo_rows,
                    lambda row: rx.el.div(
                        rx.foreach(row, ludo_cell),
                        class_name="grid",
                        style={
                            "gridTemplateColumns": "repeat(15, minmax(0, 1fr))"
                        },
                    ),
                ),
                class_name=(
                    "aspect-square w-full overflow-hidden rounded-xl "
                    "border-4 border-white/15 bg-[#071A33]"
                ),
            ),
            rx.el.div(
                rx.foreach(RoomState.ludo_zones, ludo_zone),
                class_name="mt-2 grid grid-cols-2 gap-2",
            ),
            class_name=(
                FELT + " mx-auto w-full max-w-[560px] min-w-[280px] p-3"
            ),
        ),
        class_name="w-full",
    )


def ludo_tray() -> rx.Component:
    return rx.el.div(
        rx.el.div(
            rx.el.div(
                rx.cond(RoomState.dice_value > 0, RoomState.dice_value, "?"),
                class_name=rx.cond(
                    RoomState.dice_rolled,
                    "flex size-16 items-center justify-center rounded-2xl "
                    "bg-white text-3xl font-black text-[#071A33] "
                    "transition-transform duration-300 scale-105",
                    "flex size-16 items-center justify-center rounded-2xl "
                    "bg-white text-3xl font-black text-[#071A33] "
                    "transition-transform duration-300",
                ),
            ),
            rx.el.div(
                rx.el.button(
                    rx.icon("dices", class_name="h-4 w-4"),
                    "Lancer le de",
                    on_click=RoomState.ludo_roll,
                    disabled=~(RoomState.my_turn & ~RoomState.dice_rolled),
                    class_name=(
                        "flex items-center gap-2 rounded-xl bg-[#1E9EF5] "
                        "px-4 py-2.5 text-xs font-black text-[#04121F] "
                        "hover:bg-[#22D3EE] disabled:cursor-not-allowed "
                        "disabled:bg-white/5 disabled:text-slate-500"
                    ),
                ),
                rx.cond(
                    RoomState.legal_pawns.length() > 0,
                    rx.el.div(
                        rx.foreach(
                            RoomState.legal_pawns,
                            lambda index: rx.el.button(
                                f"Pion {index + 1}",
                                on_click=lambda: RoomState.ludo_move(index),
                                disabled=~RoomState.my_turn,
                                class_name=(
                                    "rounded-xl border border-emerald-400/70 "
                                    "bg-emerald-400/10 px-3 py-2 text-[11px] "
                                    "font-black text-emerald-300 "
                                    "hover:bg-emerald-400/20 "
                                    "disabled:opacity-30"
                                ),
                            ),
                        ),
                        class_name="mt-2 flex flex-wrap gap-2",
                    ),
                    rx.el.p(
                        "Aucun pion jouable: le tour avance automatiquement.",
                        class_name="mt-2 text-[10px] text-slate-500",
                    ),
                ),
                class_name="min-w-0 flex-1",
            ),
            class_name="flex items-start gap-3",
        ),
        class_name=TABLE + " p-3",
    )


# ------------------------------------------------------------------ LOTO view
def loto_cell(cell: LotoCell) -> rx.Component:
    return rx.cond(
        cell["value"] == 0,
        rx.el.div(class_name="h-8 rounded-md bg-white/5"),
        rx.cond(
            cell["marked"],
            rx.el.div(
                cell["value"],
                class_name=(
                    "tata-pop flex h-8 items-center justify-center rounded-md "
                    "bg-emerald-500 text-xs font-black text-[#04121F] "
                    "transition-colors duration-300"
                ),
            ),
            rx.el.div(
                cell["value"],
                class_name=(
                    "flex h-8 items-center justify-center rounded-md border "
                    "border-white/15 bg-white text-xs font-bold "
                    "text-[#071A33] transition-colors duration-300"
                ),
            ),
        ),
    )


def loto_ticket(card: LotoCard) -> rx.Component:
    return rx.el.div(
        rx.el.div(
            rx.el.span(
                f"Carton #{card['card_index']}",
                class_name="text-[11px] font-black text-white",
            ),
            rx.el.span(
                f"{card['marked']}/15",
                class_name="text-[11px] font-black text-emerald-300",
            ),
            class_name="mb-2 flex items-center justify-between",
        ),
        rx.el.div(
            rx.foreach(
                card["rows"],
                lambda row: rx.el.div(
                    rx.foreach(row, loto_cell),
                    class_name="grid grid-cols-9 gap-1",
                ),
            ),
            class_name="flex flex-col gap-1",
        ),
        rx.cond(
            card["remaining"] <= 3,
            rx.el.p(
                f"Proche: {card['remaining']} numero(s) restant(s)",
                class_name="mt-2 text-[10px] font-black text-rose-300",
            ),
            rx.el.p(
                f"{card['remaining']} numero(s) restant(s)",
                class_name="mt-2 text-[10px] font-semibold text-slate-400",
            ),
        ),
        class_name=(
            "rounded-xl border border-white/10 bg-[#071A33] p-2.5 "
            "transition-colors duration-300"
        ),
    )


def loto_board() -> rx.Component:
    return rx.el.div(
        rx.el.div(
            rx.el.div(
                rx.el.p("Boule en cours", class_name=LABEL),
                rx.el.p(
                    rx.cond(
                        RoomState.last_number > 0, RoomState.last_number, "-"
                    ),
                    class_name=(
                        "tata-pop text-6xl font-black leading-none "
                        "text-amber-300"
                    ),
                ),
                rx.el.p(
                    f"{RoomState.drawn_count}/90 tirees",
                    class_name="text-[11px] font-bold text-slate-400",
                ),
                class_name="shrink-0 text-center",
            ),
            rx.el.div(
                rx.el.p("Derniers tirages", class_name=LABEL),
                rx.el.div(
                    rx.foreach(
                        RoomState.drawn,
                        lambda number: rx.el.span(
                            number,
                            class_name=(
                                "flex size-8 shrink-0 items-center "
                                "justify-center rounded-full border "
                                "border-amber-400/30 bg-[#071A33] text-[11px] "
                                "font-black text-amber-200"
                            ),
                        ),
                    ),
                    class_name=(
                        "mt-1 flex max-h-28 flex-wrap gap-1.5 overflow-y-auto"
                    ),
                ),
                class_name="min-w-0 flex-1",
            ),
            class_name=FELT + " flex flex-col gap-3 p-4 sm:flex-row",
        ),
        rx.el.div(
            tone_pill(RoomState.tier_label, "gold"),
            class_name="mt-3 flex flex-wrap gap-1.5",
        ),
        rx.el.div(
            section("ticket", "Mes cartons"),
            rx.cond(
                RoomState.my_cards.length() > 0,
                rx.el.div(
                    rx.foreach(RoomState.my_cards, loto_ticket),
                    class_name="grid gap-2 sm:grid-cols-2",
                ),
                rx.el.p(
                    "Aucun carton: prenez de 1 a 5 cartons avant le tirage.",
                    class_name="text-xs text-slate-500",
                ),
            ),
            class_name=TABLE + " mt-3 p-3",
        ),
        class_name="w-full",
    )


def loto_tray() -> rx.Component:
    return rx.el.div(
        rx.el.div(
            rx.el.label(
                "Cartons (1 a 5)",
                html_for="buy_count",
                class_name=LABEL,
            ),
            rx.el.input(
                id="buy_count",
                type="number",
                min=1,
                max=5,
                default_value=RoomState.buy_count.to_string(),
                on_change=RoomState.set_buy_count.debounce(300),
                class_name=(
                    "mt-1 w-full rounded-xl border border-white/15 "
                    "bg-[#071A33] px-3 py-2 text-sm font-bold text-white "
                    "outline-hidden focus:border-[#22D3EE]"
                ),
            ),
            rx.el.button(
                rx.icon("plus", class_name="h-4 w-4"),
                "Ajouter",
                on_click=RoomState.buy_cards,
                disabled=~RoomState.is_waiting,
                class_name=(
                    "mt-2 flex w-full items-center justify-center gap-2 "
                    "rounded-xl bg-emerald-500 py-2.5 text-xs font-black "
                    "text-[#04121F] hover:bg-emerald-400 "
                    "disabled:cursor-not-allowed disabled:bg-white/5 "
                    "disabled:text-slate-500"
                ),
            ),
            class_name="min-w-0 flex-1",
        ),
        rx.el.div(
            rx.el.p(
                "Le tirage avance automatiquement a chaque expiration du "
                "minuteur, sans bouton obligatoire.",
                class_name="text-[10px] leading-relaxed text-slate-400",
            ),
            rx.cond(
                RoomState.is_host,
                rx.el.button(
                    rx.icon("fast-forward", class_name="h-4 w-4"),
                    "Forcer la boule suivante",
                    on_click=RoomState.draw_number,
                    disabled=~RoomState.is_playing,
                    class_name=(
                        "mt-2 flex w-full items-center justify-center gap-2 "
                        "rounded-xl border border-amber-400/40 py-2.5 "
                        "text-[11px] font-black text-amber-200 "
                        "hover:bg-amber-400/10 disabled:opacity-30"
                    ),
                ),
                rx.fragment(),
            ),
            class_name="w-full sm:w-56 shrink-0",
        ),
        class_name=TABLE + " flex flex-col gap-3 p-3 sm:flex-row",
    )


# --------------------------------------------------------------- board router
def tata_board() -> rx.Component:
    return rx.match(
        RoomState.slug,
        ("domino", domino_board()),
        ("ludo", ludo_board()),
        ("loto", loto_board()),
        rx.fragment(),
    )


def tata_tray() -> rx.Component:
    return rx.match(
        RoomState.slug,
        ("domino", domino_tray()),
        ("ludo", ludo_tray()),
        ("loto", loto_tray()),
        rx.fragment(),
    )


# ----------------------------------------------------------------- rail tools
def chat_line(row: ChatRow) -> rx.Component:
    return rx.el.div(
        rx.el.div(
            rx.el.span(
                row["name"],
                class_name=rx.cond(
                    row["is_me"],
                    "text-[10px] font-black text-emerald-300",
                    "text-[10px] font-black text-[#7DC5FA]",
                ),
            ),
            rx.el.span(
                row["time_label"],
                class_name="font-mono text-[9px] text-slate-500",
            ),
            class_name="flex items-center gap-1.5",
        ),
        rx.el.p(
            row["text"],
            class_name="break-words text-[11px] text-slate-200",
        ),
        class_name="py-1",
    )


def chat_panel() -> rx.Component:
    return rx.el.div(
        section("message-circle", "Chat de la salle"),
        rx.cond(
            RoomState.chat_messages.length() > 0,
            rx.el.div(
                rx.foreach(RoomState.chat_messages, chat_line),
                class_name=(
                    "flex max-h-48 flex-col divide-y divide-white/5 "
                    "overflow-y-auto"
                ),
            ),
            rx.el.p(
                "Aucun message pour l'instant.",
                class_name="text-[11px] text-slate-500",
            ),
        ),
        rx.el.form(
            rx.el.input(
                name="message",
                placeholder="Message (240 caracteres max)",
                max_length=240,
                aria_label="Message de la salle",
                class_name=(
                    "min-w-0 flex-1 rounded-xl border border-white/15 "
                    "bg-[#071A33] px-3 py-2 text-[11px] text-white "
                    "outline-hidden focus:border-[#22D3EE]"
                ),
            ),
            rx.el.button(
                rx.icon("send", class_name="h-4 w-4"),
                type="submit",
                aria_label="Envoyer le message",
                class_name=(
                    "flex size-9 shrink-0 items-center justify-center "
                    "rounded-xl bg-[#1E9EF5] text-[#04121F] "
                    "hover:bg-[#22D3EE]"
                ),
            ),
            on_submit=RoomState.send_chat,
            reset_on_submit=True,
            class_name="mt-2 flex items-center gap-2",
        ),
        class_name=TABLE + " p-3",
    )


def reactions_panel() -> rx.Component:
    return rx.el.div(
        section("smile", "Reactions"),
        rx.el.div(
            rx.foreach(
                RoomState.reaction_choices,
                lambda choice: rx.el.button(
                    rx.el.span(choice["emoji"], class_name="text-lg"),
                    on_click=lambda: RoomState.send_reaction(
                        choice["emoji"], choice["label"]
                    ),
                    title=choice["label"],
                    aria_label=choice["label"],
                    class_name=(
                        "flex items-center justify-center rounded-xl border "
                        "border-white/10 py-1.5 hover:border-emerald-400/60"
                    ),
                ),
            ),
            class_name="grid grid-cols-4 gap-1.5",
        ),
        rx.cond(
            RoomState.reactions.length() > 0,
            rx.el.div(
                rx.foreach(
                    RoomState.reactions,
                    lambda row: rx.el.span(
                        f"{row['emoji']} {row['name']}",
                        class_name=(
                            "w-fit rounded-full border border-white/10 "
                            "bg-white/5 px-2 py-0.5 text-[10px] "
                            "font-semibold text-slate-300"
                        ),
                    ),
                ),
                class_name="mt-2 flex flex-wrap gap-1",
            ),
            rx.fragment(),
        ),
        class_name=TABLE + " p-3",
    )


def activity_panel() -> rx.Component:
    return rx.el.div(
        section("activity", "Activite"),
        rx.cond(
            RoomState.activity.length() > 0,
            rx.el.div(
                rx.foreach(
                    RoomState.activity,
                    lambda row: rx.el.div(
                        rx.el.span(
                            row["time_label"],
                            class_name=(
                                "shrink-0 font-mono text-[9px] text-slate-500"
                            ),
                        ),
                        rx.el.span(
                            row["text"],
                            class_name="text-[11px] text-slate-300",
                        ),
                        class_name="flex items-start gap-2 py-1",
                    ),
                ),
                class_name=(
                    "flex max-h-52 flex-col divide-y divide-white/5 "
                    "overflow-y-auto"
                ),
            ),
            rx.el.p(
                "Aucune activite.",
                class_name="text-[11px] text-slate-500",
            ),
        ),
        rx.cond(
            RoomState.announcements.length() > 0,
            rx.el.div(
                rx.foreach(
                    RoomState.announcements,
                    lambda item: rx.el.p(
                        item,
                        class_name=("text-[10px] font-black text-emerald-300"),
                    ),
                ),
                class_name=(
                    "mt-2 flex flex-col gap-0.5 border-t border-white/5 pt-2"
                ),
            ),
            rx.fragment(),
        ),
        class_name=TABLE + " p-3",
    )


def history_row(row: HistoryRow) -> rx.Component:
    return rx.el.div(
        rx.el.span(
            row["sequence"],
            class_name=(
                "w-8 shrink-0 font-mono text-[10px] font-bold text-slate-500"
            ),
        ),
        rx.el.div(
            rx.el.div(
                rx.el.span(
                    row["kind_label"],
                    class_name="text-[10px] font-black text-[#67E8F9]",
                ),
                rx.el.span(
                    row["actor"],
                    class_name="text-[10px] font-bold text-white",
                ),
                rx.el.span(
                    f"M{row['round_number']}",
                    class_name="text-[9px] font-bold text-slate-500",
                ),
                rx.el.span(
                    row["time_label"],
                    class_name="font-mono text-[9px] text-slate-500",
                ),
                class_name="flex flex-wrap items-center gap-1.5",
            ),
            rx.el.p(
                row["summary"],
                class_name="text-[11px] text-slate-300",
            ),
            class_name="min-w-0 flex-1",
        ),
        class_name="flex items-start gap-2 py-1",
    )


def history_panel() -> rx.Component:
    return rx.cond(
        RoomState.history_open,
        rx.el.div(
            rx.el.div(
                section("scroll-text", "Historique complet"),
                rx.el.button(
                    rx.icon("x", class_name="h-4 w-4"),
                    on_click=RoomState.toggle_history,
                    aria_label="Fermer l'historique",
                    class_name="text-slate-500 hover:text-white",
                ),
                class_name="flex items-start justify-between",
            ),
            rx.el.p(
                "Journal chronologique persiste (game_action). Les mains "
                "cachees ne sont jamais revelees.",
                class_name="mb-2 text-[10px] text-slate-500",
            ),
            rx.cond(
                RoomState.history_rows.length() > 0,
                rx.el.div(
                    rx.foreach(RoomState.history_rows, history_row),
                    class_name=(
                        "flex max-h-80 flex-col divide-y divide-white/5 "
                        "overflow-y-auto"
                    ),
                ),
                rx.el.p(
                    "Aucune action enregistree.",
                    class_name="text-[11px] text-slate-500",
                ),
            ),
            class_name=TABLE + " p-3",
        ),
        rx.fragment(),
    )


def tools_rail() -> rx.Component:
    return rx.el.div(
        rx.el.div(
            section("users", "Joueurs"),
            rx.cond(
                RoomState.players.length() > 0,
                rx.el.div(
                    rx.foreach(RoomState.players, seat_chip),
                    class_name="flex flex-col gap-2",
                ),
                rx.el.p("Salle vide.", class_name="text-[11px] text-slate-500"),
            ),
            class_name=TABLE + " p-3",
        ),
        chat_panel(),
        reactions_panel(),
        activity_panel(),
        history_panel(),
        class_name="flex w-full flex-col gap-3 lg:w-80 shrink-0",
    )


# -------------------------------------------------------------- round + result
def round_banner() -> rx.Component:
    return rx.cond(
        RoomState.round_result_open & ~RoomState.is_finished,
        rx.el.div(
            rx.icon("flag", class_name="h-4 w-4 text-amber-300"),
            rx.el.div(
                rx.el.p(
                    "Fin de manche",
                    class_name="text-[11px] font-black text-amber-200",
                ),
                rx.el.p(
                    RoomState.round_result_text,
                    class_name="text-[11px] text-slate-300",
                ),
                class_name="min-w-0 flex-1",
            ),
            rx.el.button(
                "Continuer",
                on_click=RoomState.close_round_result,
                class_name=(
                    "shrink-0 rounded-lg bg-emerald-500 px-3 py-1.5 "
                    "text-[11px] font-black text-[#04121F] "
                    "hover:bg-emerald-400"
                ),
            ),
            class_name=(
                "tata-rise mt-3 flex items-center gap-2 rounded-xl border "
                "border-amber-400/40 bg-amber-400/5 p-3"
            ),
        ),
        rx.fragment(),
    )


def standing_row(row: StandingRow) -> rx.Component:
    return rx.el.div(
        avatar(row["avatar_url"], row["avatar_remote"], "size-8"),
        rx.el.div(
            rx.el.p(
                row["name"],
                class_name="truncate text-[11px] font-black text-white",
            ),
            rx.el.p(
                row["detail"],
                class_name="text-[10px] font-semibold text-slate-400",
            ),
            class_name="min-w-0 flex-1",
        ),
        rx.cond(
            row["is_winner"],
            rx.el.span(
                "Gagnant",
                class_name=(
                    "w-fit rounded-full bg-amber-400/15 px-2 py-0.5 "
                    "text-[10px] font-black text-amber-200"
                ),
            ),
            rx.el.span(
                "Termine",
                class_name=(
                    "w-fit rounded-full bg-white/5 px-2 py-0.5 text-[10px] "
                    "font-bold text-slate-400"
                ),
            ),
        ),
        class_name=rx.cond(
            row["is_me"],
            "flex items-center gap-2 rounded-xl border border-[#22D3EE]/40 "
            "bg-[#22D3EE]/5 p-2",
            "flex items-center gap-2 rounded-xl border border-white/10 p-2",
        ),
    )


def result_overlay() -> rx.Component:
    return rx.cond(
        RoomState.show_result,
        rx.el.div(
            rx.el.div(
                rx.el.div(
                    rx.cond(
                        RoomState.winner_avatar != "",
                        avatar(
                            RoomState.winner_avatar,
                            RoomState.winner_avatar_remote,
                            "size-14",
                        ),
                        rx.el.div(
                            rx.icon(
                                "trophy",
                                class_name="h-6 w-6 text-amber-300",
                            ),
                            class_name=(
                                "flex size-14 items-center justify-center "
                                "rounded-full border border-amber-400/40"
                            ),
                        ),
                    ),
                    rx.el.div(
                        rx.el.p(
                            RoomState.result_headline,
                            class_name=rx.cond(
                                RoomState.i_won,
                                "text-xl font-black text-amber-300",
                                "text-xl font-black text-white",
                            ),
                        ),
                        rx.el.p(
                            rx.cond(
                                RoomState.winner_name != "",
                                f"Vainqueur: {RoomState.winner_name}",
                                "Aucun vainqueur enregistre.",
                            ),
                            class_name="text-[11px] font-bold text-slate-300",
                        ),
                        rx.el.p(
                            RoomState.result_detail,
                            class_name="text-[11px] text-slate-400",
                        ),
                        rx.cond(
                            RoomState.is_solo_test,
                            rx.el.span(
                                "Mode test solo • SOLO",
                                class_name=(
                                    "mt-1 inline-block w-fit rounded-md "
                                    "border border-[#22D3EE]/50 "
                                    "bg-[#22D3EE]/10 px-2 py-0.5 "
                                    "text-[10px] font-bold text-[#67E8F9]"
                                ),
                            ),
                            rx.fragment(),
                        ),
                        class_name="min-w-0 flex-1",
                    ),
                    rx.el.button(
                        rx.icon("x", class_name="h-4 w-4"),
                        on_click=RoomState.dismiss_result,
                        aria_label="Fermer",
                        class_name="text-slate-500 hover:text-white",
                    ),
                    class_name="flex items-start gap-3",
                ),
                rx.el.div(
                    rx.foreach(RoomState.standings, standing_row),
                    class_name=(
                        "mt-3 flex max-h-56 flex-col gap-2 overflow-y-auto"
                    ),
                ),
                rx.el.div(
                    rx.el.a(
                        rx.icon("gamepad-2", class_name="h-4 w-4"),
                        "Retour aux jeux",
                        href="/games",
                        class_name=(
                            "flex flex-1 items-center justify-center gap-2 "
                            "rounded-xl border border-white/15 py-2.5 "
                            "text-[11px] font-black text-slate-200 "
                            "hover:border-[#22D3EE]/60"
                        ),
                    ),
                    rx.el.button(
                        rx.icon("scroll-text", class_name="h-4 w-4"),
                        "Voir le replay",
                        on_click=RoomState.open_replay,
                        class_name=(
                            "flex flex-1 items-center justify-center gap-2 "
                            "rounded-xl border border-[#1E9EF5]/50 py-2.5 "
                            "text-[11px] font-black text-[#7DC5FA] "
                            "hover:bg-[#1E9EF5]/10"
                        ),
                    ),
                    rx.el.button(
                        rx.icon("rotate-ccw", class_name="h-4 w-4"),
                        "Revanche",
                        on_click=RoomState.rematch,
                        class_name=(
                            "flex flex-1 items-center justify-center gap-2 "
                            "rounded-xl bg-emerald-500 py-2.5 text-[11px] "
                            "font-black text-[#04121F] hover:bg-emerald-400"
                        ),
                    ),
                    class_name="mt-3 flex flex-col gap-2 sm:flex-row",
                ),
                class_name=(
                    "tata-rise w-full max-w-lg rounded-2xl border "
                    "border-amber-400/30 bg-[#0B2647] p-4"
                ),
            ),
            class_name=(
                "fixed inset-0 z-50 flex items-center justify-center "
                "bg-[#04121F]/85 p-4"
            ),
        ),
        rx.fragment(),
    )


def replay_overlay() -> rx.Component:
    return rx.cond(
        RoomState.replay_open,
        rx.el.div(
            rx.el.div(
                rx.el.div(
                    rx.el.div(
                        rx.el.p(
                            "Replay chronologique",
                            class_name="text-sm font-black text-white",
                        ),
                        rx.el.p(
                            "Lecture seule, reconstituee depuis les actions "
                            "persistees. Aucune main cachee n'est revelee.",
                            class_name="text-[10px] text-slate-400",
                        ),
                        class_name="min-w-0 flex-1",
                    ),
                    rx.el.button(
                        rx.icon("x", class_name="h-4 w-4"),
                        on_click=RoomState.close_replay,
                        aria_label="Fermer le replay",
                        class_name="text-slate-500 hover:text-white",
                    ),
                    class_name=(
                        "flex items-start justify-between border-b "
                        "border-white/10 pb-2"
                    ),
                ),
                rx.cond(
                    RoomState.history_rows.length() > 0,
                    rx.el.div(
                        rx.foreach(RoomState.history_rows, history_row),
                        class_name=(
                            "mt-2 flex max-h-[60vh] flex-col divide-y "
                            "divide-white/5 overflow-y-auto"
                        ),
                    ),
                    rx.el.p(
                        "Aucune action a rejouer.",
                        class_name="mt-2 text-[11px] text-slate-500",
                    ),
                ),
                class_name=(
                    "tata-rise w-full max-w-xl rounded-2xl border "
                    "border-white/10 bg-[#0B2647] p-4"
                ),
            ),
            class_name=(
                "fixed inset-0 z-50 flex items-center justify-center "
                "bg-[#04121F]/85 p-4"
            ),
        ),
        rx.fragment(),
    )


# ------------------------------------------------------------------ full room
def tata_room() -> rx.Component:
    return rx.el.div(
        top_bar(),
        turn_strip(),
        round_banner(),
        rx.el.div(
            rx.el.div(
                opponents_row(),
                rx.el.div(tata_board(), class_name="mt-3"),
                rx.el.div(my_seat(), class_name="mt-3"),
                rx.el.div(tata_tray(), class_name="mt-3"),
                class_name="min-w-0 flex-1",
            ),
            tools_rail(),
            class_name="mt-3 flex flex-col gap-3 lg:flex-row",
        ),
        result_overlay(),
        replay_overlay(),
        class_name=(
            "w-full rounded-2xl border border-white/5 bg-[#071A33] p-2 "
            "font-['Inter'] sm:p-3"
        ),
    )
