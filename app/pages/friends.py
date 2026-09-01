"""Friends: a people directory with requests, follows and suggestions."""

from __future__ import annotations

import reflex as rx

from app.components.header import header, mobile_nav
from app.components.people import (
    people_grid,
    people_skeleton,
    profile_drawer,
)
from app.components.rails import primary_rail
from app.states.friends_state import FriendsState


def stat_tile(icon: str, label: str, value: rx.Var) -> rx.Component:
    return rx.el.div(
        rx.el.div(
            rx.icon(icon, class_name="h-4 w-4 text-[#1E9EF5]"),
            rx.el.span(
                label,
                class_name="text-[11px] font-semibold uppercase tracking-wide text-slate-400",
            ),
            class_name="flex items-center gap-1.5",
        ),
        rx.el.p(value, class_name="mt-1 text-xl font-bold text-[#0D1420]"),
        class_name="w-full rounded-2xl border border-slate-200 bg-white px-3 py-2",
    )


def tab_button(value: str, label: str, count: rx.Var) -> rx.Component:
    return rx.el.button(
        rx.el.span(label),
        rx.el.span(
            count,
            class_name="rounded-full bg-slate-100 px-1.5 py-0.5 text-[10px] font-bold text-slate-500",
        ),
        on_click=FriendsState.set_tab(value),
        class_name=rx.cond(
            FriendsState.tab == value,
            "flex items-center gap-1.5 whitespace-nowrap border-b-2 border-[#1E9EF5] px-3 py-2 text-sm font-semibold text-[#0D1420]",
            "flex items-center gap-1.5 whitespace-nowrap border-b-2 border-transparent px-3 py-2 text-sm font-semibold text-slate-500 hover:text-[#0D1420]",
        ),
    )


def directory_search() -> rx.Component:
    return rx.el.div(
        rx.icon(
            "search",
            class_name="absolute left-3 top-2.5 h-4 w-4 text-slate-400",
        ),
        rx.el.input(
            placeholder="Search people by name or @username",
            default_value=FriendsState.query,
            on_change=FriendsState.search_people.debounce(400),
            class_name="w-full rounded-full border border-slate-200 bg-white py-2 pl-9 pr-9 text-sm font-medium text-[#0D1420] placeholder:text-slate-400 outline-hidden focus:border-[#1E9EF5] focus:ring-2 focus:ring-sky-100",
        ),
        rx.cond(
            FriendsState.query != "",
            rx.el.button(
                rx.icon("x", class_name="h-4 w-4"),
                on_click=FriendsState.clear_search,
                class_name="absolute right-3 top-2.5 text-slate-400 hover:text-[#0D1420]",
            ),
        ),
        class_name="relative w-full",
    )


def directory_body() -> rx.Component:
    return rx.cond(
        FriendsState.loading,
        people_skeleton(),
        rx.match(
            FriendsState.tab,
            (
                "search",
                rx.cond(
                    FriendsState.searching,
                    people_skeleton(),
                    people_grid(
                        FriendsState.results,
                        "No people match that search yet.",
                        "search-x",
                    ),
                ),
            ),
            (
                "incoming",
                people_grid(
                    FriendsState.incoming,
                    "No incoming friend requests.",
                    "inbox",
                ),
            ),
            (
                "outgoing",
                people_grid(
                    FriendsState.outgoing,
                    "You have no pending sent requests.",
                    "send",
                ),
            ),
            (
                "suggestions",
                people_grid(
                    FriendsState.suggestions,
                    "No suggestions right now. Try searching for people.",
                    "sparkles",
                ),
            ),
            people_grid(
                FriendsState.friends,
                "No friends yet. Add people from suggestions or search.",
                "user-plus",
            ),
        ),
    )


def friends_page() -> rx.Component:
    return rx.el.main(
        header(),
        rx.el.div(
            primary_rail("friends"),
            rx.el.div(
                rx.el.div(
                    rx.el.div(
                        rx.el.h1(
                            "People",
                            class_name="text-lg font-bold text-[#0D1420]",
                        ),
                        rx.el.p(
                            "Find people, manage requests and follow the creators you like.",
                            class_name="text-xs font-medium text-slate-500",
                        ),
                        class_name="min-w-0",
                    ),
                    rx.el.a(
                        rx.icon("message-circle", class_name="h-3.5 w-3.5"),
                        rx.el.span("Open Messages"),
                        href="/messages",
                        class_name="flex shrink-0 items-center gap-1.5 rounded-full border border-slate-200 px-3 py-1.5 text-xs font-semibold text-[#0D1420] hover:border-[#1E9EF5] hover:text-[#1E9EF5]",
                    ),
                    class_name="flex items-start justify-between gap-3",
                ),
                rx.el.div(
                    stat_tile("users", "Friends", FriendsState.friend_count),
                    stat_tile("inbox", "Requests", FriendsState.incoming_count),
                    stat_tile("send", "Sent", FriendsState.outgoing_count),
                    stat_tile(
                        "user-check", "Following", FriendsState.following_count
                    ),
                    class_name="mt-3 grid grid-cols-2 gap-3 md:grid-cols-4",
                ),
                rx.el.div(directory_search(), class_name="mt-3"),
                rx.cond(
                    FriendsState.notice != "",
                    rx.el.p(
                        FriendsState.notice,
                        class_name="mt-2 rounded-xl bg-sky-50 px-3 py-2 text-xs font-semibold text-[#1E9EF5]",
                    ),
                ),
                rx.el.div(
                    tab_button(
                        "friends", "All friends", FriendsState.friend_count
                    ),
                    tab_button(
                        "incoming", "Requests", FriendsState.incoming_count
                    ),
                    tab_button("outgoing", "Sent", FriendsState.outgoing_count),
                    tab_button(
                        "suggestions",
                        "Suggestions",
                        FriendsState.suggestions.length(),
                    ),
                    tab_button(
                        "search", "Search", FriendsState.results.length()
                    ),
                    class_name="mt-3 flex gap-1 overflow-x-auto border-b border-slate-200",
                ),
                rx.el.div(directory_body(), class_name="mt-4"),
                class_name="flex min-w-0 flex-1 flex-col",
            ),
            class_name="mx-auto flex w-full max-w-7xl gap-4 px-3 py-4 pb-24 md:px-4 md:pb-6",
        ),
        profile_drawer(),
        mobile_nav(),
        class_name="min-h-screen bg-slate-50 font-['Inter'] text-[#0D1420]",
    )
