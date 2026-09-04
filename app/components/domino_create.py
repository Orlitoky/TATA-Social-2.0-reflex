"""Domino "Creer une partie" mobile bottom sheet (controlled, reusable)."""

from __future__ import annotations

import reflex as rx

from app.states.games_state import GamesState

NAVY = "bg-[#07111f]"
PANEL = "bg-[#0c1a2b]"


def domino_pip_motif() -> rx.Component:
    """Compact ivory domino-pip motif used as the sheet's visual anchor."""
    return rx.el.div(
        rx.el.div(
            rx.foreach(
                [0, 1, 2, 3, 4, 5],
                lambda _i: rx.el.span(
                    class_name="size-1.5 rounded-full bg-[#F6F1E3]"
                ),
            ),
            class_name="grid grid-cols-2 gap-1",
        ),
        rx.el.span(class_name="h-8 w-px bg-[#F6F1E3]/30"),
        rx.el.div(
            rx.foreach(
                [0, 1, 2],
                lambda _i: rx.el.span(
                    class_name="size-1.5 rounded-full bg-[#F6F1E3]"
                ),
            ),
            class_name="grid grid-cols-1 gap-1",
        ),
        class_name=(
            "flex h-11 w-14 shrink-0 items-center justify-center gap-2 "
            "rounded-lg border border-white/10 bg-[#101f33] px-2"
        ),
    )


def section_title(label: str, hint: str = "") -> rx.Component:
    return rx.el.div(
        rx.el.p(
            label,
            class_name=(
                "text-[11px] font-bold uppercase tracking-[0.14em] "
                "text-slate-400"
            ),
        ),
        rx.el.p(hint, class_name="text-[11px] font-medium text-slate-500"),
        class_name="mb-2 flex items-baseline justify-between gap-2",
    )


def game_mode_selector() -> rx.Component:
    return rx.el.div(
        section_title("Mode de jeu"),
        rx.el.div(
            rx.foreach(GamesState.domino_modes, mode_option),
            class_name="grid grid-cols-2 gap-2",
        ),
        class_name="w-full",
    )


def mode_option(mode: dict[str, str]) -> rx.Component:
    selected = GamesState.draft_mode == mode["key"]
    return rx.el.button(
        rx.icon(
            mode["icon"],
            class_name=rx.cond(
                selected,
                "h-4 w-4 text-[#5AB0FF]",
                "h-4 w-4 text-[#3E6E9E]",
            ),
        ),
        rx.el.div(
            rx.el.p(
                mode["label"],
                class_name="text-[13px] font-bold leading-tight text-white",
            ),
            rx.el.p(
                mode["hint"],
                class_name="text-[11px] font-medium text-slate-400",
            ),
            class_name="min-w-0 text-left",
        ),
        type="button",
        on_click=lambda: GamesState.set_draft_mode(mode["key"]),
        class_name=rx.cond(
            selected,
            "flex items-center gap-2 rounded-xl border border-[#F4C542]/70 "
            "bg-[#132846] px-3 py-2.5 ring-1 ring-[#F4C542]/30",
            "flex items-center gap-2 rounded-xl border border-white/8 "
            "bg-[#0f1d30] px-3 py-2.5 hover:border-white/20",
        ),
    )


def score_chip(score: dict[str, str]) -> rx.Component:
    selected = GamesState.draft_score_choice == score["key"]
    is_custom = score["key"] == "custom"
    return rx.el.button(
        score["label"],
        type="button",
        on_click=lambda: GamesState.set_draft_score_choice(score["key"]),
        class_name=rx.cond(
            selected,
            rx.cond(
                is_custom,
                "rounded-xl border border-[#A855F7] bg-[#2A1740] px-3 py-2 "
                "text-[13px] font-bold text-[#E9D5FF]",
                "rounded-xl border border-[#F4C542] bg-[#2A2208] px-3 py-2 "
                "text-[13px] font-bold text-[#FFE79A]",
            ),
            rx.cond(
                is_custom,
                "rounded-xl border border-[#A855F7]/30 bg-[#0f1d30] px-3 "
                "py-2 text-[13px] font-bold text-[#C9A6F0] "
                "hover:border-[#A855F7]/60",
                "rounded-xl border border-white/8 bg-[#0f1d30] px-3 py-2 "
                "text-[13px] font-bold text-slate-300 hover:border-white/20",
            ),
        ),
    )


def score_selector() -> rx.Component:
    return rx.el.div(
        section_title("Score cible", GamesState.draft_score_summary),
        rx.el.div(
            rx.foreach(GamesState.domino_scores, score_chip),
            class_name="grid grid-cols-5 gap-2",
        ),
        rx.cond(
            GamesState.draft_is_custom_score,
            rx.el.div(
                rx.el.input(
                    placeholder="Score libre (20 - 500)",
                    type="text",
                    input_mode="numeric",
                    default_value=GamesState.draft_custom_score,
                    on_change=GamesState.set_draft_custom_score.debounce(250),
                    aria_label="Score personnalise",
                    class_name=(
                        "w-full rounded-xl border border-[#A855F7]/50 "
                        "bg-[#160b26] px-3 py-2.5 text-sm font-semibold "
                        "text-white outline-hidden placeholder:text-slate-500 "
                        "focus:border-[#A855F7]"
                    ),
                ),
                rx.el.p(
                    "Chiffres uniquement, entre 20 et 500 points.",
                    class_name="mt-1 text-[11px] text-slate-500",
                ),
                class_name="mt-2",
            ),
        ),
        class_name="w-full",
    )


def player_chip(count: int) -> rx.Component:
    selected = GamesState.draft_players == count
    return rx.el.button(
        rx.icon(
            "users",
            class_name=rx.cond(
                selected,
                "h-4 w-4 text-[#5AB0FF]",
                "h-4 w-4 text-[#3E6E9E]",
            ),
        ),
        rx.el.span(
            f"{count} joueurs",
            class_name="text-[13px] font-bold text-white",
        ),
        type="button",
        on_click=lambda: GamesState.set_draft_players(count),
        class_name=rx.cond(
            selected,
            "flex flex-1 items-center justify-center gap-2 rounded-xl "
            "border border-[#5AB0FF] bg-[#102a45] py-2.5",
            "flex flex-1 items-center justify-center gap-2 rounded-xl "
            "border border-white/8 bg-[#0f1d30] py-2.5 "
            "hover:border-white/20",
        ),
    )


def player_count_selector() -> rx.Component:
    return rx.el.div(
        section_title("Joueurs"),
        rx.el.div(
            player_chip(2),
            player_chip(3),
            class_name="flex gap-2",
        ),
        class_name="w-full",
    )


def rule_row(rule: dict[str, str]) -> rx.Component:
    active = GamesState.draft_rule_values[rule["key"]]
    return rx.el.button(
        rx.icon(
            rule["icon"],
            class_name=rx.cond(
                active,
                "h-4 w-4 text-[#F4C542]",
                "h-4 w-4 text-[#3E6E9E]",
            ),
        ),
        rx.el.div(
            rx.el.p(
                rule["label"],
                class_name="text-[13px] font-bold text-white",
            ),
            rx.el.p(
                rule["hint"],
                class_name="text-[11px] font-medium text-slate-400",
            ),
            class_name="min-w-0 flex-1 text-left",
        ),
        rx.el.span(
            rx.el.span(
                class_name=rx.cond(
                    active,
                    "size-4 translate-x-4 rounded-full bg-[#07111f] "
                    "transition-transform",
                    "size-4 translate-x-0 rounded-full bg-slate-400 "
                    "transition-transform",
                )
            ),
            class_name=rx.cond(
                active,
                "flex h-5 w-9 shrink-0 items-center rounded-full "
                "bg-[#F4C542] p-0.5",
                "flex h-5 w-9 shrink-0 items-center rounded-full "
                "bg-[#182a41] p-0.5",
            ),
        ),
        type="button",
        on_click=lambda: GamesState.toggle_draft_rule(rule["key"]),
        class_name=rx.cond(
            active,
            "flex w-full items-center gap-3 rounded-xl border "
            "border-[#F4C542]/40 bg-[#131f31] px-3 py-2.5",
            "flex w-full items-center gap-3 rounded-xl border border-white/8 "
            "bg-[#0f1d30] px-3 py-2.5 hover:border-white/20",
        ),
    )


def optional_rules() -> rx.Component:
    return rx.el.div(
        section_title("Regles optionnelles"),
        rx.el.div(
            rx.foreach(GamesState.domino_rules, rule_row),
            class_name="flex flex-col gap-2",
        ),
        class_name="w-full",
    )


def game_settings() -> rx.Component:
    """Scrollable, keyboard-safe settings body of the sheet."""
    return rx.el.div(
        game_mode_selector(),
        score_selector(),
        player_count_selector(),
        optional_rules(),
        rx.cond(
            GamesState.draft_error != "",
            rx.el.div(
                rx.icon("circle-alert", class_name="h-4 w-4 text-rose-400"),
                rx.el.p(
                    GamesState.draft_error,
                    class_name="text-[12px] font-semibold text-rose-300",
                ),
                class_name=(
                    "flex items-start gap-2 rounded-xl border "
                    "border-rose-500/30 bg-rose-500/10 px-3 py-2"
                ),
            ),
        ),
        rx.el.p(
            "Les points TATA sont virtuels et internes: aucun achat, aucun "
            "depot, aucun retrait, aucune valeur monetaire.",
            class_name="text-[11px] leading-relaxed text-slate-500",
        ),
        class_name=(
            "flex w-full flex-col gap-4 overflow-y-auto px-4 pb-4 pt-3 "
            "max-h-[62dvh]"
        ),
    )


def sheet_header() -> rx.Component:
    return rx.el.div(
        domino_pip_motif(),
        rx.el.div(
            rx.el.h2(
                "Creer une partie",
                class_name=("text-[15px] font-black tracking-tight text-white"),
            ),
            rx.el.p(
                "Domino double-six • salle d'attente",
                class_name="text-[11px] font-medium text-slate-400",
            ),
            class_name="min-w-0 flex-1",
        ),
        rx.el.button(
            rx.icon("x", class_name="h-4 w-4"),
            type="button",
            on_click=GamesState.cancel_domino_sheet,
            aria_label="Fermer",
            class_name=(
                "flex size-8 shrink-0 items-center justify-center rounded-lg "
                "border border-white/10 text-slate-400 hover:text-white"
            ),
        ),
        class_name=(
            "flex items-center gap-3 border-b border-white/8 px-4 pb-3 pt-4"
        ),
    )


def sheet_footer() -> rx.Component:
    return rx.el.div(
        rx.el.button(
            "Annuler",
            type="button",
            on_click=GamesState.cancel_domino_sheet,
            class_name=(
                "rounded-xl border border-white/10 bg-[#0f1d30] px-4 py-3 "
                "text-[13px] font-bold text-slate-300 hover:text-white"
            ),
        ),
        rx.el.button(
            rx.cond(
                GamesState.domino_creating,
                rx.el.span(
                    rx.icon(
                        "loader-circle",
                        class_name="h-4 w-4 animate-spin text-[#07111f]",
                    ),
                    rx.el.span("Creation..."),
                    class_name="flex items-center justify-center gap-2",
                ),
                rx.el.span(
                    rx.icon("play", class_name="h-4 w-4"),
                    rx.el.span("Creer la partie"),
                    class_name="flex items-center justify-center gap-2",
                ),
            ),
            type="button",
            disabled=GamesState.domino_creating,
            on_click=GamesState.create_domino_room,
            class_name=(
                "flex-1 rounded-xl bg-[#F4C542] px-4 py-3 text-[13px] "
                "font-black text-[#07111f] hover:bg-[#FFD75E] "
                "disabled:opacity-60"
            ),
        ),
        class_name=(
            "sticky bottom-0 flex items-center gap-2 border-t "
            "border-white/8 bg-[#07111f]/95 px-4 pt-3 backdrop-blur "
            "pb-[calc(env(safe-area-inset-bottom)+12px)]"
        ),
    )


def create_game_modal() -> rx.Component:
    """Slide-up domino creation sheet with dim overlay."""
    return rx.cond(
        GamesState.domino_sheet_open,
        rx.el.div(
            rx.el.div(
                on_click=GamesState.cancel_domino_sheet,
                class_name="absolute inset-0 bg-black/70 backdrop-blur-xs",
            ),
            rx.el.div(
                rx.el.div(
                    class_name=(
                        "mx-auto mt-2 h-1 w-10 rounded-full bg-white/15"
                    )
                ),
                sheet_header(),
                game_settings(),
                sheet_footer(),
                class_name=(
                    "relative z-10 w-full max-w-md overflow-hidden "
                    "rounded-t-2xl border border-white/10 border-b-0 "
                    "bg-[#07111f] shadow-[0_-8px_30px_rgba(0,0,0,0.6)] "
                    "max-h-[92dvh] animate-[slideUp_.22s_ease-out]"
                ),
            ),
            class_name=(
                "fixed inset-0 z-50 flex items-end justify-center "
                "font-['Inter']"
            ),
        ),
    )
