"""Settings: language, appearance, privacy, notifications, logout, deletion."""

from __future__ import annotations

import reflex as rx

from app.components.danger_zone import danger_zone
from app.components.game_shell import dark_page
from app.states.auth_state import AuthState
from app.states.settings_state import SettingsState


def card(title: str, icon: str, *children) -> rx.Component:
    return rx.el.div(
        rx.el.div(
            rx.icon(icon, class_name="h-4 w-4 text-amber-300"),
            rx.el.h2(
                title,
                class_name=(
                    "text-xs font-bold uppercase tracking-wider text-zinc-400"
                ),
            ),
            class_name="mb-3 flex items-center gap-2",
        ),
        *children,
        class_name="rounded-2xl border border-zinc-800 bg-[#0C0D10] p-4",
    )


def toggle_row(
    label: str, description: str, value: rx.Var, field: str
) -> rx.Component:
    return rx.el.div(
        rx.el.div(
            rx.el.p(label, class_name="text-sm font-semibold text-white"),
            rx.el.p(description, class_name="text-[11px] text-zinc-500"),
            class_name="min-w-0 flex-1",
        ),
        rx.el.button(
            rx.el.span(
                class_name=rx.cond(
                    value,
                    "block size-4 translate-x-5 rounded-full bg-black transition",
                    "block size-4 translate-x-0.5 rounded-full bg-zinc-400 transition",
                )
            ),
            on_click=lambda: SettingsState.toggle_flag(field),
            role="switch",
            aria_label=label,
            class_name=rx.cond(
                value,
                "flex h-5 w-10 shrink-0 items-center rounded-full bg-emerald-500",
                "flex h-5 w-10 shrink-0 items-center rounded-full bg-zinc-800",
            ),
        ),
        class_name=(
            "flex items-center gap-3 border-b border-zinc-800/60 py-3 "
            "last:border-0"
        ),
    )


def appearance_button(label: str, value: str, icon: str) -> rx.Component:
    return rx.el.button(
        rx.icon(icon, class_name="h-4 w-4"),
        rx.el.span(label, class_name="text-xs font-bold"),
        on_click=lambda: SettingsState.set_theme(value),
        class_name=rx.cond(
            SettingsState.theme == value,
            "flex flex-1 items-center justify-center gap-2 rounded-xl bg-emerald-500 py-2 text-black",
            "flex flex-1 items-center justify-center gap-2 rounded-xl border border-zinc-800 py-2 text-zinc-300 hover:border-zinc-600",
        ),
    )


def visibility_button(label: str, value: str) -> rx.Component:
    return rx.el.button(
        label,
        on_click=lambda: SettingsState.set_visibility(value),
        class_name=rx.cond(
            SettingsState.profile_visibility == value,
            "flex-1 rounded-xl bg-zinc-800 py-2 text-xs font-bold text-white",
            "flex-1 rounded-xl border border-zinc-800 py-2 text-xs font-bold text-zinc-400 hover:border-zinc-600",
        ),
    )


def settings_body() -> rx.Component:
    return rx.el.div(
        rx.cond(
            SettingsState.loading,
            rx.el.div(class_name="h-40 animate-pulse rounded-2xl bg-zinc-900"),
            rx.el.div(
                card(
                    "Langue",
                    "languages",
                    rx.el.div(
                        rx.el.select(
                            rx.foreach(
                                SettingsState.languages,
                                lambda item: rx.el.option(
                                    item["label"], value=item["value"]
                                ),
                            ),
                            value=SettingsState.language,
                            on_change=SettingsState.set_language,
                            aria_label="Langue de l'interface",
                            class_name=(
                                "w-full appearance-none rounded-xl border "
                                "border-zinc-800 bg-[#0A0B0E] px-3 py-2 pr-8 "
                                "text-sm text-white outline-hidden "
                                "focus:border-emerald-500"
                            ),
                        ),
                        rx.icon(
                            "chevron-down",
                            class_name=(
                                "pointer-events-none absolute right-3 top-3 "
                                "h-4 w-4 text-zinc-500"
                            ),
                        ),
                        class_name="relative",
                    ),
                    rx.el.p(
                        "Huit langues disponibles: anglais, francais, malgache, "
                        "arabe, hindi, chinois, espagnol, portugais.",
                        class_name="mt-2 text-[11px] text-zinc-500",
                    ),
                ),
                card(
                    "Apparence",
                    "palette",
                    rx.el.div(
                        appearance_button("Clair", "light", "sun"),
                        appearance_button("Sombre", "dark", "moon"),
                        appearance_button("Systeme", "system", "monitor"),
                        class_name="flex gap-2",
                    ),
                ),
                card(
                    "Confidentialite",
                    "shield",
                    rx.el.div(
                        visibility_button("Public", "public"),
                        visibility_button("Amis", "friends"),
                        visibility_button("Prive", "private"),
                        class_name="flex gap-2",
                    ),
                    toggle_row(
                        "Statut en ligne",
                        "Afficher quand vous etes connecte.",
                        SettingsState.show_online_status,
                        "show_online_status",
                    ),
                    toggle_row(
                        "Demandes d'amis",
                        "Autoriser les nouvelles demandes.",
                        SettingsState.allow_friend_requests,
                        "allow_friend_requests",
                    ),
                    toggle_row(
                        "Messages des inconnus",
                        "Recevoir des messages hors de vos amis.",
                        SettingsState.allow_messages_from_strangers,
                        "allow_messages_from_strangers",
                    ),
                ),
                card(
                    "Notifications",
                    "bell",
                    toggle_row(
                        "Reactions",
                        "Quand quelqu'un reagit a vos publications.",
                        SettingsState.notify_reactions,
                        "notify_reactions",
                    ),
                    toggle_row(
                        "Commentaires",
                        "Nouvelles reponses a vos publications.",
                        SettingsState.notify_comments,
                        "notify_comments",
                    ),
                    toggle_row(
                        "Messages",
                        "Nouveaux messages prives.",
                        SettingsState.notify_messages,
                        "notify_messages",
                    ),
                    toggle_row(
                        "Demandes d'amis",
                        "Nouvelles demandes recues.",
                        SettingsState.notify_friend_requests,
                        "notify_friend_requests",
                    ),
                    toggle_row(
                        "Invitations de jeu",
                        "Invitations dans les salles de jeu.",
                        SettingsState.notify_game_invites,
                        "notify_game_invites",
                    ),
                ),
                card(
                    "Compte",
                    "user",
                    rx.el.button(
                        rx.icon("log-out", class_name="h-4 w-4"),
                        rx.el.span(
                            "Se deconnecter",
                            class_name="text-xs font-bold",
                        ),
                        on_click=AuthState.logout,
                        class_name=(
                            "flex w-full items-center justify-center gap-2 "
                            "rounded-xl border border-zinc-800 py-2.5 "
                            "text-zinc-200 hover:border-zinc-600"
                        ),
                    ),
                    rx.el.div(
                        danger_zone(),
                        class_name="[&_button]:!border-zinc-800",
                    ),
                    rx.el.p(
                        "La suppression demande votre mot de passe et votre "
                        "nom d'utilisateur exact.",
                        class_name="mt-2 text-[11px] text-zinc-500",
                    ),
                ),
                class_name="grid w-full gap-4 lg:grid-cols-2",
            ),
        ),
        class_name="flex w-full flex-col gap-4",
    )


def settings_page() -> rx.Component:
    return dark_page("Parametres", settings_body(), "profil", "/games")
