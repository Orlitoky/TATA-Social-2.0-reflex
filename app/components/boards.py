"""Game boards: each one is the centerpiece of its play room."""

from __future__ import annotations

import reflex as rx

from app.components.game_shell import jewel_tag
from app.states.room_state import (
    HandCard,
    LotoCard,
    LotoCell,
    LudoCell,
    NodeRow,
    PointCell,
    RoomState,
    ScoreRow,
    SpectatorRow,
    TileRow,
)


# ------------------------------------------------------------------- helpers
def panel(*children, class_name: str = "") -> rx.Component:
    return rx.el.div(
        *children,
        class_name=(
            "rounded-2xl border border-zinc-800 bg-[#0C0D10] p-4 " + class_name
        ),
    )


def section_title(icon: str, label: str) -> rx.Component:
    return rx.el.div(
        rx.icon(icon, class_name="h-4 w-4 text-amber-300"),
        rx.el.h3(
            label,
            class_name=(
                "text-xs font-bold uppercase tracking-wider text-zinc-400"
            ),
        ),
        class_name="mb-3 flex items-center gap-2",
    )


# ---------------------------------------------------------------------- LOTO
def loto_cell(cell: LotoCell) -> rx.Component:
    return rx.cond(
        cell["value"] == 0,
        rx.el.div(
            class_name="h-9 rounded-md border border-zinc-800/60 bg-zinc-900/40"
        ),
        rx.cond(
            cell["marked"],
            rx.el.div(
                cell["value"],
                class_name=(
                    "flex h-9 items-center justify-center rounded-md "
                    "bg-emerald-500 text-sm font-bold text-black"
                ),
            ),
            rx.el.div(
                cell["value"],
                class_name=(
                    "flex h-9 items-center justify-center rounded-md border "
                    "border-amber-400/25 bg-[#141108] text-sm font-semibold "
                    "text-amber-100"
                ),
            ),
        ),
    )


def loto_card_view(card: LotoCard) -> rx.Component:
    return rx.el.div(
        rx.el.div(
            rx.el.span(
                f"Carton #{card['card_index']}",
                class_name="text-xs font-bold text-white",
            ),
            rx.el.span(
                f"{card['marked']}/15",
                class_name="text-xs font-semibold text-emerald-400",
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
                f"Faible: {card['remaining']} numero(s) restant(s)",
                class_name="mt-2 text-[11px] font-bold text-rose-400",
            ),
            rx.el.p(
                f"{card['remaining']} numero(s) restant(s)",
                class_name="mt-2 text-[11px] font-medium text-zinc-500",
            ),
        ),
        class_name="rounded-2xl border border-zinc-800 bg-[#0A0B0E] p-3",
    )


def spectator_row(row: SpectatorRow) -> rx.Component:
    return rx.el.div(
        rx.el.span(
            row["name"],
            class_name="truncate text-xs font-semibold text-zinc-200",
        ),
        rx.el.span(
            f"#{row['card_index']}",
            class_name="text-[11px] text-zinc-500",
        ),
        rx.cond(
            row["low"],
            rx.el.span(
                f"Faible {row['remaining']}",
                class_name=(
                    "w-fit rounded-full bg-rose-500/15 px-2 py-0.5 text-[10px] "
                    "font-bold text-rose-300"
                ),
            ),
            rx.el.span(
                row["remaining"],
                class_name="text-[11px] font-semibold text-zinc-400",
            ),
        ),
        class_name=(
            "flex items-center justify-between gap-2 border-b "
            "border-zinc-800/60 py-1.5 last:border-0"
        ),
    )


def loto_board() -> rx.Component:
    return rx.el.div(
        panel(
            rx.el.div(
                rx.el.div(
                    rx.el.p(
                        "Dernier tirage",
                        class_name=(
                            "text-[11px] font-bold uppercase tracking-wider "
                            "text-zinc-500"
                        ),
                    ),
                    rx.el.p(
                        rx.cond(
                            RoomState.last_number > 0,
                            RoomState.last_number,
                            "-",
                        ),
                        class_name=(
                            "text-5xl font-black leading-none text-amber-300"
                        ),
                    ),
                    class_name="shrink-0",
                ),
                rx.el.div(
                    rx.foreach(
                        RoomState.drawn,
                        lambda number: rx.el.span(
                            number,
                            class_name=(
                                "flex size-9 shrink-0 items-center "
                                "justify-center rounded-full border "
                                "border-amber-400/30 bg-[#141108] text-xs "
                                "font-bold text-amber-200"
                            ),
                        ),
                    ),
                    class_name="flex flex-1 flex-wrap gap-1.5",
                ),
                class_name="flex items-start gap-4",
            ),
            rx.el.div(
                jewel_tag(RoomState.tier_label, "gold"),
                jewel_tag(f"Pot {RoomState.pot_coins} pts", "cyan"),
                jewel_tag(f"Net {RoomState.net_prize} pts", "emerald"),
                rx.el.span(
                    "Gains nets, frais deduits.",
                    class_name="text-[11px] font-medium text-zinc-500",
                ),
                class_name="mt-3 flex flex-wrap items-center gap-2",
            ),
        ),
        rx.el.div(
            rx.el.div(
                panel(
                    section_title("credit-card", "Mes cartons"),
                    rx.cond(
                        RoomState.my_cards.length() > 0,
                        rx.el.div(
                            rx.foreach(RoomState.my_cards, loto_card_view),
                            class_name="grid gap-3 sm:grid-cols-2",
                        ),
                        rx.el.p(
                            "Aucun carton pour l'instant. Achetez de 1 a "
                            "10 cartons selon votre niveau.",
                            class_name="text-sm text-zinc-500",
                        ),
                    ),
                ),
                class_name="min-w-0 flex-1",
            ),
            rx.el.div(
                panel(
                    section_title("eye", "Spectateurs / cartons"),
                    rx.cond(
                        RoomState.spectators.length() > 0,
                        rx.el.div(
                            rx.foreach(RoomState.spectators, spectator_row),
                            class_name="flex flex-col",
                        ),
                        rx.el.p(
                            "Aucun carton en jeu.",
                            class_name="text-sm text-zinc-500",
                        ),
                    ),
                ),
                class_name="w-full lg:w-72 shrink-0",
            ),
            class_name="mt-4 flex flex-col gap-4 lg:flex-row",
        ),
        class_name="w-full",
    )


def loto_controls() -> rx.Component:
    return panel(
        section_title("ticket", "Cartons et tirage"),
        rx.el.div(
            rx.el.label(
                "Nombre de cartons",
                html_for="buy_count",
                class_name="text-xs font-semibold text-zinc-400",
            ),
            rx.el.input(
                id="buy_count",
                type="number",
                min=1,
                max=10,
                default_value=RoomState.buy_count.to_string(),
                on_change=RoomState.set_buy_count.debounce(300),
                class_name=(
                    "mt-1 w-full rounded-xl border border-zinc-800 "
                    "bg-[#0A0B0E] px-3 py-2 text-sm text-white outline-hidden "
                    "focus:border-amber-400/60"
                ),
            ),
            rx.el.p(
                f"{RoomState.tier_label}: {RoomState.tier_price} pts / carton, "
                f"max {RoomState.tier_max_cards}",
                class_name="mt-1 text-[11px] text-zinc-500",
            ),
            rx.el.button(
                rx.icon("plus", class_name="h-4 w-4"),
                "Acheter",
                on_click=RoomState.buy_cards,
                disabled=~RoomState.is_waiting,
                class_name=(
                    "mt-2 flex w-full items-center justify-center gap-2 "
                    "rounded-xl bg-emerald-500 py-2.5 text-sm font-bold "
                    "text-black hover:bg-emerald-400 disabled:opacity-40"
                ),
            ),
            class_name="w-full",
        ),
        rx.el.button(
            rx.icon("dices", class_name="h-4 w-4"),
            "Tirer la boule suivante",
            on_click=RoomState.draw_number,
            disabled=~RoomState.is_playing,
            class_name=(
                "mt-3 flex w-full items-center justify-center gap-2 rounded-xl "
                "border border-amber-400/40 bg-[#141108] py-2.5 text-sm "
                "font-bold text-amber-200 hover:bg-amber-400/10 "
                "disabled:opacity-40"
            ),
        ),
        rx.el.p(
            "Le tirage avance des que le minuteur atteint zero: aucun "
            "processus de fond n'est necessaire pour jouer.",
            class_name="mt-2 text-[11px] text-zinc-500",
        ),
    )


# -------------------------------------------------------------------- DOMINO
DOT = "size-1.5 rounded-full bg-black"
BLANK = "size-1.5"


def _pip(flag: int) -> rx.Component:
    return rx.el.span(class_name=DOT if flag else BLANK)


def face(
    a: int, b: int, c: int, d: int, e: int, f: int, g: int, h: int, i: int
) -> rx.Component:
    return rx.el.div(
        _pip(a),
        _pip(b),
        _pip(c),
        _pip(d),
        _pip(e),
        _pip(f),
        _pip(g),
        _pip(h),
        _pip(i),
        class_name=(
            "grid grid-cols-3 grid-rows-3 place-items-center gap-0.5 p-1"
        ),
    )


def pip_face(value: rx.Var) -> rx.Component:
    return rx.match(
        value,
        (0, rx.el.div(class_name="h-full w-full")),
        (1, face(0, 0, 0, 0, 1, 0, 0, 0, 0)),
        (2, face(1, 0, 0, 0, 0, 0, 0, 0, 1)),
        (3, face(1, 0, 0, 0, 1, 0, 0, 0, 1)),
        (4, face(1, 0, 1, 0, 0, 0, 1, 0, 1)),
        (5, face(1, 0, 1, 0, 1, 0, 1, 0, 1)),
        (6, face(1, 0, 1, 1, 0, 1, 1, 0, 1)),
        rx.el.div(class_name="h-full w-full"),
    )


def domino_tile(tile: TileRow, in_hand: bool = False) -> rx.Component:
    return rx.el.div(
        rx.el.div(
            pip_face(tile["a"]),
            class_name="flex h-8 w-8 items-center justify-center",
        ),
        rx.el.div(class_name="h-px w-6 bg-black/40"),
        rx.el.div(
            pip_face(tile["b"]),
            class_name="flex h-8 w-8 items-center justify-center",
        ),
        class_name=(
            "flex h-[76px] w-[38px] shrink-0 flex-col items-center "
            "justify-center gap-0.5 rounded-md border border-[#C8BB9B] "
            "bg-[linear-gradient(160deg,#FFFDF3,#EFE6CE_60%,#D9CDAF)] "
            "shadow-[0_3px_0_#A79571,0_5px_8px_rgba(0,0,0,0.45)]"
        ),
    )


def domino_hand_tile(tile: TileRow) -> rx.Component:
    return rx.el.div(
        domino_tile(tile, True),
        rx.el.div(
            rx.el.button(
                "G",
                on_click=lambda: RoomState.domino_play(tile["index"], "left"),
                aria_label="Poser a gauche",
                class_name=(
                    "flex-1 rounded-l-md bg-zinc-800 py-1 text-[10px] "
                    "font-bold text-zinc-200 hover:bg-emerald-500 "
                    "hover:text-black"
                ),
            ),
            rx.el.button(
                "D",
                on_click=lambda: RoomState.domino_play(tile["index"], "right"),
                aria_label="Poser a droite",
                class_name=(
                    "flex-1 rounded-r-md bg-zinc-800 py-1 text-[10px] "
                    "font-bold text-zinc-200 hover:bg-emerald-500 "
                    "hover:text-black"
                ),
            ),
            class_name="mt-1 flex w-[38px] gap-px",
        ),
        class_name=rx.cond(
            tile["playable"],
            "flex flex-col items-center opacity-100",
            "flex flex-col items-center opacity-50",
        ),
    )


def score_row(row: ScoreRow) -> rx.Component:
    return rx.el.div(
        rx.el.span(
            row["name"],
            class_name="truncate text-xs font-semibold text-zinc-200",
        ),
        rx.el.span(
            row["score"],
            class_name="text-sm font-bold text-amber-300 tabular-nums",
        ),
        class_name="flex items-center justify-between gap-2 py-1",
    )


def domino_board() -> rx.Component:
    return rx.el.div(
        panel(
            rx.el.div(
                jewel_tag(f"Maty {RoomState.maty_target}", "gold"),
                jewel_tag(RoomState.domino_variants, "violet"),
                jewel_tag(f"Pioche {RoomState.boneyard_count}", "cyan"),
                class_name="mb-3 flex flex-wrap gap-2",
            ),
            rx.el.div(
                rx.cond(
                    RoomState.chain.length() > 0,
                    rx.el.div(
                        rx.foreach(
                            RoomState.chain,
                            lambda tile: domino_tile(tile),
                        ),
                        class_name=(
                            "flex flex-wrap content-start items-center "
                            "gap-1.5 [&>div:nth-child(6n)]:rotate-90 "
                            "[&>div:nth-child(11n)]:rotate-90"
                        ),
                    ),
                    rx.el.p(
                        "La chaine est vide: posez la premiere tuile.",
                        class_name="text-sm text-zinc-400",
                    ),
                ),
                class_name=(
                    "min-h-48 w-full rounded-2xl border border-teal-900/60 "
                    "bg-[radial-gradient(circle_at_50%_20%,#0D3B39,#062225_70%)]"
                    " p-4"
                ),
            ),
            rx.el.div(
                rx.el.span(
                    f"Extremites: {RoomState.left_end} | {RoomState.right_end}",
                    class_name="text-[11px] font-semibold text-teal-300",
                ),
                class_name="mt-2",
            ),
        ),
        panel(
            section_title("hand", "Ma main"),
            rx.cond(
                RoomState.my_tiles.length() > 0,
                rx.el.div(
                    rx.foreach(RoomState.my_tiles, domino_hand_tile),
                    class_name="flex flex-wrap gap-2",
                ),
                rx.el.p("Main vide.", class_name="text-sm text-zinc-500"),
            ),
            rx.el.div(
                rx.el.button(
                    rx.icon("download", class_name="h-4 w-4"),
                    "Piocher",
                    on_click=RoomState.domino_draw,
                    disabled=~RoomState.my_turn,
                    class_name=(
                        "flex items-center gap-2 rounded-xl border "
                        "border-zinc-700 px-3 py-2 text-xs font-bold "
                        "text-zinc-200 hover:border-emerald-400 "
                        "disabled:opacity-40"
                    ),
                ),
                rx.el.button(
                    rx.icon("skip-forward", class_name="h-4 w-4"),
                    "Passer",
                    on_click=RoomState.domino_pass,
                    disabled=~RoomState.my_turn,
                    class_name=(
                        "flex items-center gap-2 rounded-xl border "
                        "border-zinc-700 px-3 py-2 text-xs font-bold "
                        "text-zinc-200 hover:border-emerald-400 "
                        "disabled:opacity-40"
                    ),
                ),
                class_name="mt-3 flex gap-2",
            ),
            class_name="mt-4",
        ),
        panel(
            section_title("trophy", "Tableau des scores"),
            rx.cond(
                RoomState.scores.length() > 0,
                rx.el.div(
                    rx.foreach(RoomState.scores, score_row),
                    class_name="flex flex-col divide-y divide-zinc-800/60",
                ),
                rx.el.p("Scores a zero.", class_name="text-sm text-zinc-500"),
            ),
            class_name="mt-4",
        ),
        class_name="w-full",
    )


def domino_result_modal() -> rx.Component:
    return rx.cond(
        RoomState.round_result_open,
        rx.el.div(
            rx.el.div(
                rx.el.h2(
                    "Fin de manche",
                    class_name="text-base font-bold text-white",
                ),
                rx.el.p(
                    RoomState.round_result_text,
                    class_name="mt-2 text-sm text-zinc-300",
                ),
                rx.el.p(
                    f"Objectif Maty {RoomState.maty_target}",
                    class_name="mt-1 text-xs text-amber-300",
                ),
                rx.el.button(
                    "Manche suivante",
                    on_click=RoomState.close_round_result,
                    class_name=(
                        "mt-4 w-full rounded-xl bg-emerald-500 py-2.5 "
                        "text-sm font-bold text-black hover:bg-emerald-400"
                    ),
                ),
                class_name=(
                    "w-full max-w-sm rounded-2xl border border-zinc-800 "
                    "bg-[#0C0D10] p-5"
                ),
            ),
            class_name=(
                "fixed inset-0 z-50 flex items-center justify-center "
                "bg-black/70 p-4"
            ),
        ),
    )


# ---------------------------------------------------------------------- LUDO
def pawn_dot(color: rx.Var) -> rx.Component:
    return rx.match(
        color,
        (
            "red",
            rx.el.span(
                class_name="size-3 rounded-full bg-rose-500 ring-1 ring-white/70"
            ),
        ),
        (
            "green",
            rx.el.span(
                class_name="size-3 rounded-full bg-emerald-500 ring-1 ring-white/70"
            ),
        ),
        (
            "yellow",
            rx.el.span(
                class_name="size-3 rounded-full bg-amber-400 ring-1 ring-white/70"
            ),
        ),
        (
            "blue",
            rx.el.span(
                class_name="size-3 rounded-full bg-sky-500 ring-1 ring-white/70"
            ),
        ),
        rx.fragment(),
    )


def ludo_cell(cell: LudoCell) -> rx.Component:
    return rx.el.div(
        rx.cond(cell["pawn"] != "", pawn_dot(cell["pawn"]), rx.fragment()),
        rx.cond(
            cell["safe"] & (cell["pawn"] == ""),
            rx.icon("star", class_name="h-2.5 w-2.5 text-amber-500"),
            rx.fragment(),
        ),
        rx.cond(
            (cell["arrow"] != "") & (cell["pawn"] == "") & ~cell["safe"],
            rx.icon(cell["arrow"], class_name="h-2.5 w-2.5 text-zinc-500"),
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
                        "flex aspect-square items-center justify-center bg-rose-900/50",
                    ),
                    (
                        "green",
                        "flex aspect-square items-center justify-center bg-emerald-900/50",
                    ),
                    (
                        "yellow",
                        "flex aspect-square items-center justify-center bg-amber-900/50",
                    ),
                    "flex aspect-square items-center justify-center bg-sky-900/50",
                ),
            ),
            (
                "lane",
                rx.match(
                    cell["color"],
                    (
                        "red",
                        "flex aspect-square items-center justify-center bg-rose-500/40",
                    ),
                    (
                        "green",
                        "flex aspect-square items-center justify-center bg-emerald-500/40",
                    ),
                    (
                        "yellow",
                        "flex aspect-square items-center justify-center bg-amber-500/40",
                    ),
                    "flex aspect-square items-center justify-center bg-sky-500/40",
                ),
            ),
            (
                "center",
                "flex aspect-square items-center justify-center bg-amber-400/70",
            ),
            (
                "path",
                "flex aspect-square items-center justify-center border border-zinc-800 bg-zinc-100/90",
            ),
            "aspect-square bg-[#0A0B0E]",
        ),
    )


def ludo_board() -> rx.Component:
    return rx.el.div(
        panel(
            rx.el.div(
                jewel_tag(f"Objectif {RoomState.ludo_goal} pions", "gold"),
                jewel_tag(f"De {RoomState.dice_value}", "cyan"),
                class_name="mb-3 flex flex-wrap gap-2",
            ),
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
                    "mx-auto flex w-full max-w-[520px] flex-col "
                    "overflow-hidden rounded-2xl border-4 border-zinc-800 "
                    "bg-[#0A0B0E]"
                ),
            ),
        ),
        panel(
            section_title("dices", "Mon tour"),
            rx.el.div(
                rx.el.div(
                    rx.cond(
                        RoomState.dice_value > 0, RoomState.dice_value, "?"
                    ),
                    class_name=rx.cond(
                        RoomState.dice_rolled,
                        "flex size-16 items-center justify-center rounded-2xl bg-white text-3xl font-black text-black animate-pulse",
                        "flex size-16 items-center justify-center rounded-2xl bg-white text-3xl font-black text-black",
                    ),
                ),
                rx.el.div(
                    rx.el.button(
                        "Lancer le de",
                        on_click=RoomState.ludo_roll,
                        disabled=~RoomState.my_turn,
                        class_name=(
                            "rounded-xl bg-emerald-500 px-4 py-2 text-sm "
                            "font-bold text-black hover:bg-emerald-400 "
                            "disabled:opacity-40"
                        ),
                    ),
                    rx.el.div(
                        rx.foreach(
                            RoomState.legal_pawns,
                            lambda index: rx.el.button(
                                f"Pion {index + 1}",
                                on_click=lambda: RoomState.ludo_move(index),
                                class_name=(
                                    "rounded-xl border border-zinc-700 px-3 "
                                    "py-2 text-xs font-bold text-zinc-100 "
                                    "hover:border-emerald-400"
                                ),
                            ),
                        ),
                        class_name="mt-2 flex flex-wrap gap-2",
                    ),
                    class_name="flex-1",
                ),
                class_name="flex items-start gap-4",
            ),
            class_name="mt-4",
        ),
        class_name="w-full",
    )


# ------------------------------------------------------------------ FARITANY
def faritany_node(node: NodeRow) -> rx.Component:
    return rx.el.button(
        rx.cond(
            node["empty"],
            rx.el.span(class_name="size-2 rounded-full bg-zinc-600"),
            rx.cond(
                node["mine"],
                rx.el.span(
                    class_name=(
                        "size-5 rounded-full bg-[radial-gradient(circle_at_30%_30%,"
                        "#FDE68A,#D97706)] ring-1 ring-amber-200"
                    )
                ),
                rx.el.span(
                    class_name=(
                        "size-5 rounded-full bg-[radial-gradient(circle_at_30%_30%,"
                        "#93C5FD,#1D4ED8)] ring-1 ring-sky-200"
                    )
                ),
            ),
        ),
        on_click=lambda: RoomState.faritany_click(node["index"]),
        aria_label="Case Faritany",
        class_name=rx.cond(
            node["selected"],
            "relative z-10 flex size-9 items-center justify-center rounded-full ring-2 ring-emerald-400",
            "relative z-10 flex size-9 items-center justify-center rounded-full hover:ring-1 hover:ring-zinc-600",
        ),
    )


def faritany_board() -> rx.Component:
    return rx.el.div(
        panel(
            rx.el.div(
                jewel_tag("Reseau diamant", "violet"),
                jewel_tag("15 s / tour", "ruby"),
                class_name="mb-3 flex flex-wrap gap-2",
            ),
            rx.el.div(
                rx.el.div(
                    rx.foreach(
                        RoomState.faritany_rows,
                        lambda row: rx.el.div(
                            rx.foreach(row, faritany_node),
                            class_name="flex items-center justify-between",
                        ),
                    ),
                    class_name=(
                        "relative z-10 flex flex-col justify-between gap-6 p-4"
                    ),
                ),
                rx.el.div(
                    class_name=(
                        "pointer-events-none absolute inset-4 "
                        "[background-image:repeating-linear-gradient(0deg,"
                        "rgba(148,163,184,0.35)_0_1px,transparent_1px_25%),"
                        "repeating-linear-gradient(90deg,"
                        "rgba(148,163,184,0.35)_0_1px,transparent_1px_25%),"
                        "linear-gradient(45deg,transparent_49%,"
                        "rgba(148,163,184,0.22)_49%_51%,transparent_51%),"
                        "linear-gradient(-45deg,transparent_49%,"
                        "rgba(148,163,184,0.22)_49%_51%,transparent_51%)]"
                    ),
                ),
                class_name=(
                    "relative mx-auto aspect-square w-full max-w-[420px] "
                    "rounded-2xl border border-indigo-900/70 "
                    "bg-[radial-gradient(circle_at_50%_40%,#131A2E,#080A12_70%)]"
                ),
            ),
            rx.el.p(
                "Cliquez un de vos pions puis une case adjacente vide. Un "
                "pion ennemi juste derriere est capture par approche.",
                class_name="mt-3 text-[11px] text-zinc-500",
            ),
        ),
        class_name="w-full",
    )


# ------------------------------------------------------------ JEUX DE POINT
def point_cell(cell: PointCell) -> rx.Component:
    return rx.match(
        cell["kind"],
        (
            "dot",
            rx.el.div(
                rx.el.span(class_name="size-2 rounded-full bg-zinc-300"),
                class_name="flex size-4 items-center justify-center",
            ),
        ),
        (
            "h",
            rx.el.button(
                on_click=lambda: RoomState.points_claim("h", cell["index"]),
                aria_label="Ligne horizontale",
                class_name=rx.cond(
                    cell["owner"] == "",
                    "h-4 w-10 rounded bg-zinc-800 hover:bg-emerald-500/70",
                    "h-4 w-10 rounded bg-amber-400",
                ),
            ),
        ),
        (
            "v",
            rx.el.button(
                on_click=lambda: RoomState.points_claim("v", cell["index"]),
                aria_label="Ligne verticale",
                class_name=rx.cond(
                    cell["owner"] == "",
                    "h-10 w-4 rounded bg-zinc-800 hover:bg-emerald-500/70",
                    "h-10 w-4 rounded bg-cyan-400",
                ),
            ),
        ),
        rx.el.div(
            class_name=rx.cond(
                cell["owner"] == "",
                "h-10 w-10 rounded bg-transparent",
                "h-10 w-10 rounded bg-emerald-500/30",
            ),
        ),
    )


def points_board() -> rx.Component:
    return rx.el.div(
        panel(
            rx.el.div(
                jewel_tag("Pipopipette", "cyan"),
                jewel_tag("15 s / tour", "ruby"),
                class_name="mb-3 flex flex-wrap gap-2",
            ),
            rx.el.div(
                rx.foreach(
                    RoomState.points_grid,
                    lambda row: rx.el.div(
                        rx.foreach(row, point_cell),
                        class_name="flex items-center justify-center gap-0.5",
                    ),
                ),
                class_name=(
                    "mx-auto flex w-fit flex-col items-center gap-0.5 "
                    "rounded-2xl border border-zinc-800 bg-[#0A0B0E] p-5"
                ),
            ),
            rx.el.div(
                rx.foreach(RoomState.scores, score_row),
                class_name="mt-3 flex flex-col divide-y divide-zinc-800/60",
            ),
        ),
        class_name="w-full",
    )


# ------------------------------------------------------------- RAMI and TRI
def hand_card(card: HandCard) -> rx.Component:
    return rx.el.button(
        card["label"],
        on_click=lambda: RoomState.toggle_card(card["index"]),
        aria_label="Carte",
        class_name=rx.cond(
            card["selected"],
            rx.cond(
                card["red"],
                "h-20 w-14 shrink-0 -translate-y-2 rounded-lg border-2 border-emerald-400 bg-white text-lg font-bold text-rose-600",
                "h-20 w-14 shrink-0 -translate-y-2 rounded-lg border-2 border-emerald-400 bg-white text-lg font-bold text-zinc-900",
            ),
            rx.cond(
                card["red"],
                "h-20 w-14 shrink-0 rounded-lg border border-zinc-400 bg-white text-lg font-bold text-rose-600 hover:-translate-y-1",
                "h-20 w-14 shrink-0 rounded-lg border border-zinc-400 bg-white text-lg font-bold text-zinc-900 hover:-translate-y-1",
            ),
        ),
    )


def cards_board(is_tri: bool) -> rx.Component:
    return rx.el.div(
        panel(
            rx.el.div(
                rx.cond(
                    is_tri,
                    jewel_tag("32 cartes - variante malgache", "violet"),
                    jewel_tag("52 cartes", "violet"),
                ),
                jewel_tag(f"Pioche {RoomState.stock_count}", "cyan"),
                class_name="mb-3 flex flex-wrap gap-2",
            ),
            rx.cond(
                is_tri,
                rx.el.p(
                    "TRI est presente ici comme une variante malgache de jeu "
                    "de defausse: posez la meme couleur ou le meme rang, "
                    "sinon piochez ou passez.",
                    class_name="mb-3 text-xs text-zinc-400",
                ),
                rx.el.p(
                    "Piochez au talon ou a la defausse, posez des "
                    "combinaisons (meme rang ou suite de meme couleur), "
                    "puis defaussez une carte.",
                    class_name="mb-3 text-xs text-zinc-400",
                ),
            ),
            rx.el.div(
                rx.el.div(
                    rx.el.p(
                        "Defausse",
                        class_name="text-[11px] font-bold text-zinc-500",
                    ),
                    rx.el.div(
                        rx.cond(
                            RoomState.discard_label != "",
                            RoomState.discard_label,
                            "-",
                        ),
                        class_name=(
                            "mt-1 flex h-24 w-16 items-center justify-center "
                            "rounded-xl border border-zinc-500 bg-white "
                            "text-xl font-bold text-zinc-900"
                        ),
                    ),
                    class_name="text-center",
                ),
                rx.el.div(
                    rx.el.p(
                        "Talon",
                        class_name="text-[11px] font-bold text-zinc-500",
                    ),
                    rx.el.div(
                        RoomState.stock_count,
                        class_name=(
                            "mt-1 flex h-24 w-16 items-center justify-center "
                            "rounded-xl border border-zinc-700 "
                            "bg-[linear-gradient(140deg,#1F2937,#0B1120)] "
                            "text-lg font-bold text-zinc-300"
                        ),
                    ),
                    class_name="text-center",
                ),
                class_name=(
                    "flex items-center justify-center gap-6 rounded-2xl "
                    "border border-emerald-900/60 "
                    "bg-[radial-gradient(circle_at_50%_10%,#0C3B2A,#06170F_70%)]"
                    " p-6"
                ),
            ),
        ),
        panel(
            section_title("hand", "Ma main"),
            rx.cond(
                RoomState.my_hand.length() > 0,
                rx.el.div(
                    rx.foreach(RoomState.my_hand, hand_card),
                    class_name="flex flex-wrap gap-2",
                ),
                rx.el.p("Main vide.", class_name="text-sm text-zinc-500"),
            ),
            rx.el.div(
                rx.el.button(
                    "Piocher au talon",
                    on_click=lambda: RoomState.cards_draw("stock"),
                    disabled=~RoomState.my_turn,
                    class_name=(
                        "rounded-xl border border-zinc-700 px-3 py-2 "
                        "text-xs font-bold text-zinc-100 "
                        "hover:border-emerald-400 disabled:opacity-40"
                    ),
                ),
                rx.el.button(
                    "Prendre la defausse",
                    on_click=lambda: RoomState.cards_draw("discard"),
                    disabled=~RoomState.my_turn,
                    class_name=(
                        "rounded-xl border border-zinc-700 px-3 py-2 "
                        "text-xs font-bold text-zinc-100 "
                        "hover:border-emerald-400 disabled:opacity-40"
                    ),
                ),
                rx.cond(
                    is_tri,
                    rx.el.div(
                        rx.el.button(
                            "Jouer la carte",
                            on_click=RoomState.tri_play_selected,
                            disabled=~RoomState.my_turn,
                            class_name=(
                                "rounded-xl bg-emerald-500 px-3 py-2 text-xs "
                                "font-bold text-black hover:bg-emerald-400 "
                                "disabled:opacity-40"
                            ),
                        ),
                        rx.el.button(
                            "Passer",
                            on_click=RoomState.tri_pass,
                            disabled=~RoomState.my_turn,
                            class_name=(
                                "rounded-xl border border-zinc-700 px-3 py-2 "
                                "text-xs font-bold text-zinc-100 "
                                "hover:border-emerald-400 disabled:opacity-40"
                            ),
                        ),
                        class_name="flex gap-2",
                    ),
                    rx.el.div(
                        rx.el.button(
                            "Poser la combinaison",
                            on_click=RoomState.cards_meld,
                            disabled=~RoomState.my_turn,
                            class_name=(
                                "rounded-xl border border-amber-400/50 "
                                "px-3 py-2 text-xs font-bold text-amber-200 "
                                "hover:bg-amber-400/10 disabled:opacity-40"
                            ),
                        ),
                        rx.el.button(
                            "Defausser",
                            on_click=RoomState.cards_discard,
                            disabled=~RoomState.my_turn,
                            class_name=(
                                "rounded-xl bg-emerald-500 px-3 py-2 text-xs "
                                "font-bold text-black hover:bg-emerald-400 "
                                "disabled:opacity-40"
                            ),
                        ),
                        class_name="flex gap-2",
                    ),
                ),
                class_name="mt-3 flex flex-wrap gap-2",
            ),
            rx.cond(
                RoomState.melds.length() > 0,
                rx.el.div(
                    rx.foreach(
                        RoomState.melds,
                        lambda meld: rx.el.div(
                            rx.el.span(
                                meld["name"],
                                class_name="text-[11px] font-bold text-zinc-400",
                            ),
                            rx.el.span(
                                meld["label"],
                                class_name="text-sm font-semibold text-white",
                            ),
                            class_name="flex items-center gap-2",
                        ),
                    ),
                    class_name="mt-3 flex flex-col gap-1",
                ),
            ),
            class_name="mt-4",
        ),
        class_name="w-full",
    )


# ------------------------------------------------------------------- BILLARD
def billard_board() -> rx.Component:
    return rx.el.div(
        panel(
            rx.el.div(
                jewel_tag("1v1", "emerald"),
                jewel_tag(RoomState.my_group, "gold"),
                rx.el.span(
                    "Simulation 2D deterministe calculee par le serveur "
                    "(table CSS dimensionnelle, pas de 3D).",
                    class_name="text-[11px] text-zinc-500",
                ),
                class_name="mb-3 flex flex-wrap items-center gap-2",
            ),
            rx.el.div(
                rx.el.div(
                    rx.foreach(
                        RoomState.balls,
                        lambda ball: rx.el.div(
                            ball["label"],
                            style={
                                "left": f"{ball['left']:.2f}%",
                                "top": f"{ball['top']:.2f}%",
                                "backgroundColor": ball["color"],
                            },
                            class_name=(
                                "absolute flex size-[5%] -translate-x-1/2 "
                                "-translate-y-1/2 items-center justify-center "
                                "rounded-full text-[9px] font-bold "
                                "text-black shadow-[inset_-2px_-3px_6px_"
                                "rgba(0,0,0,0.45),inset_2px_2px_4px_"
                                "rgba(255,255,255,0.55)]"
                            ),
                        ),
                    ),
                    rx.el.span(
                        class_name="absolute left-[2%] top-[4%] size-[7%] -translate-x-1/2 -translate-y-1/2 rounded-full bg-black/80"
                    ),
                    rx.el.span(
                        class_name="absolute left-[50%] top-[2.5%] size-[7%] -translate-x-1/2 -translate-y-1/2 rounded-full bg-black/80"
                    ),
                    rx.el.span(
                        class_name="absolute left-[98%] top-[4%] size-[7%] -translate-x-1/2 -translate-y-1/2 rounded-full bg-black/80"
                    ),
                    rx.el.span(
                        class_name="absolute left-[2%] top-[96%] size-[7%] -translate-x-1/2 -translate-y-1/2 rounded-full bg-black/80"
                    ),
                    rx.el.span(
                        class_name="absolute left-[50%] top-[97.5%] size-[7%] -translate-x-1/2 -translate-y-1/2 rounded-full bg-black/80"
                    ),
                    rx.el.span(
                        class_name="absolute left-[98%] top-[96%] size-[7%] -translate-x-1/2 -translate-y-1/2 rounded-full bg-black/80"
                    ),
                    class_name=(
                        "relative aspect-[2/1] w-full rounded-xl "
                        "bg-[radial-gradient(circle_at_50%_30%,#12805A,"
                        "#0A5238_75%)] shadow-[inset_0_0_40px_rgba(0,0,0,0.55)]"
                    ),
                ),
                class_name=(
                    "rounded-3xl border-[10px] border-[#5B3A1A] "
                    "bg-[#3E2711] p-2 "
                    "shadow-[0_18px_30px_rgba(0,0,0,0.6)]"
                ),
            ),
            rx.el.p(
                RoomState.billard_note,
                class_name="mt-2 text-xs font-semibold text-emerald-300",
            ),
        ),
        panel(
            section_title("crosshair", "Visee"),
            rx.el.label(
                f"Angle {RoomState.aim_angle}°",
                html_for="angle",
                class_name="text-xs font-semibold text-zinc-400",
            ),
            rx.el.input(
                id="angle",
                type="range",
                min=-180,
                max=180,
                default_value=RoomState.aim_angle.to_string(),
                on_change=RoomState.set_angle.throttle(100),
                class_name="mt-1 w-full accent-emerald-500",
            ),
            rx.el.label(
                f"Puissance {RoomState.aim_power}%",
                html_for="power",
                class_name="mt-3 block text-xs font-semibold text-zinc-400",
            ),
            rx.el.input(
                id="power",
                type="range",
                min=5,
                max=100,
                default_value=RoomState.aim_power.to_string(),
                on_change=RoomState.set_power.throttle(100),
                class_name="mt-1 w-full accent-amber-400",
            ),
            rx.el.button(
                rx.icon("target", class_name="h-4 w-4"),
                "Tirer",
                on_click=RoomState.billard_shoot,
                disabled=~RoomState.my_turn,
                class_name=(
                    "mt-3 flex w-full items-center justify-center gap-2 "
                    "rounded-xl bg-emerald-500 py-2.5 text-sm font-bold "
                    "text-black hover:bg-emerald-400 disabled:opacity-40"
                ),
            ),
            class_name="mt-4",
        ),
        class_name="w-full",
    )


def game_board() -> rx.Component:
    return rx.match(
        RoomState.slug,
        ("loto", loto_board()),
        ("domino", domino_board()),
        ("ludo", ludo_board()),
        ("faritany", faritany_board()),
        ("points", points_board()),
        ("rami", cards_board(False)),
        ("tri", cards_board(True)),
        ("billard", billard_board()),
        rx.el.p("Plateau indisponible.", class_name="text-sm text-zinc-500"),
    )
