"""Bright generic room-creation sheet for Ludo and Loto detail pages."""

from __future__ import annotations

import reflex as rx

from app.states.games_state import GamesState

INPUT = (
    "mt-1 w-full rounded-lg border border-slate-200 bg-white px-3 py-2 "
    "text-sm font-medium text-[#071A33] outline-hidden "
    "placeholder:text-slate-400 focus:border-[#1E9EF5] "
    "focus:ring-2 focus:ring-[#1E9EF5]/20"
)


def label(text: str) -> rx.Component:
    return rx.el.label(
        text,
        class_name=(
            "text-[11px] font-bold uppercase tracking-[0.12em] text-slate-500"
        ),
    )


def player_chip(count: int) -> rx.Component:
    return rx.el.button(
        f"{count}",
        type="button",
        on_click=lambda: GamesState.set_gen_players(count),
        aria_label=f"{count} joueurs",
        class_name=rx.cond(
            GamesState.gen_players == count,
            "rounded-lg border border-[#1E9EF5] bg-[#EAF6FE] px-3 py-2 "
            "text-sm font-bold text-[#0B4F86]",
            "rounded-lg border border-slate-200 bg-white px-3 py-2 text-sm "
            "font-bold text-slate-600 hover:border-[#1E9EF5]/60",
        ),
    )


def tier_row(tier: dict[str, str]) -> rx.Component:
    return rx.el.button(
        rx.el.div(
            rx.el.p(
                tier["label"],
                class_name="text-[13px] font-bold text-[#071A33]",
            ),
            rx.el.p(
                f"{tier['price']} pts / carton • max {tier['max']}",
                class_name="text-[11px] font-medium text-slate-500",
            ),
            class_name="min-w-0 text-left",
        ),
        rx.cond(
            GamesState.gen_tier == tier["key"],
            rx.icon("check", class_name="h-4 w-4 text-[#1E9EF5]"),
            rx.el.span(class_name="size-4"),
        ),
        type="button",
        on_click=lambda: GamesState.set_gen_tier(tier["key"]),
        class_name=rx.cond(
            GamesState.gen_tier == tier["key"],
            "flex w-full items-center justify-between gap-2 rounded-lg "
            "border border-[#1E9EF5] bg-[#F5FAFF] px-3 py-2",
            "flex w-full items-center justify-between gap-2 rounded-lg "
            "border border-slate-200 bg-white px-3 py-2 "
            "hover:border-[#1E9EF5]/60",
        ),
    )


def privacy_selector() -> rx.Component:
    return rx.el.div(
        label("Visibilite"),
        rx.el.div(
            rx.el.button(
                rx.icon("globe", class_name="h-4 w-4"),
                rx.el.span("Publique", class_name="text-xs font-bold"),
                type="button",
                on_click=rx.cond(
                    GamesState.gen_private,
                    GamesState.toggle_gen_private,
                    rx.noop(),
                ),
                class_name=rx.cond(
                    GamesState.gen_private,
                    "flex flex-1 items-center justify-center gap-2 rounded-lg "
                    "border border-slate-200 bg-white py-2 text-slate-600",
                    "flex flex-1 items-center justify-center gap-2 rounded-lg "
                    "border border-[#1E9EF5] bg-[#EAF6FE] py-2 "
                    "text-[#0B4F86]",
                ),
            ),
            rx.el.button(
                rx.icon("lock", class_name="h-4 w-4"),
                rx.el.span("Privee", class_name="text-xs font-bold"),
                type="button",
                on_click=rx.cond(
                    GamesState.gen_private,
                    rx.noop(),
                    GamesState.toggle_gen_private,
                ),
                class_name=rx.cond(
                    GamesState.gen_private,
                    "flex flex-1 items-center justify-center gap-2 rounded-lg "
                    "border border-[#1E9EF5] bg-[#EAF6FE] py-2 "
                    "text-[#0B4F86]",
                    "flex flex-1 items-center justify-center gap-2 rounded-lg "
                    "border border-slate-200 bg-white py-2 text-slate-600",
                ),
            ),
            class_name="mt-1 flex gap-2",
        ),
        rx.cond(
            GamesState.gen_private,
            rx.el.div(
                rx.el.input(
                    placeholder="Code d'acces (4 caracteres minimum)",
                    default_value=GamesState.gen_secret,
                    on_change=GamesState.set_gen_secret.debounce(300),
                    aria_label="Code d'acces prive",
                    class_name=INPUT,
                ),
                class_name="mt-2",
            ),
        ),
        class_name="w-full",
    )


def create_room_sheet() -> rx.Component:
    """Controlled Ludo/Loto creation sheet (never used for Domino)."""
    return rx.cond(
        GamesState.create_sheet_open,
        rx.el.div(
            rx.el.div(
                on_click=GamesState.close_create_sheet,
                class_name="absolute inset-0 bg-[#071A33]/50",
            ),
            rx.el.div(
                rx.el.div(
                    rx.el.div(
                        rx.el.h2(
                            "Creer une salle",
                            class_name=("text-[15px] font-bold text-[#071A33]"),
                        ),
                        rx.el.p(
                            GamesState.detail_mode,
                            class_name=(
                                "text-[11px] font-medium text-slate-500"
                            ),
                        ),
                        class_name="min-w-0 flex-1",
                    ),
                    rx.el.button(
                        rx.icon("x", class_name="h-4 w-4"),
                        type="button",
                        on_click=GamesState.close_create_sheet,
                        aria_label="Fermer",
                        class_name=(
                            "flex size-8 items-center justify-center "
                            "rounded-lg border border-slate-200 "
                            "text-slate-500 hover:text-[#071A33]"
                        ),
                    ),
                    class_name=(
                        "flex items-center gap-3 border-b border-slate-200 "
                        "px-4 py-3"
                    ),
                ),
                rx.el.div(
                    rx.el.div(
                        label("Nom de la salle"),
                        rx.el.input(
                            placeholder="Ma salle TATA",
                            default_value=GamesState.gen_name,
                            on_change=GamesState.set_gen_name.debounce(300),
                            aria_label="Nom de la salle",
                            class_name=INPUT,
                        ),
                    ),
                    privacy_selector(),
                    rx.el.div(
                        label("Joueurs"),
                        rx.el.div(
                            rx.foreach(
                                GamesState.create_player_options, player_chip
                            ),
                            class_name="mt-1 flex flex-wrap gap-2",
                        ),
                    ),
                    rx.cond(
                        GamesState.is_loto,
                        rx.el.div(
                            label("Palier du carton"),
                            rx.el.div(
                                rx.foreach(GamesState.tier_options, tier_row),
                                class_name="mt-1 flex flex-col gap-2",
                            ),
                            rx.el.p(
                                "1 a 5 cartons par joueur. Denomination de "
                                "palier en jeu: debit en points internes, "
                                "aucun depot, aucun retrait, aucune valeur "
                                "monetaire, aucune conversion.",
                                class_name=(
                                    "mt-2 text-[10px] leading-relaxed "
                                    "text-slate-500"
                                ),
                            ),
                        ),
                        rx.el.div(
                            rx.el.p(
                                "Ludo standard: quatre pions par joueur, "
                                "victoire quand les quatre atteignent la "
                                "maison.",
                                class_name=(
                                    "rounded-lg border border-slate-200 "
                                    "bg-slate-50 px-3 py-2 text-[11px] "
                                    "font-semibold text-slate-600"
                                ),
                            ),
                            rx.el.div(
                                label("Mise (points internes)"),
                                rx.el.input(
                                    type="text",
                                    input_mode="numeric",
                                    default_value=GamesState.gen_entry,
                                    on_change=GamesState.set_gen_entry.debounce(
                                        300
                                    ),
                                    aria_label="Mise en points internes",
                                    class_name=INPUT,
                                ),
                                class_name="mt-3",
                            ),
                        ),
                    ),
                    rx.cond(
                        GamesState.create_error != "",
                        rx.el.div(
                            rx.icon(
                                "circle-alert",
                                class_name="h-4 w-4 text-red-500",
                            ),
                            rx.el.p(
                                GamesState.create_error,
                                class_name=(
                                    "text-xs font-semibold text-red-600"
                                ),
                            ),
                            class_name=(
                                "flex items-start gap-2 rounded-lg border "
                                "border-red-200 bg-red-50 px-3 py-2"
                            ),
                        ),
                    ),
                    rx.el.p(
                        "Les points TATA sont internes et virtuels: aucun "
                        "achat, aucun depot, aucun retrait, aucune valeur "
                        "monetaire.",
                        class_name="text-[11px] leading-relaxed text-slate-500",
                    ),
                    class_name=(
                        "flex max-h-[62dvh] flex-col gap-4 overflow-y-auto "
                        "px-4 py-4"
                    ),
                ),
                rx.el.div(
                    rx.el.button(
                        "Annuler",
                        type="button",
                        on_click=GamesState.close_create_sheet,
                        class_name=(
                            "rounded-lg border border-slate-200 bg-white "
                            "px-4 py-2.5 text-[13px] font-bold text-slate-600 "
                            "hover:text-[#071A33]"
                        ),
                    ),
                    rx.el.button(
                        rx.cond(
                            GamesState.create_busy,
                            rx.el.span(
                                rx.icon(
                                    "loader-circle",
                                    class_name="h-4 w-4 animate-spin",
                                ),
                                rx.el.span("Creation..."),
                                class_name=(
                                    "flex items-center justify-center gap-2"
                                ),
                            ),
                            rx.el.span(
                                rx.icon("play", class_name="h-4 w-4"),
                                rx.el.span("Creer et rejoindre"),
                                class_name=(
                                    "flex items-center justify-center gap-2"
                                ),
                            ),
                        ),
                        type="button",
                        disabled=GamesState.create_busy,
                        on_click=GamesState.submit_generic_room,
                        class_name=(
                            "flex-1 rounded-lg bg-[#1E9EF5] px-4 py-2.5 "
                            "text-[13px] font-bold text-white "
                            "hover:bg-[#3FAFFA] disabled:opacity-60"
                        ),
                    ),
                    class_name=(
                        "flex items-center gap-2 border-t border-slate-200 "
                        "bg-white px-4 pt-3 "
                        "pb-[calc(env(safe-area-inset-bottom)+12px)]"
                    ),
                ),
                class_name=(
                    "relative z-10 w-full max-w-md overflow-hidden "
                    "rounded-t-2xl border border-slate-200 border-b-0 "
                    "bg-white sm:rounded-2xl sm:border-b"
                ),
            ),
            class_name=(
                "fixed inset-0 z-50 flex items-end justify-center "
                "font-['Inter'] sm:items-center sm:p-4"
            ),
        ),
    )


def private_join_dialog() -> rx.Component:
    """Focused per-room secret dialog: never a shared global input."""
    return rx.cond(
        GamesState.secret_room_id > 0,
        rx.el.div(
            rx.el.div(
                on_click=GamesState.close_secret_dialog,
                class_name="absolute inset-0 bg-[#071A33]/50",
            ),
            rx.el.div(
                rx.el.div(
                    rx.icon("lock", class_name="h-4 w-4 text-[#1E9EF5]"),
                    rx.el.h2(
                        "Salle privee",
                        class_name="text-sm font-bold text-[#071A33]",
                    ),
                    class_name="flex items-center gap-2",
                ),
                rx.el.p(
                    GamesState.secret_room_name,
                    class_name="mt-1 text-xs font-medium text-slate-500",
                ),
                rx.el.input(
                    placeholder="Code d'acces",
                    default_value=GamesState.room_secret,
                    on_change=GamesState.set_room_secret.debounce(300),
                    aria_label="Code d'acces de la salle privee",
                    class_name=INPUT,
                ),
                rx.el.div(
                    rx.el.button(
                        "Annuler",
                        type="button",
                        on_click=GamesState.close_secret_dialog,
                        class_name=(
                            "rounded-lg border border-slate-200 px-3 py-2 "
                            "text-xs font-bold text-slate-600"
                        ),
                    ),
                    rx.el.button(
                        "Rejoindre",
                        type="button",
                        on_click=GamesState.submit_room_secret,
                        class_name=(
                            "flex-1 rounded-lg bg-[#1E9EF5] px-3 py-2 "
                            "text-xs font-bold text-white hover:bg-[#3FAFFA]"
                        ),
                    ),
                    class_name="mt-3 flex items-center gap-2",
                ),
                class_name=(
                    "relative z-10 w-full max-w-sm rounded-2xl border "
                    "border-slate-200 bg-white p-4"
                ),
            ),
            class_name=(
                "fixed inset-0 z-50 flex items-center justify-center p-4 "
                "font-['Inter']"
            ),
        ),
    )
