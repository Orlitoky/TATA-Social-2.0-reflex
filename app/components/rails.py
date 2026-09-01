"""Desktop primary rail and contacts rail."""

from __future__ import annotations

import reflex as rx

from app.components.ui import avatar
from app.states.auth_state import AuthState
from app.states.social_state import PersonRow, SocialState


def rail_link(
    icon: str, label: str, href: str = "/", active: bool = False
) -> rx.Component:
    return rx.el.a(
        rx.icon(
            icon,
            class_name=(
                "h-4 w-4 text-[#1E9EF5]" if active else "h-4 w-4 text-slate-400"
            ),
        ),
        rx.el.span(label, class_name="text-sm font-semibold"),
        href=href,
        class_name=(
            "flex items-center gap-3 rounded-xl px-3 py-2 bg-sky-50 text-[#0D1420]"
            if active
            else "flex items-center gap-3 rounded-xl px-3 py-2 text-slate-600 hover:bg-slate-50"
        ),
    )


def primary_rail(active: str = "home") -> rx.Component:
    return rx.el.aside(
        rx.el.a(
            avatar(AuthState.avatar_url, AuthState.avatar_remote, "size-11"),
            rx.el.div(
                rx.el.p(
                    AuthState.display_name,
                    class_name="text-sm font-semibold text-[#0D1420] truncate",
                ),
                rx.el.p(
                    f"@{AuthState.username}",
                    class_name="text-xs text-slate-500 truncate",
                ),
                class_name="min-w-0",
            ),
            href="/profile",
            class_name="flex items-center gap-3 rounded-2xl border border-slate-200 bg-white p-3 hover:border-[#1E9EF5]",
        ),
        rx.el.nav(
            rail_link("house", "Home", "/", active == "home"),
            rail_link("users", "Friends", "/friends", active == "friends"),
            rail_link(
                "message-circle", "Messages", "/messages", active == "messages"
            ),
            rail_link("compass", "Discover", "/"),
            rail_link("bookmark", "Saved", "/"),
            rail_link("circle-play", "Stories", "/"),
            rail_link("user", "Profile", "/profile", active == "profile"),
            class_name="mt-3 flex flex-col gap-1 rounded-2xl border border-slate-200 bg-white p-2",
        ),
        rx.el.div(
            rx.el.div(
                rx.icon("coins", class_name="h-4 w-4 text-[#22D3EE]"),
                rx.el.span(
                    "TATA Coins",
                    class_name="text-xs font-semibold uppercase tracking-wide text-slate-500",
                ),
                class_name="flex items-center gap-2",
            ),
            rx.el.p(
                f"{AuthState.coin_balance}",
                class_name="mt-1 text-2xl font-bold text-[#0D1420]",
            ),
            rx.el.p(
                "Virtual only. No cash value.",
                class_name="text-xs text-slate-500",
            ),
            class_name="mt-3 rounded-2xl border border-slate-200 bg-white p-3",
        ),
        class_name="hidden lg:block w-64 shrink-0",
    )


def contact_row(person: PersonRow) -> rx.Component:
    return rx.el.div(
        rx.el.div(
            avatar(person["avatar_url"], person["avatar_remote"], "size-9"),
            rx.cond(
                person["is_online"],
                rx.el.span(
                    class_name="absolute bottom-0 right-0 size-2.5 rounded-full border-2 border-white bg-emerald-500",
                ),
            ),
            class_name="relative",
        ),
        rx.el.div(
            rx.el.p(
                person["display_name"],
                class_name="text-sm font-semibold text-[#0D1420] truncate",
            ),
            rx.el.p(
                person["subtitle"], class_name="text-xs text-slate-500 truncate"
            ),
            class_name="min-w-0 flex-1",
        ),
        class_name="flex items-center gap-3 rounded-xl px-2 py-2 hover:bg-sky-50",
    )


def contacts_rail() -> rx.Component:
    return rx.el.aside(
        rx.el.div(
            rx.el.div(
                rx.icon("users", class_name="h-4 w-4 text-[#1E9EF5]"),
                rx.el.span(
                    "Contacts",
                    class_name="text-sm font-semibold text-[#0D1420]",
                ),
                class_name="flex items-center gap-2 px-2 pb-2",
            ),
            rx.cond(
                SocialState.contacts.length() > 0,
                rx.el.div(
                    rx.foreach(SocialState.contacts, contact_row),
                    class_name="flex flex-col",
                ),
                rx.el.p(
                    "No contacts yet.",
                    class_name="px-2 py-3 text-sm text-slate-500",
                ),
            ),
            class_name="rounded-2xl border border-slate-200 bg-white p-2",
        ),
        class_name="hidden xl:block w-72 shrink-0",
    )
