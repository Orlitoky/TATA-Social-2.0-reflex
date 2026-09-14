"""Shared TATA waiting lobby for Domino, Ludo and Loto.

Dark-navy table surface (#071A33 / #0B2647) nested inside the bright TATA
journey: sky/cyan controls, emerald ready signals, red removal/disconnect,
a touch of warm gold reserved for host and pot. Points are internal and
virtual: no deposit, no withdrawal, no monetary value.
"""

from __future__ import annotations

import reflex as rx

from app.components.boards import loto_controls
from app.components.ui import avatar
from app.states.room_state import LobbySlot, RoomState

CARD = "rounded-xl border border-[#123A63] bg-[#0B2647]"
SUBTLE = "text-[10px] font-bold uppercase tracking-[0.16em] text-slate-400"

TONES = {
    "sky": "border-sky-400/35 bg-sky-500/10 text-sky-200",
    "cyan": "border-cyan-400/35 bg-cyan-500/10 text-cyan-200",
    "emerald": "border-emerald-400/40 bg-emerald-500/10 text-emerald-200",
    "rose": "border-rose-400/40 bg-rose-500/10 text-rose-200",
    "gold": "border-amber-400/35 bg-amber-500/10 text-amber-200",
    "slate": "border-[#1C4576] bg-[#0E2F52] text-slate-300",
}


def chip(label: str | rx.Var, tone: str = "sky") -> rx.Component:
    return rx.el.span(
        label,
        class_name=(
            "w-fit rounded-md border px-2 py-0.5 text-[11px] font-bold "
            "tracking-tight " + TONES.get(tone, TONES["sky"])
        ),
    )


# --------------------------------------------------------------- connection
def connection_chip() -> rx.Component:
    return rx.match(
        RoomState.connection_state,
        ("live", chip("● En direct", "cyan")),
        ("connecting", chip("○ Connexion...", "slate")),
        ("paused", chip("‖ Synchro en pause", "slate")),
        ("removed", chip("✕ Hors de la salle", "rose")),
        chip("✕ Connexion perdue", "rose"),
    )


def connection_banner() -> rx.Component:
    return rx.cond(
        RoomState.error != "",
        rx.el.div(
            rx.icon("wifi-off", class_name="h-4 w-4 shrink-0 text-rose-300"),
            rx.el.p(
                RoomState.error,
                class_name="min-w-0 flex-1 text-[11px] font-semibold text-rose-200",
            ),
            rx.el.button(
                rx.icon("refresh-cw", class_name="h-3.5 w-3.5"),
                "Reessayer",
                on_click=RoomState.manual_refresh,
                class_name=(
                    "flex shrink-0 items-center gap-1 rounded-md border "
                    "border-rose-400/50 px-2 py-1 text-[11px] font-bold "
                    "text-rose-100 hover:bg-rose-500/15 "
                    "focus:outline-hidden focus:ring-2 focus:ring-rose-400/60"
                ),
            ),
            class_name=(
                "flex items-center gap-2 rounded-xl border "
                "border-rose-500/40 bg-rose-500/5 p-2.5"
            ),
        ),
        rx.fragment(),
    )


# ------------------------------------------------------------------- header
def lobby_header() -> rx.Component:
    return rx.el.div(
        rx.el.div(
            rx.el.div(
                rx.el.h1(
                    RoomState.game_name,
                    class_name=(
                        "truncate text-lg font-black tracking-tight text-white"
                    ),
                ),
                rx.el.p(
                    RoomState.room_name,
                    class_name="truncate text-[11px] font-medium text-slate-400",
                ),
                class_name="min-w-0 flex-1",
            ),
            connection_chip(),
            class_name="flex items-start gap-2",
        ),
        rx.el.div(
            rx.el.div(
                rx.el.p("Code de la salle", class_name=SUBTLE),
                rx.el.p(
                    RoomState.code,
                    class_name=(
                        "font-mono text-lg font-black tracking-[0.18em] "
                        "text-amber-200"
                    ),
                ),
                rx.el.p(
                    f"Salle #{RoomState.active_id}",
                    class_name="text-[10px] font-semibold text-slate-500",
                ),
                class_name="min-w-0 flex-1",
            ),
            rx.el.div(
                rx.el.button(
                    rx.icon("copy", class_name="h-4 w-4"),
                    "Copier",
                    on_click=RoomState.copy_code,
                    class_name=(
                        "flex items-center gap-1.5 rounded-lg border "
                        "border-sky-400/40 bg-[#0C2C4B] px-3 py-2 "
                        "text-[11px] font-bold text-sky-100 "
                        "hover:bg-sky-500/15 active:scale-[0.98] "
                        "focus:outline-hidden focus:ring-2 "
                        "focus:ring-sky-400/60"
                    ),
                ),
                rx.el.button(
                    rx.icon("share-2", class_name="h-4 w-4"),
                    "Inviter",
                    on_click=RoomState.invite_players,
                    class_name=(
                        "flex items-center gap-1.5 rounded-lg border "
                        "border-cyan-400/40 bg-[#082B3F] px-3 py-2 "
                        "text-[11px] font-bold text-cyan-100 "
                        "hover:bg-cyan-500/15 active:scale-[0.98] "
                        "focus:outline-hidden focus:ring-2 "
                        "focus:ring-cyan-400/60"
                    ),
                ),
                class_name="flex shrink-0 gap-2",
            ),
            class_name=(
                "mt-3 flex items-end gap-2 border-t border-[#123A63] pt-3"
            ),
        ),
        rx.el.div(
            rx.cond(
                RoomState.is_private,
                chip("Privee", "gold"),
                chip("Publique", "sky"),
            ),
            chip(
                f"{RoomState.lobby_occupied}/{RoomState.lobby_target_players} "
                "sieges",
                "cyan",
            ),
            chip(f"Mise {RoomState.entry_coins} pts", "slate"),
            chip(f"Pot {RoomState.pot_coins} pts", "gold"),
            chip(RoomState.status_label, "slate"),
            class_name="mt-3 flex flex-wrap gap-1.5",
        ),
        class_name=CARD + " p-3",
    )


# --------------------------------------------------------------- seat pieces
def seat_puck(slot: LobbySlot) -> rx.Component:
    """Compact seat token used inside the table geometry."""
    return rx.el.div(
        rx.el.div(
            rx.match(
                slot["kind"],
                (
                    "player",
                    avatar(
                        slot["avatar_url"], slot["avatar_remote"], "size-10"
                    ),
                ),
                (
                    "bot",
                    rx.el.div(
                        rx.icon("bot", class_name="h-4 w-4 text-cyan-200"),
                        class_name=(
                            "flex size-10 items-center justify-center "
                            "rounded-full border border-cyan-400/40 "
                            "bg-cyan-500/10"
                        ),
                    ),
                ),
                rx.el.div(
                    rx.icon("user-plus", class_name="h-4 w-4 text-slate-500"),
                    class_name=(
                        "flex size-10 items-center justify-center "
                        "rounded-full border border-dashed border-[#1C4576]"
                    ),
                ),
            ),
            rx.el.span(
                slot["seat"],
                class_name=(
                    "absolute -left-1 -top-1 flex size-4 items-center "
                    "justify-center rounded border border-[#1C4576] "
                    "bg-[#071A33] text-[9px] font-bold text-sky-200"
                ),
            ),
            rx.cond(
                slot["kind"] == "player",
                rx.cond(
                    slot["is_online"],
                    rx.el.span(
                        class_name=(
                            "absolute -bottom-0.5 -right-0.5 size-3 "
                            "rounded-full border-2 border-[#0B2647] "
                            "bg-emerald-500"
                        )
                    ),
                    rx.el.span(
                        class_name=(
                            "absolute -bottom-0.5 -right-0.5 size-3 "
                            "rounded-full border-2 border-[#0B2647] "
                            "bg-rose-500"
                        )
                    ),
                ),
                rx.fragment(),
            ),
            class_name="relative",
        ),
        rx.el.p(
            slot["name"],
            class_name=rx.cond(
                slot["kind"] == "empty",
                "max-w-[76px] truncate text-[10px] font-semibold text-slate-500",
                "max-w-[76px] truncate text-[10px] font-bold text-white",
            ),
        ),
        rx.cond(
            slot["is_host"],
            rx.el.span(
                "HOTE",
                class_name="text-[9px] font-black tracking-wide text-amber-300",
            ),
            rx.cond(
                (slot["kind"] == "player") & slot["is_ready"],
                rx.el.span(
                    "PRET",
                    class_name="text-[9px] font-black text-emerald-300",
                ),
                rx.cond(
                    slot["kind"] == "player",
                    rx.el.span(
                        "ATTENTE",
                        class_name="text-[9px] font-bold text-slate-500",
                    ),
                    rx.fragment(),
                ),
            ),
        ),
        class_name="flex w-20 flex-col items-center gap-1",
    )


def slot_at(index: int) -> rx.Component:
    return rx.cond(
        RoomState.lobby_slots.length() > index,
        seat_puck(RoomState.lobby_slots[index]),
        rx.el.div(class_name="w-20"),
    )


def roster_row(slot: LobbySlot) -> rx.Component:
    """Full roster line: identity, badges, ticket count, host removal."""
    return rx.el.div(
        rx.el.span(
            slot["seat"],
            class_name=(
                "flex size-6 shrink-0 items-center justify-center rounded "
                "border border-[#1C4576] bg-[#071A33] text-[11px] "
                "font-bold text-sky-200"
            ),
        ),
        rx.match(
            slot["kind"],
            (
                "player",
                rx.el.div(
                    avatar(slot["avatar_url"], slot["avatar_remote"], "size-9"),
                    rx.cond(
                        slot["is_online"],
                        rx.el.span(
                            class_name=(
                                "absolute -bottom-0.5 -right-0.5 size-3 "
                                "rounded-full border-2 border-[#0B2647] "
                                "bg-emerald-500"
                            )
                        ),
                        rx.el.span(
                            class_name=(
                                "absolute -bottom-0.5 -right-0.5 size-3 "
                                "rounded-full border-2 border-[#0B2647] "
                                "bg-rose-500"
                            )
                        ),
                    ),
                    class_name="relative shrink-0",
                ),
            ),
            (
                "bot",
                rx.el.div(
                    rx.icon("bot", class_name="h-4 w-4 text-cyan-200"),
                    class_name=(
                        "flex size-9 shrink-0 items-center justify-center "
                        "rounded-full border border-cyan-400/40 "
                        "bg-cyan-500/10"
                    ),
                ),
            ),
            rx.el.div(
                rx.icon("user-plus", class_name="h-4 w-4 text-slate-500"),
                class_name=(
                    "flex size-9 shrink-0 items-center justify-center "
                    "rounded-full border border-dashed border-[#1C4576]"
                ),
            ),
        ),
        rx.el.div(
            rx.el.p(
                slot["name"],
                class_name=rx.cond(
                    slot["kind"] == "empty",
                    "truncate text-xs font-bold text-slate-500",
                    "truncate text-xs font-bold text-white",
                ),
            ),
            rx.el.div(
                rx.cond(
                    slot["is_host"],
                    chip("Hote", "gold"),
                    rx.fragment(),
                ),
                rx.cond(slot["is_me"], chip("Vous", "cyan"), rx.fragment()),
                rx.cond(
                    slot["kind"] == "player",
                    rx.cond(
                        slot["is_ready"],
                        chip("Pret", "emerald"),
                        chip("En attente", "slate"),
                    ),
                    rx.cond(
                        slot["kind"] == "bot",
                        chip("Bot serveur", "cyan"),
                        chip("Siege libre", "slate"),
                    ),
                ),
                rx.cond(
                    (slot["kind"] == "player") & ~slot["is_online"],
                    chip("Deconnecte", "rose"),
                    rx.fragment(),
                ),
                rx.cond(
                    RoomState.is_loto_lobby & (slot["kind"] == "player"),
                    chip(f"{slot['cards']} carton(s)", "sky"),
                    rx.fragment(),
                ),
                class_name="mt-1 flex flex-wrap items-center gap-1",
            ),
            class_name="min-w-0 flex-1",
        ),
        rx.cond(
            slot["can_remove"],
            rx.el.button(
                rx.icon("user-minus", class_name="h-4 w-4"),
                on_click=lambda: RoomState.remove_player(slot["account_id"]),
                aria_label="Retirer ce joueur",
                title="Retirer ce joueur",
                class_name=(
                    "flex size-8 shrink-0 items-center justify-center "
                    "rounded-lg border border-rose-400/40 text-rose-300 "
                    "hover:bg-rose-500/15 focus:outline-hidden "
                    "focus:ring-2 focus:ring-rose-400/60"
                ),
            ),
            rx.fragment(),
        ),
        class_name=rx.cond(
            slot["kind"] == "empty",
            "flex items-center gap-2.5 rounded-lg border border-dashed "
            "border-[#1C4576] bg-[#071A33]/60 p-2",
            "flex items-center gap-2.5 rounded-lg border border-[#123A63] "
            "bg-[#0A2440] p-2",
        ),
    )


def roster(scrollable: bool) -> rx.Component:
    return rx.el.div(
        rx.el.div(
            rx.el.p("Joueurs installes", class_name=SUBTLE),
            rx.cond(
                RoomState.lobby_is_complete,
                chip("Complet", "emerald"),
                chip(f"{RoomState.lobby_free_seats} libre(s)", "slate"),
            ),
            class_name="mb-2 flex items-center justify-between",
        ),
        rx.el.div(
            rx.foreach(
                RoomState.lobby_slots,
                lambda slot: roster_row(slot),
            ),
            class_name=(
                "flex max-h-72 flex-col gap-1.5 overflow-y-auto pr-1"
                if scrollable
                else "flex flex-col gap-1.5"
            ),
        ),
        class_name=CARD + " p-3",
    )


# --------------------------------------------------------- table geometries
def felt(*children, class_name: str = "") -> rx.Component:
    return rx.el.div(
        *children,
        class_name=(
            "flex items-center justify-center rounded-full border "
            "border-cyan-500/25 "
            "bg-[radial-gradient(circle_at_50%_30%,#0E3A5C,#071A33_72%)] "
            + class_name
        ),
    )


def domino_table() -> rx.Component:
    """Compact 2-3 seat domino ring around a felt table."""
    return rx.el.div(
        rx.el.p("Table Domino", class_name=SUBTLE),
        rx.el.div(
            rx.el.div(slot_at(0), class_name="flex justify-center"),
            rx.el.div(
                rx.cond(
                    RoomState.lobby_slots.length() > 2,
                    slot_at(1),
                    rx.el.div(class_name="w-20"),
                ),
                felt(
                    rx.el.div(
                        rx.el.span(
                            class_name="size-1.5 rounded-full bg-[#0B2647]"
                        ),
                        rx.el.span(
                            class_name="size-1.5 rounded-full bg-[#0B2647]"
                        ),
                        rx.el.span(
                            class_name="size-1.5 rounded-full bg-[#0B2647]"
                        ),
                        class_name=(
                            "flex h-10 w-7 flex-col items-center "
                            "justify-center gap-1 rounded border "
                            "border-[#C8BB9B] bg-[#F5EEDC]"
                        ),
                    ),
                    class_name="size-28 shrink-0",
                ),
                rx.cond(
                    RoomState.lobby_slots.length() > 2,
                    slot_at(2),
                    slot_at(1),
                ),
                class_name="flex items-center justify-center gap-3",
            ),
            class_name="mt-2 flex flex-col items-center gap-3",
        ),
        class_name=CARD + " p-3",
    )


def ludo_quadrant(color: str) -> rx.Component:
    return rx.el.span(class_name=f"size-5 rounded-sm {color}")


def ludo_table() -> rx.Component:
    """Up to four seats around a simplified four-colour Ludo centre."""
    return rx.el.div(
        rx.el.p("Plateau Ludo", class_name=SUBTLE),
        rx.el.div(
            rx.el.div(slot_at(0), class_name="flex justify-center"),
            rx.el.div(
                rx.cond(
                    RoomState.lobby_slots.length() > 3,
                    slot_at(3),
                    rx.el.div(class_name="w-20"),
                ),
                rx.el.div(
                    rx.el.div(
                        ludo_quadrant("bg-rose-500"),
                        ludo_quadrant("bg-emerald-500"),
                        ludo_quadrant("bg-sky-500"),
                        ludo_quadrant("bg-amber-400"),
                        class_name="grid grid-cols-2 gap-1",
                    ),
                    class_name=(
                        "flex size-28 shrink-0 items-center justify-center "
                        "rounded-lg border border-[#1C4576] "
                        "bg-[radial-gradient(circle_at_50%_30%,#0E3A5C,"
                        "#071A33_72%)]"
                    ),
                ),
                rx.cond(
                    RoomState.lobby_slots.length() > 1,
                    slot_at(1),
                    rx.el.div(class_name="w-20"),
                ),
                class_name="flex items-center justify-center gap-3",
            ),
            rx.el.div(
                rx.cond(
                    RoomState.lobby_slots.length() > 2,
                    slot_at(2),
                    rx.el.div(class_name="w-20"),
                ),
                class_name="flex justify-center",
            ),
            class_name="mt-2 flex flex-col items-center gap-3",
        ),
        class_name=CARD + " p-3",
    )


def loto_head() -> rx.Component:
    """Host / draw table heading for the Loto waiting room."""
    return rx.el.div(
        rx.el.div(
            rx.el.div(
                rx.icon("dices", class_name="h-5 w-5 text-cyan-200"),
                class_name=(
                    "flex size-11 shrink-0 items-center justify-center "
                    "rounded-lg border border-cyan-400/35 bg-[#082B3F]"
                ),
            ),
            rx.el.div(
                rx.el.p("Table de tirage", class_name=SUBTLE),
                rx.el.p(
                    rx.cond(
                        RoomState.lobby_host_name != "",
                        RoomState.lobby_host_name,
                        "Hote absent",
                    ),
                    class_name="truncate text-sm font-bold text-white",
                ),
                class_name="min-w-0 flex-1",
            ),
            chip(f"{RoomState.lobby_ticket_total} carton(s) en jeu", "cyan"),
            class_name="flex items-center gap-2",
        ),
        rx.el.p(
            f"Une boule toutes les {RoomState.lobby_draw_seconds}s des le "
            "lancement. Vos cartons: "
            f"{RoomState.lobby_my_tickets}.",
            class_name="mt-2 text-[11px] font-medium text-slate-400",
        ),
        class_name=CARD + " p-3",
    )


def table_composition() -> rx.Component:
    return rx.match(
        RoomState.slug,
        ("domino", domino_table()),
        ("ludo", ludo_table()),
        ("loto", loto_head()),
        rx.fragment(),
    )


# ----------------------------------------------------------------- settings
def settings_panel() -> rx.Component:
    return rx.el.div(
        rx.el.p("Reglages de la partie", class_name=SUBTLE),
        rx.el.div(
            rx.match(
                RoomState.slug,
                (
                    "domino",
                    rx.el.div(
                        chip(RoomState.lobby_mode_label, "sky"),
                        chip(
                            f"Objectif {RoomState.lobby_target_score} pts",
                            "gold",
                        ),
                        chip(
                            f"{RoomState.lobby_target_players} joueurs", "cyan"
                        ),
                        rx.foreach(
                            RoomState.lobby_special_rules,
                            lambda rule: chip(rule, "slate"),
                        ),
                        rx.cond(
                            RoomState.lobby_fill_bots,
                            chip(
                                f"{RoomState.lobby_bot_count} bot(s) prevu(s)",
                                "cyan",
                            ),
                            chip("Sans bots", "slate"),
                        ),
                        class_name="flex flex-wrap gap-1.5",
                    ),
                ),
                (
                    "ludo",
                    rx.el.div(
                        chip(
                            "Quatre pions a la maison pour gagner",
                            "gold",
                        ),
                        chip(
                            f"2 a {RoomState.lobby_target_players} joueurs",
                            "cyan",
                        ),
                        chip("Zones sures et captures actives", "sky"),
                        class_name="flex flex-wrap gap-1.5",
                    ),
                ),
                (
                    "loto",
                    rx.el.div(
                        chip(RoomState.lobby_tier_label, "gold"),
                        chip(
                            f"{RoomState.lobby_tier_price} pts / carton",
                            "sky",
                        ),
                        chip(
                            f"1 a {RoomState.lobby_tier_max_cards} cartons "
                            "par joueur",
                            "slate",
                        ),
                        chip("Mandry 1 / Mandry 2 / Aoka", "cyan"),
                        chip(
                            f"Tirage toutes les {RoomState.lobby_draw_seconds}s",
                            "cyan",
                        ),
                        chip(
                            f"{RoomState.lobby_target_players} joueurs max",
                            "slate",
                        ),
                        class_name="flex flex-wrap gap-1.5",
                    ),
                ),
                rx.fragment(),
            ),
            class_name="mt-2",
        ),
        rx.el.p(
            "Les points TATA sont virtuels et internes: aucun depot, aucun "
            "retrait, aucune valeur monetaire.",
            class_name="mt-2 text-[10px] leading-relaxed text-slate-500",
        ),
        class_name=CARD + " p-3",
    )


# ------------------------------------------------------------------ actions
def lobby_actions() -> rx.Component:
    return rx.el.div(
        rx.el.p(
            RoomState.lobby_start_hint,
            class_name="text-[11px] font-semibold text-slate-300",
        ),
        rx.cond(
            RoomState.is_host,
            rx.el.button(
                rx.icon("play", class_name="h-4 w-4"),
                "Lancer la partie",
                on_click=rx.cond(
                    RoomState.lobby_can_start,
                    RoomState.start_match,
                    rx.noop(),
                ),
                disabled=~RoomState.lobby_can_start,
                class_name=(
                    "mt-2 flex w-full items-center justify-center gap-2 "
                    "rounded-lg bg-sky-500 py-3 text-sm font-black "
                    "text-[#04182E] hover:bg-sky-400 active:scale-[0.99] "
                    "focus:outline-hidden focus:ring-2 focus:ring-cyan-300 "
                    "disabled:cursor-not-allowed disabled:bg-[#123A63] "
                    "disabled:text-slate-500"
                ),
            ),
            rx.el.button(
                rx.icon("check", class_name="h-4 w-4"),
                rx.cond(RoomState.my_ready, "Je suis pret", "Se declarer pret"),
                on_click=RoomState.toggle_ready,
                class_name=rx.cond(
                    RoomState.my_ready,
                    "mt-2 flex w-full items-center justify-center gap-2 "
                    "rounded-lg border border-emerald-400/50 "
                    "bg-emerald-500/15 py-3 text-sm font-bold "
                    "text-emerald-200 active:scale-[0.99] "
                    "focus:outline-hidden focus:ring-2 "
                    "focus:ring-emerald-300",
                    "mt-2 flex w-full items-center justify-center gap-2 "
                    "rounded-lg border border-[#1C4576] bg-[#0A2440] py-3 "
                    "text-sm font-bold text-slate-200 hover:border-sky-400/60 "
                    "active:scale-[0.99] focus:outline-hidden focus:ring-2 "
                    "focus:ring-sky-400/60",
                ),
            ),
        ),
        rx.el.div(
            rx.el.button(
                rx.icon("refresh-cw", class_name="h-4 w-4"),
                "Actualiser",
                on_click=RoomState.manual_refresh,
                class_name=(
                    "flex flex-1 items-center justify-center gap-1.5 "
                    "rounded-lg border border-[#1C4576] py-2.5 text-xs "
                    "font-bold text-slate-300 hover:border-cyan-400/50 "
                    "focus:outline-hidden focus:ring-2 focus:ring-cyan-400/50"
                ),
            ),
            rx.el.button(
                rx.icon("log-out", class_name="h-4 w-4"),
                "Quitter",
                on_click=RoomState.leave_room,
                class_name=(
                    "flex flex-1 items-center justify-center gap-1.5 "
                    "rounded-lg border border-[#1C4576] py-2.5 text-xs "
                    "font-bold text-slate-400 hover:border-rose-500/60 "
                    "hover:text-rose-300 focus:outline-hidden focus:ring-2 "
                    "focus:ring-rose-400/50"
                ),
            ),
            class_name="mt-2 flex gap-2",
        ),
        class_name=(
            "sticky bottom-0 mt-1 rounded-xl border border-[#123A63] "
            "bg-[#071A33]/95 p-3 "
            "pb-[calc(env(safe-area-inset-bottom)+12px)]"
        ),
    )


def locked_out() -> rx.Component:
    return rx.el.div(
        rx.el.div(
            rx.icon("user-x", class_name="h-6 w-6 text-rose-300"),
            rx.el.h1(
                "Vous n'etes plus dans cette salle",
                class_name="mt-2 text-base font-black text-white",
            ),
            rx.el.p(
                "L'hote vous a retire de la salle d'attente, ou votre siege a "
                "ete libere apres une deconnexion. Rejoignez une autre salle "
                "ou demandez un nouveau code a l'hote.",
                class_name="mt-1 text-[12px] leading-relaxed text-slate-400",
            ),
            rx.el.a(
                rx.icon("arrow-left", class_name="h-4 w-4"),
                f"Retour a {RoomState.game_name}",
                href=RoomState.detail_href,
                class_name=(
                    "mt-3 flex w-full items-center justify-center gap-2 "
                    "rounded-lg bg-sky-500 py-3 text-sm font-black "
                    "text-[#04182E] hover:bg-sky-400"
                ),
            ),
            rx.el.button(
                rx.icon("refresh-cw", class_name="h-4 w-4"),
                "Reessayer la connexion",
                on_click=RoomState.manual_refresh,
                class_name=(
                    "mt-2 flex w-full items-center justify-center gap-2 "
                    "rounded-lg border border-[#1C4576] py-2.5 text-xs "
                    "font-bold text-slate-300 hover:border-cyan-400/50"
                ),
            ),
            class_name=CARD + " p-4",
        ),
        class_name=(
            "mx-auto flex w-full max-w-[440px] flex-col gap-3 px-1 pt-1 "
            "font-['Inter']"
        ),
    )


def lobby_body() -> rx.Component:
    return rx.el.div(
        connection_banner(),
        lobby_header(),
        table_composition(),
        settings_panel(),
        rx.cond(
            RoomState.is_loto_lobby,
            roster(True),
            roster(False),
        ),
        rx.cond(
            RoomState.is_loto_lobby,
            rx.el.div(loto_controls(), class_name="w-full"),
            rx.fragment(),
        ),
        lobby_actions(),
        class_name=(
            "mx-auto flex w-full max-w-[440px] flex-col gap-3 px-1 pt-1 "
            "font-['Inter']"
        ),
    )


def table_lobby() -> rx.Component:
    """Connected shared waiting lobby (auto-refreshed by RoomState polling)."""
    return rx.cond(
        RoomState.lobby_locked_out,
        locked_out(),
        lobby_body(),
    )
