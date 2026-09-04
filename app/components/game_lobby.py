"""Reusable waiting-lobby pieces: RoomCode, PlayerSlot and GameLobby.

Premium competitive Domino identity: layered dark navy, warm gold room code
and primary action, blue player iconography, purple special-rule accents.
Coins stay internal virtual points: no purchase, deposit, withdrawal or
monetary value anywhere in this screen.
"""

from __future__ import annotations

import reflex as rx

from app.components.ui import avatar
from app.states.room_state import LobbySlot, RoomState

NAVY_CARD = (
    "rounded-2xl border border-[#1E2A47] bg-[#0E1626] "
    "shadow-[0_1px_0_rgba(255,255,255,0.04)_inset,0_10px_24px_rgba(0,0,0,0.45)]"
)


def domino_motif() -> rx.Component:
    """Tactile ivory domino tile used as the lobby identity mark."""
    return rx.el.div(
        rx.el.div(
            rx.el.span(class_name="size-1.5 rounded-full bg-[#1B2740]"),
            rx.el.span(class_name="size-1.5 rounded-full bg-[#1B2740]"),
            rx.el.span(class_name="size-1.5 rounded-full bg-[#1B2740]"),
            class_name="flex items-center justify-center gap-1",
        ),
        rx.el.div(class_name="h-px w-6 bg-[#1B2740]/50"),
        rx.el.div(
            rx.el.span(class_name="size-1.5 rounded-full bg-[#1B2740]"),
            rx.el.span(class_name="size-1.5 rounded-full bg-[#1B2740]"),
            class_name="flex items-center justify-center gap-1.5",
        ),
        class_name=(
            "flex h-12 w-8 shrink-0 flex-col items-center justify-center "
            "gap-1 rounded-md border border-[#C8BB9B] "
            "bg-[linear-gradient(160deg,#FFFDF3,#EFE6CE_60%,#D9CDAF)] "
            "shadow-[0_3px_0_#A79571,0_5px_10px_rgba(0,0,0,0.5)]"
        ),
    )


def lobby_chip(label: str | rx.Var, tone: str = "blue") -> rx.Component:
    tones = {
        "blue": "border-sky-400/30 bg-sky-500/10 text-sky-200",
        "gold": "border-amber-400/35 bg-amber-500/10 text-amber-200",
        "violet": "border-indigo-400/35 bg-indigo-500/10 text-indigo-200",
        "slate": "border-[#243250] bg-[#131E33] text-slate-300",
    }
    return rx.el.span(
        label,
        class_name=(
            "w-fit rounded-full border px-2.5 py-1 text-[11px] font-bold "
            "tracking-tight " + tones.get(tone, tones["blue"])
        ),
    )


def room_code_card() -> rx.Component:
    """Gold room code with clipboard copy and Web Share invite."""
    return rx.el.div(
        rx.el.div(
            rx.el.p(
                "Code de la salle",
                class_name=(
                    "text-[10px] font-bold uppercase tracking-[0.18em] "
                    "text-amber-500/80"
                ),
            ),
            rx.el.p(
                f"Room #{RoomState.code}",
                class_name=(
                    "font-mono text-xl font-black tracking-[0.14em] "
                    "text-amber-200"
                ),
            ),
            class_name="min-w-0 flex-1",
        ),
        rx.el.div(
            rx.el.button(
                rx.icon("copy", class_name="h-4 w-4"),
                "Copier le code",
                on_click=RoomState.copy_code,
                class_name=(
                    "flex flex-1 items-center justify-center gap-1.5 "
                    "rounded-xl border border-amber-400/40 bg-[#1A1608] "
                    "px-3 py-2 text-[11px] font-bold text-amber-200 "
                    "hover:bg-amber-400/10 active:scale-[0.98]"
                ),
            ),
            rx.el.button(
                rx.icon("share-2", class_name="h-4 w-4"),
                "Inviter",
                on_click=RoomState.invite_players,
                class_name=(
                    "flex flex-1 items-center justify-center gap-1.5 "
                    "rounded-xl border border-sky-400/40 bg-[#0C1A2C] "
                    "px-3 py-2 text-[11px] font-bold text-sky-200 "
                    "hover:bg-sky-400/10 active:scale-[0.98]"
                ),
            ),
            class_name="mt-3 flex w-full gap-2",
        ),
        class_name=(
            "rounded-2xl border border-dashed border-amber-400/35 "
            "bg-[radial-gradient(circle_at_15%_0%,#1B1608,#0E1626_70%)] p-3"
        ),
    )


def player_slot(slot: LobbySlot) -> rx.Component:
    """Numbered seat: human player, server bot, or empty waiting seat."""
    return rx.el.div(
        rx.el.span(
            slot["seat"],
            class_name=rx.cond(
                slot["kind"] == "empty",
                "flex size-6 shrink-0 items-center justify-center rounded-lg "
                "border border-dashed border-[#2B3B5E] text-[11px] "
                "font-bold text-slate-500",
                "flex size-6 shrink-0 items-center justify-center rounded-lg "
                "border border-sky-400/40 bg-sky-500/10 text-[11px] "
                "font-bold text-sky-200",
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
                                "rounded-full border-2 border-[#0E1626] "
                                "bg-emerald-500"
                            )
                        ),
                        rx.el.span(
                            class_name=(
                                "absolute -bottom-0.5 -right-0.5 size-3 "
                                "rounded-full border-2 border-[#0E1626] "
                                "bg-slate-600"
                            )
                        ),
                    ),
                    class_name="relative shrink-0",
                ),
            ),
            (
                "bot",
                rx.el.div(
                    rx.icon("bot", class_name="h-4 w-4 text-indigo-200"),
                    class_name=(
                        "flex size-9 shrink-0 items-center justify-center "
                        "rounded-full border border-indigo-400/40 "
                        "bg-indigo-500/15"
                    ),
                ),
            ),
            rx.el.div(
                rx.icon("user-plus", class_name="h-4 w-4 text-slate-500"),
                class_name=(
                    "flex size-9 shrink-0 items-center justify-center "
                    "rounded-full border border-dashed border-[#2B3B5E]"
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
                rx.match(
                    slot["kind"],
                    (
                        "player",
                        rx.cond(
                            slot["is_host"],
                            rx.el.span(
                                "Host",
                                class_name=(
                                    "text-[10px] font-black uppercase "
                                    "tracking-wide text-amber-300"
                                ),
                            ),
                            rx.el.span(
                                "Joueur",
                                class_name=(
                                    "text-[10px] font-bold uppercase "
                                    "tracking-wide text-sky-300"
                                ),
                            ),
                        ),
                    ),
                    (
                        "bot",
                        rx.el.span(
                            "Bot serveur",
                            class_name=(
                                "text-[10px] font-bold uppercase "
                                "tracking-wide text-indigo-300"
                            ),
                        ),
                    ),
                    rx.el.span(
                        "Siege libre",
                        class_name=(
                            "text-[10px] font-bold uppercase tracking-wide "
                            "text-slate-500"
                        ),
                    ),
                ),
                rx.cond(
                    slot["kind"] == "player",
                    rx.cond(
                        slot["is_online"],
                        rx.el.span(
                            "Online",
                            class_name=(
                                "text-[10px] font-bold text-emerald-400"
                            ),
                        ),
                        rx.el.span(
                            "Disconnected",
                            class_name="text-[10px] font-bold text-rose-400",
                        ),
                    ),
                    rx.fragment(),
                ),
                rx.cond(
                    (slot["kind"] == "player") & slot["is_ready"],
                    rx.el.span(
                        "Pret",
                        class_name="text-[10px] font-bold text-emerald-300",
                    ),
                    rx.fragment(),
                ),
                class_name="flex flex-wrap items-center gap-2",
            ),
            class_name="min-w-0 flex-1",
        ),
        rx.cond(
            slot["is_me"],
            lobby_chip("Vous", "gold"),
            rx.fragment(),
        ),
        class_name=rx.cond(
            slot["kind"] == "empty",
            "flex items-center gap-3 rounded-xl border border-dashed "
            "border-[#2B3B5E] bg-[#0B1220]/60 p-2.5",
            "flex items-center gap-3 rounded-xl border border-[#22314F] "
            "bg-[#111C2F] p-2.5",
        ),
    )


def lobby_settings() -> rx.Component:
    return rx.el.div(
        rx.el.p(
            "Reglages de la partie",
            class_name=(
                "mb-2 text-[10px] font-bold uppercase tracking-[0.18em] "
                "text-slate-500"
            ),
        ),
        rx.el.div(
            lobby_chip(RoomState.lobby_mode_label, "blue"),
            lobby_chip(f"Objectif {RoomState.lobby_target_score} pts", "gold"),
            lobby_chip(f"{RoomState.lobby_target_players} joueurs", "blue"),
            rx.foreach(
                RoomState.lobby_special_rules,
                lambda rule: lobby_chip(rule, "violet"),
            ),
            rx.cond(
                RoomState.lobby_fill_bots,
                lobby_chip("Completer avec des bots", "violet"),
                rx.fragment(),
            ),
            class_name="flex flex-wrap gap-1.5",
        ),
        class_name=NAVY_CARD + " p-3",
    )


def lobby_host_card() -> rx.Component:
    return rx.el.div(
        rx.icon("crown", class_name="h-4 w-4 shrink-0 text-amber-300"),
        rx.el.div(
            rx.el.p(
                "Hote de la partie",
                class_name="text-[10px] font-bold uppercase text-slate-500",
            ),
            rx.el.p(
                rx.cond(
                    RoomState.lobby_host_name != "",
                    RoomState.lobby_host_name,
                    "Hote absent",
                ),
                class_name="truncate text-xs font-bold text-white",
            ),
            class_name="min-w-0 flex-1",
        ),
        rx.cond(
            RoomState.is_host,
            lobby_chip("Vous etes l'hote", "gold"),
            lobby_chip(RoomState.status_label, "slate"),
        ),
        class_name=NAVY_CARD + " flex items-center gap-2 p-3",
    )


def lobby_actions() -> rx.Component:
    return rx.el.div(
        rx.el.p(
            RoomState.lobby_start_hint,
            class_name="text-[11px] font-semibold text-slate-400",
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
                    "rounded-xl bg-[linear-gradient(140deg,#FFDF8A,#E0A32A)] "
                    "py-3 text-sm font-black text-[#2B1D02] "
                    "shadow-[0_6px_16px_rgba(224,163,42,0.35)] "
                    "hover:brightness-110 active:scale-[0.99] "
                    "disabled:cursor-not-allowed disabled:opacity-40 "
                    "disabled:shadow-none"
                ),
            ),
            rx.el.div(
                rx.el.button(
                    rx.icon("check", class_name="h-4 w-4"),
                    rx.cond(RoomState.my_ready, "Je suis pret", "Je suis pret"),
                    on_click=RoomState.toggle_ready,
                    class_name=rx.cond(
                        RoomState.my_ready,
                        "flex w-full items-center justify-center gap-2 "
                        "rounded-xl border border-emerald-400/50 "
                        "bg-emerald-500/15 py-3 text-sm font-bold "
                        "text-emerald-200 active:scale-[0.99]",
                        "flex w-full items-center justify-center gap-2 "
                        "rounded-xl border border-[#2B3B5E] bg-[#111C2F] "
                        "py-3 text-sm font-bold text-slate-200 "
                        "hover:border-sky-400/50 active:scale-[0.99]",
                    ),
                ),
                rx.el.p(
                    rx.cond(
                        RoomState.my_ready,
                        "Vous etes pret: en attente du lancement par l'hote.",
                        "En attente du lancement par l'hote.",
                    ),
                    class_name="mt-2 text-center text-[11px] text-slate-500",
                ),
                class_name="mt-2 w-full",
            ),
        ),
        rx.el.button(
            rx.icon("log-out", class_name="h-4 w-4"),
            "Quitter la partie",
            on_click=RoomState.leave_room,
            class_name=(
                "mt-2 flex w-full items-center justify-center gap-2 "
                "rounded-xl border border-[#2B3B5E] bg-transparent py-2.5 "
                "text-xs font-bold text-slate-400 hover:border-rose-500/60 "
                "hover:text-rose-300 active:scale-[0.99]"
            ),
        ),
        class_name=(
            "sticky bottom-0 -mx-1 mt-1 rounded-2xl border border-[#1E2A47] "
            "bg-[#0B1220]/95 p-3 backdrop-blur "
            "pb-[calc(env(safe-area-inset-bottom)+12px)]"
        ),
    )


def game_lobby() -> rx.Component:
    """Connected Domino waiting lobby (auto-refreshed by RoomState polling)."""
    return rx.el.div(
        rx.el.div(
            domino_motif(),
            rx.el.div(
                rx.el.h1(
                    "DOMINO",
                    class_name=(
                        "text-xl font-black tracking-[0.16em] text-white"
                    ),
                ),
                rx.el.p(
                    "Salle d'attente premium - points internes uniquement",
                    class_name="text-[11px] font-medium text-slate-400",
                ),
                class_name="min-w-0 flex-1",
            ),
            lobby_chip(
                f"{RoomState.lobby_occupied}/{RoomState.lobby_target_players}",
                "blue",
            ),
            class_name=NAVY_CARD + " flex items-center gap-3 p-3",
        ),
        room_code_card(),
        lobby_settings(),
        lobby_host_card(),
        rx.el.div(
            rx.el.div(
                rx.el.p(
                    "Joueurs",
                    class_name=(
                        "text-[10px] font-bold uppercase tracking-[0.18em] "
                        "text-slate-500"
                    ),
                ),
                rx.cond(
                    RoomState.lobby_is_complete,
                    lobby_chip("Complet", "gold"),
                    lobby_chip(
                        f"{RoomState.lobby_free_seats} libre(s)", "slate"
                    ),
                ),
                class_name="mb-2 flex items-center justify-between",
            ),
            rx.el.div(
                rx.foreach(RoomState.lobby_slots, player_slot),
                class_name="flex flex-col gap-2",
            ),
            class_name=NAVY_CARD + " p-3",
        ),
        rx.el.p(
            "Les points TATA sont virtuels et internes: aucun depot, aucun "
            "retrait, aucune valeur monetaire.",
            class_name="px-1 text-[10px] leading-relaxed text-slate-500",
        ),
        lobby_actions(),
        class_name=(
            "mx-auto flex w-full max-w-[440px] flex-col gap-3 "
            "px-1 pt-1 font-['Inter']"
        ),
    )
