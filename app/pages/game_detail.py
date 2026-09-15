"""Bright TATA game detail + room discovery for Domino, Ludo and Loto."""

from __future__ import annotations

import reflex as rx

from app.components.bright_shell import bright_page
from app.components.domino_create import create_game_modal
from app.components.room_create import create_room_sheet, private_join_dialog
from app.states.games_state import GamesState, RoomRow


def pill(text_var, tone: str) -> rx.Component:
    tones = {
        "sky": "border-[#1E9EF5]/40 bg-[#EAF6FE] text-[#0B4F86]",
        "cyan": "border-[#22D3EE]/40 bg-[#ECFEFF] text-[#0E7490]",
        "navy": "border-[#071A33]/15 bg-[#F1F5FB] text-[#071A33]",
        "gold": "border-amber-300 bg-amber-50 text-amber-700",
        "slate": "border-slate-200 bg-slate-50 text-slate-600",
    }
    return rx.el.span(
        text_var,
        class_name=(
            "w-fit rounded-md border px-2 py-0.5 text-[11px] font-bold "
            f"{tones.get(tone, tones['slate'])}"
        ),
    )


def metric(icon: str, value, label: str) -> rx.Component:
    return rx.el.div(
        rx.icon(icon, class_name="h-4 w-4 text-[#1E9EF5]"),
        rx.el.div(
            rx.el.p(
                value,
                class_name="text-sm font-bold leading-none text-[#071A33]",
            ),
            rx.el.p(
                label,
                class_name="mt-1 text-[10px] font-semibold text-slate-500",
            ),
            class_name="min-w-0",
        ),
        class_name=(
            "flex w-full items-center gap-2 rounded-lg border "
            "border-slate-200 bg-white px-3 py-2"
        ),
    )


def preview_panel() -> rx.Component:
    return rx.el.div(
        rx.el.div(
            rx.image(
                src=GamesState.detail_cover,
                alt=GamesState.active_game_name,
                class_name="h-full w-full object-contain",
            ),
            class_name=(
                "flex h-48 w-full items-center justify-center rounded-lg "
                "bg-[#0B2647] p-3 sm:h-64"
            ),
        ),
        rx.el.div(
            rx.el.h1(
                GamesState.active_game_name,
                class_name="text-xl font-bold tracking-tight text-white",
            ),
            rx.el.p(
                GamesState.detail_overview,
                class_name="mt-1 text-xs leading-relaxed text-slate-300",
            ),
            rx.el.div(
                rx.cond(
                    GamesState.open_room_count > 0,
                    rx.el.span(
                        rx.el.span(
                            class_name=(
                                "size-2 rounded-full bg-[#22D3EE] animate-pulse"
                            )
                        ),
                        rx.el.span(
                            f"{GamesState.open_room_count} salle(s) ouverte(s)",
                            class_name="text-[11px] font-bold text-[#22D3EE]",
                        ),
                        class_name="flex items-center gap-1.5",
                    ),
                    rx.el.span(
                        "Aucune salle ouverte",
                        class_name="text-[11px] font-bold text-slate-400",
                    ),
                ),
                rx.el.span(
                    f"{GamesState.live_player_count} joueur(s) en salle",
                    class_name="text-[11px] font-semibold text-slate-400",
                ),
                class_name="mt-3 flex flex-wrap items-center gap-3",
            ),
            class_name="mt-3",
        ),
        class_name="rounded-2xl border border-[#0B2647] bg-[#071A33] p-4",
    )


def action_bar() -> rx.Component:
    return rx.el.div(
        rx.el.button(
            rx.cond(
                GamesState.quick_playing,
                rx.icon("loader-circle", class_name="h-4 w-4 animate-spin"),
                rx.icon("zap", class_name="h-4 w-4"),
            ),
            rx.el.span("Quick Play"),
            on_click=GamesState.quick_play,
            disabled=GamesState.quick_playing,
            class_name=(
                "flex flex-1 items-center justify-center gap-2 rounded-lg "
                "bg-[#1E9EF5] px-4 py-2.5 text-sm font-bold text-white "
                "hover:bg-[#3FAFFA] disabled:opacity-60"
            ),
        ),
        rx.el.button(
            rx.icon("plus", class_name="h-4 w-4"),
            rx.el.span("Creer une salle"),
            on_click=rx.cond(
                GamesState.is_domino,
                GamesState.open_domino_sheet,
                GamesState.open_create_sheet,
            ),
            class_name=(
                "flex flex-1 items-center justify-center gap-2 rounded-lg "
                "border border-[#1E9EF5] bg-white px-4 py-2.5 text-sm "
                "font-bold text-[#0B4F86] hover:bg-[#F5FAFF]"
            ),
        ),
        class_name="flex flex-col gap-2 sm:flex-row",
    )


def join_by_code() -> rx.Component:
    return rx.el.div(
        rx.el.div(
            rx.icon("key-round", class_name="h-4 w-4 text-[#1E9EF5]"),
            rx.el.p(
                "Rejoindre avec un code",
                class_name="text-xs font-bold text-[#071A33]",
            ),
            class_name="flex items-center gap-2",
        ),
        rx.el.div(
            rx.el.input(
                placeholder="Code de salle",
                default_value=GamesState.join_code,
                on_change=GamesState.set_join_code.debounce(300),
                aria_label="Code de salle",
                class_name=(
                    "flex-1 rounded-lg border border-slate-200 bg-white "
                    "px-3 py-2 text-sm font-semibold uppercase "
                    "text-[#071A33] outline-hidden "
                    "placeholder:text-slate-400 focus:border-[#1E9EF5]"
                ),
            ),
            rx.el.button(
                "Rejoindre",
                on_click=GamesState.join_by_code,
                class_name=(
                    "rounded-lg bg-[#071A33] px-4 py-2 text-xs font-bold "
                    "text-white hover:bg-[#0B2647]"
                ),
            ),
            class_name="mt-2 flex items-center gap-2",
        ),
        rx.cond(
            GamesState.error != "",
            rx.el.p(
                GamesState.error,
                class_name="mt-2 text-[11px] font-semibold text-red-600",
            ),
        ),
        class_name="rounded-2xl border border-slate-200 bg-white p-4",
    )


def rules_line(line: str) -> rx.Component:
    return rx.el.li(
        rx.icon(
            "check", class_name="mt-0.5 h-3.5 w-3.5 shrink-0 text-[#1E9EF5]"
        ),
        rx.el.span(line, class_name="text-xs leading-relaxed text-slate-700"),
        class_name="flex items-start gap-2",
    )


def howto_line(line: str, index: int) -> rx.Component:
    return rx.el.li(
        rx.el.span(
            (index + 1).to_string(),
            class_name=(
                "flex size-5 shrink-0 items-center justify-center "
                "rounded-md bg-[#ECFEFF] text-[10px] font-bold "
                "text-[#0E7490]"
            ),
        ),
        rx.el.span(line, class_name="text-xs leading-relaxed text-slate-700"),
        class_name="flex items-start gap-2",
    )


def tab_button(label: str, value: str, active) -> rx.Component:
    return rx.el.button(
        label,
        on_click=lambda: GamesState.set_panel_tab(value),
        aria_pressed=active,
        class_name=rx.cond(
            active,
            "rounded-lg border border-[#1E9EF5] bg-[#EAF6FE] px-3 py-1.5 "
            "text-xs font-bold text-[#0B4F86]",
            "rounded-lg border border-slate-200 bg-white px-3 py-1.5 "
            "text-xs font-bold text-slate-600 hover:border-[#1E9EF5]/60",
        ),
    )


def rules_panel() -> rx.Component:
    return rx.el.section(
        rx.el.div(
            tab_button("Regles", "rules", GamesState.showing_rules),
            tab_button("Comment jouer", "howto", ~GamesState.showing_rules),
            class_name="flex items-center gap-2",
        ),
        rx.el.div(class_name="my-3 h-px w-full bg-slate-200"),
        rx.cond(
            GamesState.showing_rules,
            rx.el.ul(
                rx.foreach(GamesState.detail_rules_list, rules_line),
                class_name="flex flex-col gap-2",
            ),
            rx.el.ol(
                rx.foreach(
                    GamesState.detail_howto_list,
                    lambda line, index: howto_line(line, index),
                ),
                class_name="flex flex-col gap-2",
            ),
        ),
        class_name="rounded-2xl border border-slate-200 bg-white p-4",
    )


def room_card(room: RoomRow) -> rx.Component:
    return rx.el.div(
        rx.el.div(
            rx.el.div(
                rx.el.p(
                    room["name"],
                    class_name="truncate text-sm font-bold text-[#071A33]",
                ),
                rx.el.div(
                    rx.el.span(
                        f"Hote {room['host_name']}",
                        class_name="text-[11px] font-medium text-slate-500",
                    ),
                    rx.cond(
                        room["host_online"],
                        rx.el.span(
                            rx.el.span(
                                class_name="size-2 rounded-full bg-[#22D3EE]"
                            ),
                            rx.el.span(
                                "en ligne",
                                class_name=(
                                    "text-[10px] font-bold text-[#0E7490]"
                                ),
                            ),
                            class_name="flex items-center gap-1",
                        ),
                        rx.el.span(
                            "hors ligne",
                            class_name="text-[10px] font-bold text-slate-400",
                        ),
                    ),
                    class_name="mt-0.5 flex items-center gap-2",
                ),
                class_name="min-w-0 flex-1",
            ),
            rx.el.button(
                rx.icon("copy", class_name="h-3.5 w-3.5"),
                rx.el.span(
                    room["code"],
                    class_name="text-[11px] font-bold tracking-wider",
                ),
                on_click=lambda: GamesState.copy_code(room["code"]),
                title="Copier le code de la salle",
                aria_label="Copier le code de la salle",
                class_name=(
                    "flex shrink-0 items-center gap-1.5 rounded-md border "
                    "border-slate-200 bg-[#F7FBFF] px-2 py-1 text-slate-600 "
                    "hover:border-[#1E9EF5]/60 hover:text-[#0B4F86]"
                ),
            ),
            class_name="flex items-start gap-2",
        ),
        rx.el.div(
            pill(room["status_label"], "sky"),
            rx.cond(
                room["is_private"],
                pill("Privee", "navy"),
                pill("Publique", "cyan"),
            ),
            rx.cond(
                room["tier_label"] != "",
                pill(room["tier_label"], "gold"),
                rx.fragment(),
            ),
            class_name="mt-3 flex flex-wrap gap-1.5",
        ),
        rx.el.div(class_name="my-3 h-px w-full bg-slate-100"),
        rx.el.div(
            rx.el.div(
                rx.el.p(
                    f"{room['player_count']}/{room['max_players']} joueurs",
                    class_name="text-[11px] font-bold text-[#071A33]",
                ),
                rx.el.p(
                    f"Salle #{room['id']}",
                    class_name="text-[10px] font-medium text-slate-500",
                ),
                class_name="min-w-0",
            ),
            rx.cond(
                room["is_private"] & ~room["joined"],
                rx.el.button(
                    rx.icon("lock", class_name="h-3.5 w-3.5"),
                    rx.el.span("Code"),
                    on_click=lambda: GamesState.open_secret_dialog(
                        room["id"], room["name"]
                    ),
                    disabled=room["full"],
                    class_name=(
                        "flex items-center gap-1.5 rounded-lg bg-[#071A33] "
                        "px-3 py-1.5 text-xs font-bold text-white "
                        "hover:bg-[#0B2647] disabled:opacity-40"
                    ),
                ),
                rx.el.button(
                    rx.cond(room["joined"], "Reprendre", "Rejoindre"),
                    on_click=lambda: GamesState.join_room(room["id"], ""),
                    disabled=room["full"] & ~room["joined"],
                    class_name=(
                        "rounded-lg bg-[#1E9EF5] px-4 py-1.5 text-xs "
                        "font-bold text-white hover:bg-[#3FAFFA] "
                        "disabled:opacity-40"
                    ),
                ),
            ),
            class_name="flex items-center justify-between gap-2",
        ),
        class_name="rounded-2xl border border-slate-200 bg-white p-4",
    )


def filter_chip(item: dict[str, str]) -> rx.Component:
    return rx.el.button(
        item["label"],
        on_click=lambda: GamesState.set_status_filter(item["value"]),
        class_name=rx.cond(
            GamesState.status_filter == item["value"],
            "rounded-lg border border-[#1E9EF5] bg-[#EAF6FE] px-3 py-1.5 "
            "text-xs font-bold text-[#0B4F86]",
            "rounded-lg border border-slate-200 bg-white px-3 py-1.5 "
            "text-xs font-bold text-slate-600 hover:border-[#1E9EF5]/60",
        ),
    )


def rooms_section() -> rx.Component:
    return rx.el.section(
        rx.el.div(
            rx.el.h2(
                "Salles disponibles",
                class_name="text-sm font-bold text-[#071A33]",
            ),
            rx.el.div(
                rx.foreach(GamesState.status_filters, filter_chip),
                class_name="flex flex-wrap gap-2",
            ),
            class_name=(
                "flex flex-col gap-2 sm:flex-row sm:items-center "
                "sm:justify-between"
            ),
        ),
        rx.cond(
            GamesState.loading,
            rx.el.div(
                rx.el.div(
                    class_name=(
                        "h-40 animate-pulse rounded-2xl border "
                        "border-slate-200 bg-slate-100"
                    )
                ),
                rx.el.div(
                    class_name=(
                        "h-40 animate-pulse rounded-2xl border "
                        "border-slate-200 bg-slate-100"
                    )
                ),
                class_name="mt-3 grid gap-3 sm:grid-cols-2",
            ),
            rx.cond(
                GamesState.visible_rooms.length() > 0,
                rx.el.div(
                    rx.foreach(GamesState.visible_rooms, room_card),
                    class_name="mt-3 grid gap-3 sm:grid-cols-2",
                ),
                rx.el.div(
                    rx.icon("door-open", class_name="h-7 w-7 text-slate-300"),
                    rx.el.p(
                        "Aucune salle pour ce filtre.",
                        class_name="mt-2 text-sm font-semibold text-slate-600",
                    ),
                    rx.el.p(
                        "Lancez Quick Play ou creez la premiere salle.",
                        class_name="text-xs text-slate-500",
                    ),
                    class_name=(
                        "mt-3 flex flex-col items-center justify-center "
                        "rounded-2xl border border-dashed border-slate-300 "
                        "bg-white py-12"
                    ),
                ),
            ),
        ),
        class_name="w-full",
    )


def unavailable_state() -> rx.Component:
    return rx.el.div(
        rx.icon("triangle-alert", class_name="h-8 w-8 text-slate-300"),
        rx.el.p(
            "Ce jeu n'est pas disponible.",
            class_name="mt-2 text-sm font-bold text-[#071A33]",
        ),
        rx.el.p(
            "Seuls Domino, Ludo et Loto sont proposes.",
            class_name="text-xs text-slate-500",
        ),
        rx.el.a(
            "Retour aux jeux",
            href="/games",
            class_name=(
                "mt-3 rounded-lg bg-[#1E9EF5] px-4 py-2 text-xs font-bold "
                "text-white hover:bg-[#3FAFFA]"
            ),
        ),
        class_name=(
            "flex flex-col items-center justify-center rounded-2xl border "
            "border-slate-200 bg-white py-16"
        ),
    )


def detail_body() -> rx.Component:
    return rx.el.div(
        rx.el.a(
            rx.icon("chevron-left", class_name="h-4 w-4"),
            rx.el.span("Retour aux jeux"),
            href="/games",
            class_name=(
                "flex w-fit items-center gap-1.5 rounded-lg border "
                "border-slate-200 bg-white px-3 py-1.5 text-xs font-bold "
                "text-[#071A33] hover:border-[#1E9EF5]/60"
            ),
        ),
        rx.el.div(
            rx.el.div(
                preview_panel(),
                class_name="w-full lg:w-1/2",
            ),
            rx.el.div(
                rx.el.div(
                    metric("users", GamesState.detail_player_range, "Joueurs"),
                    metric("gamepad-2", GamesState.detail_mode, "Mode"),
                    metric(
                        "door-open",
                        GamesState.open_room_count.to_string(),
                        "Salles ouvertes",
                    ),
                    class_name="grid w-full grid-cols-2 gap-2",
                ),
                action_bar(),
                join_by_code(),
                class_name="flex w-full flex-col gap-3 lg:w-1/2",
            ),
            class_name="flex flex-col gap-3 lg:flex-row",
        ),
        rules_panel(),
        rooms_section(),
        create_room_sheet(),
        private_join_dialog(),
        rx.cond(GamesState.is_domino, create_game_modal(), rx.fragment()),
        class_name="flex w-full flex-col gap-4",
    )


def game_detail_page() -> rx.Component:
    return bright_page(
        rx.cond(GamesState.slug_valid, detail_body(), unavailable_state()),
        "jeux",
    )
