"""Dark leaderboard & personal statistics area inside the game hall."""

from __future__ import annotations

import reflex as rx

from app.components.game_shell import dark_page, jewel_tag, medallion
from app.components.ui import avatar
from app.states.leaderboard_state import (
    GameOption,
    LeaderboardState,
    LeaderRow,
)


def _chip(label: str | rx.Var, active: rx.Var | bool, on_click) -> rx.Component:
    return rx.el.button(
        label,
        on_click=on_click,
        aria_pressed=active,
        class_name=rx.cond(
            active,
            "w-fit rounded-full border border-amber-400/60 bg-amber-500/15 "
            "px-3 py-1.5 text-[11px] font-bold uppercase tracking-wide "
            "text-amber-200",
            "w-fit rounded-full border border-zinc-800 bg-[#0A0B0E] px-3 "
            "py-1.5 text-[11px] font-bold uppercase tracking-wide "
            "text-zinc-400 hover:border-zinc-600 hover:text-zinc-200",
        ),
    )


def game_chip(option: GameOption) -> rx.Component:
    return _chip(
        option["name"],
        LeaderboardState.active_game == option["slug"],
        LeaderboardState.set_game_filter(option["slug"]),
    )


def filters() -> rx.Component:
    return rx.el.div(
        rx.el.div(
            rx.el.p(
                "Jeu",
                class_name=(
                    "mb-2 text-[10px] font-bold uppercase tracking-wider "
                    "text-zinc-500"
                ),
            ),
            rx.el.div(
                rx.foreach(LeaderboardState.game_options, game_chip),
                class_name="flex flex-wrap gap-1.5",
            ),
            class_name="min-w-0 flex-1",
        ),
        rx.el.div(
            rx.el.p(
                "Periode",
                class_name=(
                    "mb-2 text-[10px] font-bold uppercase tracking-wider "
                    "text-zinc-500"
                ),
            ),
            rx.el.div(
                _chip(
                    "Toujours",
                    LeaderboardState.active_range == "all",
                    LeaderboardState.set_range_filter("all"),
                ),
                _chip(
                    "30 jours",
                    LeaderboardState.active_range == "30d",
                    LeaderboardState.set_range_filter("30d"),
                ),
                _chip(
                    "7 jours",
                    LeaderboardState.active_range == "7d",
                    LeaderboardState.set_range_filter("7d"),
                ),
                class_name="flex flex-wrap gap-1.5",
            ),
            class_name="min-w-0",
        ),
        class_name=(
            "flex w-full flex-col gap-4 rounded-2xl border border-zinc-800 "
            "bg-[#0C0D10] p-4 sm:flex-row sm:items-start sm:gap-8"
        ),
    )


def stat_tile(
    label: str, value: rx.Var | str, icon: str, tone: str
) -> rx.Component:
    return rx.el.div(
        rx.el.div(
            rx.icon(icon, class_name=f"h-4 w-4 {tone}"),
            rx.el.span(
                label,
                class_name=(
                    "text-[10px] font-bold uppercase tracking-wider "
                    "text-zinc-500"
                ),
            ),
            class_name="flex items-center gap-1.5",
        ),
        rx.el.p(
            value,
            class_name=(
                "mt-2 text-2xl font-black tabular-nums tracking-tight "
                "text-white"
            ),
        ),
        class_name=(
            "w-full rounded-2xl border border-zinc-800 "
            "bg-[linear-gradient(160deg,#111317,#0A0B0E)] p-4"
        ),
    )


def personal_panel() -> rx.Component:
    return rx.el.div(
        rx.el.div(
            stat_tile(
                "Parties",
                LeaderboardState.my_games.to_string(),
                "gamepad-2",
                "text-cyan-300",
            ),
            stat_tile(
                "Victoires",
                LeaderboardState.my_wins.to_string(),
                "trophy",
                "text-emerald-400",
            ),
            stat_tile(
                "Defaites",
                LeaderboardState.my_losses.to_string(),
                "circle-x",
                "text-rose-400",
            ),
            stat_tile(
                "Taux de victoire",
                LeaderboardState.my_win_rate_display,
                "percent",
                "text-amber-300",
            ),
            class_name="grid w-full grid-cols-2 gap-3 md:grid-cols-4",
        ),
        rx.el.div(
            rx.el.div(
                medallion("crown", "size-11"),
                rx.el.div(
                    rx.el.p(
                        "Jeu favori",
                        class_name=(
                            "text-[10px] font-bold uppercase tracking-wider "
                            "text-zinc-500"
                        ),
                    ),
                    rx.el.p(
                        LeaderboardState.my_favorite_game,
                        class_name="text-sm font-bold text-white",
                    ),
                    class_name="min-w-0",
                ),
                class_name="flex items-center gap-3",
            ),
            rx.el.div(
                jewel_tag(LeaderboardState.rank_context, "emerald"),
                jewel_tag(LeaderboardState.game_label, "violet"),
                jewel_tag(LeaderboardState.range_label, "cyan"),
                class_name="flex flex-wrap gap-1.5",
            ),
            class_name=(
                "mt-3 flex w-full flex-col gap-3 rounded-2xl border "
                "border-zinc-800 bg-[#0C0D10] p-4 sm:flex-row "
                "sm:items-center sm:justify-between"
            ),
        ),
        rx.cond(
            LeaderboardState.has_personal_history,
            rx.fragment(),
            rx.el.p(
                "Vous n'avez encore termine aucune partie avec ces filtres. "
                "Jouez une partie complete pour apparaitre au classement.",
                class_name="mt-3 text-xs text-zinc-500",
            ),
        ),
        class_name="w-full",
    )


def _podium_card(row: LeaderRow, place: int) -> rx.Component:
    return rx.el.div(
        rx.el.div(
            rx.el.span(
                f"#{place}",
                class_name=rx.match(
                    place,
                    (
                        1,
                        "text-xs font-black text-[#3B2606] bg-[linear-gradient"
                        "(140deg,#FFF3CB,#E7B53C)] rounded-full px-2 py-0.5",
                    ),
                    (
                        2,
                        "text-xs font-black text-[#1A1D22] bg-[linear-gradient"
                        "(140deg,#F2F4F7,#B9C0CA)] rounded-full px-2 py-0.5",
                    ),
                    "text-xs font-black text-[#2A1608] bg-[linear-gradient"
                    "(140deg,#F0C39A,#B0743C)] rounded-full px-2 py-0.5",
                ),
            ),
            class_name="flex justify-center",
        ),
        avatar(
            row["avatar_url"],
            row["avatar_remote"],
            rx.match(
                place,
                (1, "size-20 ring-2 ring-amber-400"),
                (2, "size-16 ring-2 ring-zinc-300"),
                "size-16 ring-2 ring-amber-700",
            ),
        ),
        rx.el.p(
            row["display_name"],
            class_name="line-clamp-1 text-sm font-bold text-white",
        ),
        rx.el.p(
            f"@{row['username']}",
            class_name="line-clamp-1 text-[11px] text-zinc-500",
        ),
        rx.el.div(
            rx.el.span(
                f"{row['wins']} V",
                class_name="text-xs font-black text-emerald-400",
            ),
            rx.el.span("•", class_name="text-xs text-zinc-700"),
            rx.el.span(
                row["win_rate_display"],
                class_name="text-xs font-bold text-amber-300",
            ),
            class_name="flex items-center gap-2",
        ),
        rx.el.p(
            f"{row['games']} parties",
            class_name="text-[11px] text-zinc-500",
        ),
        class_name=rx.cond(
            place == 1,
            "flex w-full flex-col items-center gap-2 rounded-2xl border "
            "border-amber-400/40 bg-[linear-gradient(170deg,#1A1608,#0A0B0E)] "
            "p-4 sm:order-2 sm:-mt-4",
            rx.cond(
                place == 2,
                "flex w-full flex-col items-center gap-2 rounded-2xl border "
                "border-zinc-600/60 bg-[linear-gradient(170deg,#15171B,"
                "#0A0B0E)] p-4 sm:order-1",
                "flex w-full flex-col items-center gap-2 rounded-2xl border "
                "border-amber-800/60 bg-[linear-gradient(170deg,#171208,"
                "#0A0B0E)] p-4 sm:order-3",
            ),
        ),
    )


def podium() -> rx.Component:
    return rx.el.div(
        rx.el.h2(
            "Podium",
            class_name=(
                "mb-3 text-xs font-bold uppercase tracking-wider text-zinc-400"
            ),
        ),
        rx.el.div(
            rx.foreach(
                LeaderboardState.podium,
                lambda row: _podium_card(row, row["rank"]),
            ),
            class_name=(
                "grid w-full grid-cols-1 items-end gap-3 sm:grid-cols-3"
            ),
        ),
        class_name="w-full",
    )


def _rank_badge(row: LeaderRow) -> rx.Component:
    return rx.el.span(
        f"#{row['rank']}",
        class_name=rx.match(
            row["rank"],
            (1, "text-sm font-black text-amber-300 tabular-nums"),
            (2, "text-sm font-black text-zinc-200 tabular-nums"),
            (3, "text-sm font-black text-amber-600 tabular-nums"),
            "text-sm font-black text-zinc-500 tabular-nums",
        ),
    )


def rank_row(row: LeaderRow) -> rx.Component:
    return rx.el.tr(
        rx.el.td(
            _rank_badge(row),
            class_name="px-3 py-2 align-middle",
        ),
        rx.el.td(
            rx.el.div(
                avatar(row["avatar_url"], row["avatar_remote"], "size-8"),
                rx.el.div(
                    rx.el.p(
                        row["display_name"],
                        class_name=(
                            "line-clamp-1 text-xs font-bold text-white"
                        ),
                    ),
                    rx.el.p(
                        f"@{row['username']}",
                        class_name="line-clamp-1 text-[10px] text-zinc-500",
                    ),
                    class_name="min-w-0",
                ),
                rx.cond(
                    row["is_me"],
                    rx.el.span(
                        "Moi",
                        class_name=(
                            "w-fit rounded-full bg-emerald-500/15 px-2 py-0.5 "
                            "text-[10px] font-bold uppercase text-emerald-300"
                        ),
                    ),
                    rx.fragment(),
                ),
                class_name="flex min-w-0 items-center gap-2",
            ),
            class_name="px-3 py-2 align-middle",
        ),
        rx.el.td(
            rx.el.span(
                row["favorite_game"],
                class_name="text-[11px] text-zinc-400",
            ),
            class_name="hidden px-3 py-2 align-middle sm:table-cell",
        ),
        rx.el.td(
            rx.el.span(
                row["games"],
                class_name="text-xs font-semibold tabular-nums text-zinc-300",
            ),
            class_name="px-3 py-2 text-right align-middle",
        ),
        rx.el.td(
            rx.el.span(
                row["wins"],
                class_name=("text-xs font-black tabular-nums text-emerald-400"),
            ),
            class_name="px-3 py-2 text-right align-middle",
        ),
        rx.el.td(
            rx.el.span(
                row["losses"],
                class_name="text-xs font-semibold tabular-nums text-rose-400",
            ),
            class_name="hidden px-3 py-2 text-right align-middle sm:table-cell",
        ),
        rx.el.td(
            rx.el.span(
                row["win_rate_display"],
                class_name="text-xs font-bold tabular-nums text-amber-300",
            ),
            class_name="px-3 py-2 text-right align-middle",
        ),
        class_name=rx.cond(
            row["is_me"],
            "border-l-2 border-emerald-500 bg-emerald-500/5",
            "border-l-2 border-transparent hover:bg-white/[0.03]",
        ),
    )


def _th(label: str, extra: str = "") -> rx.Component:
    return rx.el.th(
        label,
        scope="col",
        class_name=(
            "px-3 py-2 text-left text-[10px] font-bold uppercase "
            "tracking-wider text-zinc-500 " + extra
        ),
    )


def rank_table() -> rx.Component:
    return rx.el.div(
        rx.el.h2(
            "Classement complet",
            class_name=(
                "mb-3 text-xs font-bold uppercase tracking-wider text-zinc-400"
            ),
        ),
        rx.el.div(
            rx.el.table(
                rx.el.caption(
                    "Classement calcule uniquement a partir des parties "
                    "terminees. Points internes uniquement.",
                    class_name="sr-only",
                ),
                rx.el.thead(
                    rx.el.tr(
                        _th("Rang"),
                        _th("Joueur"),
                        _th("Favori", "hidden sm:table-cell"),
                        _th("Parties", "text-right"),
                        _th("V", "text-right"),
                        _th("D", "hidden sm:table-cell text-right"),
                        _th("Taux", "text-right"),
                        class_name="border-b border-zinc-800",
                    ),
                ),
                rx.el.tbody(
                    rx.foreach(LeaderboardState.rows, rank_row),
                    class_name="divide-y divide-zinc-900",
                ),
                class_name="w-full table-auto",
            ),
            class_name=(
                "w-full overflow-hidden rounded-2xl border border-zinc-800 "
                "bg-[#0C0D10]"
            ),
        ),
        class_name="w-full",
    )


def skeleton() -> rx.Component:
    return rx.el.div(
        rx.el.div(class_name="h-24 animate-pulse rounded-2xl bg-zinc-900"),
        rx.el.div(class_name="h-40 animate-pulse rounded-2xl bg-zinc-900"),
        rx.el.div(class_name="h-64 animate-pulse rounded-2xl bg-zinc-900"),
        class_name="flex w-full flex-col gap-4",
    )


def empty_state() -> rx.Component:
    return rx.el.div(
        medallion("trophy", "size-16"),
        rx.el.p(
            "Aucune partie terminee pour ces filtres",
            class_name="mt-3 text-sm font-bold text-white",
        ),
        rx.el.p(
            "Le classement apparait des qu'une partie se termine avec un "
            "vainqueur. Rien n'est simule ici.",
            class_name="mt-1 max-w-md text-xs text-zinc-500",
        ),
        rx.el.a(
            "Aller a la salle de jeux",
            href="/games",
            class_name=(
                "mt-4 rounded-xl bg-emerald-500 px-4 py-2 text-xs font-black "
                "tracking-wider text-black hover:bg-emerald-400"
            ),
        ),
        class_name=(
            "flex w-full flex-col items-center rounded-2xl border border-dashed "
            "border-zinc-800 bg-[#0C0D10] p-8 text-center"
        ),
    )


def leaderboard_body() -> rx.Component:
    return rx.el.div(
        rx.el.div(
            rx.el.h1(
                "Classement TATA",
                class_name="text-xl font-black tracking-tight text-white",
            ),
            rx.el.p(
                "Statistiques et classement calcules uniquement sur les "
                "parties terminees. Points internes uniquement, aucune "
                "valeur monetaire.",
                class_name="mt-1 max-w-2xl text-xs text-zinc-500",
            ),
            class_name="w-full",
        ),
        filters(),
        rx.cond(
            LeaderboardState.error != "",
            rx.el.p(
                LeaderboardState.error,
                class_name="text-sm font-semibold text-rose-400",
            ),
            rx.fragment(),
        ),
        rx.cond(
            LeaderboardState.loading,
            skeleton(),
            rx.el.div(
                personal_panel(),
                rx.cond(
                    LeaderboardState.has_rows,
                    rx.el.div(
                        podium(),
                        rank_table(),
                        class_name="flex w-full flex-col gap-5",
                    ),
                    empty_state(),
                ),
                class_name="flex w-full flex-col gap-5",
            ),
        ),
        class_name="flex w-full flex-col gap-5",
    )


def leaderboard_page() -> rx.Component:
    return dark_page("Classement", leaderboard_body(), "jeux", "/games")
