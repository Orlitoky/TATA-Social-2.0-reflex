"""People directory cards, relationship actions and the profile drawer."""

from __future__ import annotations

import reflex as rx

from app.components.ui import avatar
from app.states.friends_state import FriendsState, PersonCard


def presence_dot(is_online: rx.Var | bool) -> rx.Component:
    return rx.cond(
        is_online,
        rx.el.span(
            class_name="absolute bottom-0 right-0 size-3 rounded-full border-2 border-white bg-emerald-500",
        ),
        rx.el.span(
            class_name="absolute bottom-0 right-0 size-3 rounded-full border-2 border-white bg-slate-300",
        ),
    )


def pill_button(
    icon: str, label: str, on_click, primary: bool = True
) -> rx.Component:
    return rx.el.button(
        rx.icon(icon, class_name="h-3.5 w-3.5"),
        rx.el.span(label),
        on_click=on_click,
        class_name=(
            rx.cond(
                primary,
                "flex w-full items-center justify-center gap-1.5 rounded-full bg-[#1E9EF5] px-3 py-1.5 text-xs font-semibold text-white hover:bg-[#1888d6]",
                "flex w-full items-center justify-center gap-1.5 rounded-full border border-slate-200 px-3 py-1.5 text-xs font-semibold text-[#0D1420] hover:border-[#1E9EF5] hover:text-[#1E9EF5]",
            )
        ),
    )


def relation_actions(person: PersonCard) -> rx.Component:
    return rx.match(
        person["relation"],
        (
            "friend",
            rx.el.div(
                pill_button(
                    "message-circle",
                    "Message",
                    FriendsState.message_person(person["id"]),
                ),
                pill_button(
                    "user-minus",
                    "Remove",
                    FriendsState.unfriend(person["id"]),
                    False,
                ),
                class_name="flex gap-2",
            ),
        ),
        (
            "incoming",
            rx.el.div(
                pill_button(
                    "check",
                    "Accept",
                    FriendsState.accept_request(person["id"]),
                ),
                pill_button(
                    "x",
                    "Decline",
                    FriendsState.decline_request(person["id"]),
                    False,
                ),
                class_name="flex gap-2",
            ),
        ),
        (
            "outgoing",
            rx.el.div(
                pill_button(
                    "clock",
                    "Cancel request",
                    FriendsState.cancel_request(person["id"]),
                    False,
                ),
                class_name="flex gap-2",
            ),
        ),
        rx.el.div(
            pill_button(
                "user-plus",
                "Add friend",
                FriendsState.send_request(person["id"]),
            ),
            rx.cond(
                person["is_following"],
                pill_button(
                    "user-check",
                    "Following",
                    FriendsState.unfollow(person["id"]),
                    False,
                ),
                pill_button(
                    "plus",
                    "Follow",
                    FriendsState.follow(person["id"]),
                    False,
                ),
            ),
            class_name="flex gap-2",
        ),
    )


def person_card(person: PersonCard, **props) -> rx.Component:
    return rx.el.div(
        rx.el.button(
            rx.el.div(
                avatar(
                    person["avatar_url"], person["avatar_remote"], "size-12"
                ),
                presence_dot(person["is_online"]),
                class_name="relative shrink-0",
            ),
            rx.el.div(
                rx.el.p(
                    person["display_name"],
                    class_name="truncate text-sm font-semibold text-[#0D1420]",
                ),
                rx.el.p(
                    f"@{person['username']}",
                    class_name="truncate text-xs text-slate-500",
                ),
                rx.el.p(
                    person["status_label"],
                    class_name="mt-0.5 truncate text-[11px] font-medium text-[#22D3EE]",
                ),
                class_name="min-w-0 flex-1 text-left",
            ),
            on_click=FriendsState.open_profile(person["id"]),
            class_name="flex w-full items-center gap-3",
        ),
        rx.cond(
            person["mutuals"] > 0,
            rx.el.p(
                rx.icon(
                    "users", class_name="mr-1 inline h-3 w-3 text-slate-400"
                ),
                f"{person['mutuals']} mutual friends",
                class_name="mt-2 text-[11px] font-medium text-slate-500",
            ),
            rx.cond(
                person["bio"] != "",
                rx.el.p(
                    person["bio"],
                    class_name="mt-2 line-clamp-2 text-[11px] text-slate-500",
                ),
            ),
        ),
        rx.el.div(
            relation_actions(person),
            class_name="mt-3 border-t border-slate-100 pt-3",
        ),
        class_name="flex flex-col rounded-2xl border border-slate-200 bg-white p-3 hover:border-[#1E9EF5]/40 hover:shadow-sm",
        **props,
    )


def people_grid(rows: rx.Var, empty_text: str, empty_icon: str) -> rx.Component:
    return rx.cond(
        rows.length() > 0,
        rx.el.div(
            rx.foreach(rows, lambda p: person_card(p, key=p["id"].to_string())),
            class_name="grid grid-cols-1 gap-3 sm:grid-cols-2 xl:grid-cols-3",
        ),
        rx.el.div(
            rx.icon(empty_icon, class_name="h-6 w-6 text-slate-300"),
            rx.el.p(
                empty_text,
                class_name="mt-2 text-sm font-medium text-slate-500",
            ),
            class_name="flex flex-col items-center justify-center rounded-2xl border border-dashed border-slate-200 bg-white px-6 py-12 text-center",
        ),
    )


def people_skeleton() -> rx.Component:
    return rx.el.div(
        rx.foreach(
            [0, 1, 2, 3, 4, 5],
            lambda _: rx.el.div(
                rx.el.div(
                    rx.el.div(class_name="size-12 rounded-full bg-slate-200"),
                    rx.el.div(
                        rx.el.div(class_name="h-3 w-28 rounded bg-slate-200"),
                        rx.el.div(
                            class_name="mt-2 h-3 w-20 rounded bg-slate-200"
                        ),
                        class_name="flex-1",
                    ),
                    class_name="flex items-center gap-3",
                ),
                rx.el.div(
                    class_name="mt-4 h-7 w-full rounded-full bg-slate-200"
                ),
                class_name="animate-pulse rounded-2xl border border-slate-200 bg-white p-3",
            ),
        ),
        class_name="grid grid-cols-1 gap-3 sm:grid-cols-2 xl:grid-cols-3",
    )


def profile_stat(label: str, value: rx.Var) -> rx.Component:
    return rx.el.div(
        rx.el.p(value, class_name="text-base font-bold text-[#0D1420]"),
        rx.el.p(
            label,
            class_name="text-[11px] font-semibold uppercase tracking-wide text-slate-400",
        ),
        class_name="flex flex-col items-center rounded-xl border border-slate-100 bg-slate-50/60 px-2 py-2",
    )


def profile_drawer() -> rx.Component:
    return rx.cond(
        FriendsState.profile_open,
        rx.el.div(
            rx.el.div(
                rx.el.div(
                    rx.el.span(
                        "Profile",
                        class_name="text-sm font-semibold text-[#0D1420]",
                    ),
                    rx.el.button(
                        rx.icon("x", class_name="h-4 w-4"),
                        on_click=FriendsState.close_profile,
                        class_name="text-slate-400 hover:text-[#0D1420]",
                    ),
                    class_name="flex items-center justify-between border-b border-slate-200 px-4 py-3",
                ),
                rx.el.div(
                    rx.el.div(
                        class_name="h-20 w-full rounded-xl bg-gradient-to-r from-[#1E9EF5] to-[#22D3EE]"
                    ),
                    rx.el.div(
                        rx.el.div(
                            avatar(
                                FriendsState.profile["avatar_url"],
                                FriendsState.profile["avatar_remote"],
                                "size-16 border-4 border-white",
                            ),
                            presence_dot(FriendsState.profile["is_online"]),
                            class_name="relative -mt-8",
                        ),
                        rx.el.p(
                            FriendsState.profile["display_name"],
                            class_name="mt-2 text-base font-bold text-[#0D1420]",
                        ),
                        rx.el.p(
                            f"@{FriendsState.profile['username']}",
                            class_name="text-xs text-slate-500",
                        ),
                        rx.el.p(
                            FriendsState.profile["status_label"],
                            class_name="mt-1 text-[11px] font-semibold text-[#22D3EE]",
                        ),
                        rx.cond(
                            FriendsState.profile["bio"] != "",
                            rx.el.p(
                                FriendsState.profile["bio"],
                                class_name="mt-2 text-xs text-slate-600",
                            ),
                        ),
                        rx.cond(
                            FriendsState.profile["location"] != "",
                            rx.el.p(
                                rx.icon(
                                    "map-pin",
                                    class_name="mr-1 inline h-3 w-3 text-slate-400",
                                ),
                                FriendsState.profile["location"],
                                class_name="mt-1 text-[11px] text-slate-500",
                            ),
                        ),
                        class_name="flex flex-col items-start px-1",
                    ),
                    rx.el.div(
                        profile_stat(
                            "Friends", FriendsState.profile["friend_count"]
                        ),
                        profile_stat(
                            "Followers", FriendsState.profile["follower_count"]
                        ),
                        profile_stat(
                            "Following",
                            FriendsState.profile["following_count"],
                        ),
                        profile_stat(
                            "Posts", FriendsState.profile["post_count"]
                        ),
                        class_name="mt-3 grid grid-cols-4 gap-2",
                    ),
                    rx.el.div(
                        relation_actions(FriendsState.profile),
                        class_name="mt-3",
                    ),
                    rx.el.button(
                        rx.icon("send", class_name="h-3.5 w-3.5"),
                        rx.el.span("Message"),
                        on_click=FriendsState.message_person(
                            FriendsState.profile["id"]
                        ),
                        class_name="mt-2 flex w-full items-center justify-center gap-1.5 rounded-full border border-[#22D3EE] px-3 py-1.5 text-xs font-semibold text-[#0D1420] hover:bg-cyan-50",
                    ),
                    class_name="p-4",
                ),
                class_name="w-full max-w-sm overflow-hidden rounded-2xl border border-slate-200 bg-white shadow-sm",
            ),
            class_name="fixed inset-0 z-50 flex items-end justify-center bg-[#0D1420]/50 p-3 sm:items-center",
        ),
    )
