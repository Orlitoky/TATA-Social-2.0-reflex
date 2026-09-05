"""Messages: a focused two-pane private conversation workspace."""

from __future__ import annotations

import reflex as rx

from app.components.header import header, mobile_nav
from app.components.people import presence_dot
from app.components.ui import avatar
from app.states.messages_state import (
    AvatarBit,
    ConversationRow,
    FriendPick,
    MemberRow,
    MessagesState,
    ThreadMessage,
)


def cluster_avatar(bit: AvatarBit, **props) -> rx.Component:
    return rx.el.div(
        avatar(bit["url"], bit["remote"], "size-6"),
        class_name="-ml-2 rounded-full ring-2 ring-white first:ml-0",
        **props,
    )


def avatar_cluster(bits: rx.Var, member_count: rx.Var) -> rx.Component:
    return rx.el.div(
        rx.el.div(
            rx.foreach(bits, lambda bit: cluster_avatar(bit)),
            class_name="flex items-center",
        ),
        rx.el.span(
            member_count,
            class_name="flex size-6 -ml-2 items-center justify-center rounded-full bg-cyan-50 text-[10px] font-bold text-[#0D1420] ring-2 ring-white",
        ),
        class_name="flex size-11 shrink-0 flex-wrap items-center justify-center rounded-full border border-slate-200 bg-slate-50 p-0.5",
    )


def conversation_item(row: ConversationRow, **props) -> rx.Component:
    return rx.el.button(
        rx.cond(
            row["is_group"],
            avatar_cluster(row["avatars"], row["member_count"]),
            rx.el.div(
                avatar(row["avatar_url"], row["avatar_remote"], "size-11"),
                presence_dot(row["is_online"]),
                class_name="relative shrink-0",
            ),
        ),
        rx.el.div(
            rx.el.div(
                rx.cond(
                    row["is_group"],
                    rx.icon(
                        "users",
                        class_name="h-3.5 w-3.5 shrink-0 text-[#1E9EF5]",
                    ),
                ),
                rx.el.p(
                    row["display_name"],
                    class_name="truncate text-sm font-semibold text-[#0D1420]",
                ),
                rx.el.span(
                    row["time_label"],
                    class_name="shrink-0 text-[10px] font-medium text-slate-400",
                ),
                class_name="flex items-center gap-1.5",
            ),
            rx.el.p(
                row["summary"],
                class_name="truncate text-[10px] font-medium text-slate-400",
            ),
            rx.el.div(
                rx.el.p(
                    row["preview"],
                    class_name=rx.cond(
                        row["unread"] > 0,
                        "truncate text-xs font-semibold text-[#0D1420]",
                        "truncate text-xs text-slate-500",
                    ),
                ),
                rx.cond(
                    row["unread"] > 0,
                    rx.el.span(
                        row["unread"],
                        class_name="flex h-4 min-w-4 shrink-0 items-center justify-center rounded-full bg-[#1E9EF5] px-1 text-[10px] font-bold text-white",
                    ),
                ),
                class_name="mt-0.5 flex items-center justify-between gap-2",
            ),
            class_name="min-w-0 flex-1 text-left",
        ),
        on_click=MessagesState.open_conversation(row["id"]),
        class_name=rx.cond(
            MessagesState.active_id == row["id"],
            "flex w-full items-center gap-3 border-b border-slate-100 bg-sky-50 px-3 py-3",
            "flex w-full items-center gap-3 border-b border-slate-100 px-3 py-3 hover:bg-slate-50",
        ),
        **props,
    )


def conversation_list() -> rx.Component:
    return rx.el.aside(
        rx.el.div(
            rx.el.div(
                rx.el.h1(
                    "Messages", class_name="text-base font-bold text-[#0D1420]"
                ),
                rx.el.div(
                    rx.cond(
                        MessagesState.total_unread > 0,
                        rx.el.span(
                            f"{MessagesState.total_unread} unread",
                            class_name="rounded-full bg-cyan-50 px-2 py-0.5 text-[10px] font-bold text-[#0D1420]",
                        ),
                    ),
                    rx.el.button(
                        rx.icon("users-round", class_name="h-3.5 w-3.5"),
                        rx.el.span("New group"),
                        on_click=MessagesState.open_group_modal,
                        aria_label="Create a new group conversation",
                        title="Create a new group conversation",
                        class_name="flex items-center gap-1.5 rounded-full bg-[#1E9EF5] px-3 py-1.5 text-[11px] font-semibold text-white hover:bg-[#1888d6] focus:outline-hidden focus:ring-2 focus:ring-sky-200",
                    ),
                    class_name="flex items-center gap-2",
                ),
                class_name="flex items-center justify-between gap-2",
            ),
            rx.el.div(
                rx.icon(
                    "search",
                    class_name="absolute left-3 top-2.5 h-4 w-4 text-slate-400",
                ),
                rx.el.input(
                    placeholder="Search conversations",
                    default_value=MessagesState.query,
                    on_change=MessagesState.search_conversations.debounce(400),
                    class_name="w-full rounded-full border border-slate-200 bg-slate-50 py-2 pl-9 pr-3 text-sm font-medium text-[#0D1420] placeholder:text-slate-400 outline-hidden focus:border-[#1E9EF5] focus:bg-white focus:ring-2 focus:ring-sky-100",
                ),
                class_name="relative mt-2",
            ),
            class_name="shrink-0 border-b border-slate-200 px-3 py-3",
        ),
        rx.cond(
            MessagesState.loading,
            rx.el.div(
                rx.foreach(
                    [0, 1, 2, 3, 4],
                    lambda _: rx.el.div(
                        rx.el.div(
                            class_name="size-11 rounded-full bg-slate-200"
                        ),
                        rx.el.div(
                            rx.el.div(
                                class_name="h-3 w-28 rounded bg-slate-200"
                            ),
                            rx.el.div(
                                class_name="mt-2 h-3 w-40 rounded bg-slate-200"
                            ),
                            class_name="flex-1",
                        ),
                        class_name="flex animate-pulse items-center gap-3 border-b border-slate-100 px-3 py-3",
                    ),
                ),
                class_name="flex-1 overflow-y-auto",
            ),
            rx.cond(
                MessagesState.conversations.length() > 0,
                rx.el.div(
                    rx.foreach(
                        MessagesState.conversations,
                        lambda row: conversation_item(
                            row, key=row["id"].to_string()
                        ),
                    ),
                    class_name="min-h-0 flex-1 overflow-y-auto",
                ),
                rx.el.div(
                    rx.icon(
                        "message-square-dashed",
                        class_name="h-6 w-6 text-slate-300",
                    ),
                    rx.el.p(
                        "No conversations yet.",
                        class_name="mt-2 text-sm font-semibold text-[#0D1420]",
                    ),
                    rx.el.p(
                        "Start a private direct chat from the People directory, or create a group with your friends.",
                        class_name="mt-1 text-xs text-slate-500",
                    ),
                    rx.el.div(
                        rx.el.a(
                            rx.icon("users", class_name="h-3.5 w-3.5"),
                            rx.el.span("Find people"),
                            href="/friends",
                            class_name="flex items-center gap-1.5 rounded-full bg-[#1E9EF5] px-3 py-1.5 text-xs font-semibold text-white hover:bg-[#1888d6]",
                        ),
                        rx.el.button(
                            rx.icon("users-round", class_name="h-3.5 w-3.5"),
                            rx.el.span("New group"),
                            on_click=MessagesState.open_group_modal,
                            class_name="flex items-center gap-1.5 rounded-full border border-[#22D3EE] px-3 py-1.5 text-xs font-semibold text-[#0D1420] hover:bg-cyan-50",
                        ),
                        class_name="mt-3 flex flex-wrap items-center justify-center gap-2",
                    ),
                    class_name="flex flex-1 flex-col items-center justify-center px-6 text-center",
                ),
            ),
        ),
        class_name=rx.cond(
            MessagesState.has_active,
            "hidden md:flex h-full w-full md:w-80 shrink-0 flex-col border-r border-slate-200 bg-white",
            "flex h-full w-full md:w-80 shrink-0 flex-col border-r border-slate-200 bg-white",
        ),
    )


def friend_pick_row(person: FriendPick, **props) -> rx.Component:
    return rx.el.button(
        rx.el.div(
            avatar(person["avatar_url"], person["avatar_remote"], "size-9"),
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
                class_name="truncate text-[11px] text-slate-500",
            ),
            class_name="min-w-0 flex-1 text-left",
        ),
        rx.cond(
            MessagesState.selected_ids.contains(person["id"]),
            rx.el.span(
                rx.icon("check", class_name="h-3.5 w-3.5 text-white"),
                class_name="flex size-5 shrink-0 items-center justify-center rounded-md bg-[#1E9EF5]",
            ),
            rx.el.span(
                class_name="size-5 shrink-0 rounded-md border border-slate-300 bg-white",
            ),
        ),
        on_click=MessagesState.toggle_member(person["id"]),
        class_name=rx.cond(
            MessagesState.selected_ids.contains(person["id"]),
            "flex w-full items-center gap-3 rounded-xl border border-[#1E9EF5] bg-sky-50 px-2.5 py-2",
            "flex w-full items-center gap-3 rounded-xl border border-slate-200 bg-white px-2.5 py-2 hover:border-[#22D3EE]",
        ),
        **props,
    )


def selected_chip(person: FriendPick, **props) -> rx.Component:
    return rx.el.button(
        avatar(person["avatar_url"], person["avatar_remote"], "size-5"),
        rx.el.span(
            person["display_name"],
            class_name="max-w-24 truncate text-[11px] font-semibold text-[#0D1420]",
        ),
        rx.icon("x", class_name="h-3 w-3 text-slate-400"),
        on_click=MessagesState.toggle_member(person["id"]),
        class_name="flex items-center gap-1.5 rounded-full border border-cyan-200 bg-cyan-50 px-2 py-1",
        **props,
    )


def group_create_sheet() -> rx.Component:
    return rx.cond(
        MessagesState.group_open,
        rx.el.div(
            rx.el.div(
                rx.el.div(
                    rx.el.div(
                        rx.el.p(
                            "New group",
                            class_name="text-sm font-bold text-[#0D1420]",
                        ),
                        rx.el.p(
                            "Private group chat with at least three people.",
                            class_name="text-[11px] text-slate-500",
                        ),
                        class_name="min-w-0",
                    ),
                    rx.el.button(
                        rx.icon("x", class_name="h-4 w-4"),
                        on_click=MessagesState.close_group_modal,
                        aria_label="Close",
                        class_name="text-slate-400 hover:text-[#0D1420]",
                    ),
                    class_name="flex items-start justify-between gap-3 border-b border-slate-200 px-4 py-3",
                ),
                rx.el.div(
                    rx.el.label(
                        "Group name",
                        html_for="group-name",
                        class_name="text-[11px] font-semibold uppercase tracking-wide text-slate-400",
                    ),
                    rx.el.input(
                        id="group-name",
                        placeholder="Weekend crew",
                        default_value=MessagesState.group_title,
                        max_length=120,
                        on_change=MessagesState.change_group_title.debounce(
                            250
                        ),
                        class_name="mt-1 w-full rounded-xl border border-slate-200 bg-slate-50 px-3 py-2 text-sm font-medium text-[#0D1420] placeholder:text-slate-400 outline-hidden focus:border-[#1E9EF5] focus:bg-white focus:ring-2 focus:ring-sky-100",
                    ),
                    rx.el.div(
                        rx.icon(
                            "search",
                            class_name="absolute left-3 top-2.5 h-4 w-4 text-slate-400",
                        ),
                        rx.el.input(
                            placeholder="Search your friends",
                            default_value=MessagesState.group_query,
                            on_change=MessagesState.search_group_friends.debounce(
                                400
                            ),
                            class_name="w-full rounded-full border border-slate-200 bg-slate-50 py-2 pl-9 pr-3 text-sm font-medium text-[#0D1420] placeholder:text-slate-400 outline-hidden focus:border-[#1E9EF5] focus:bg-white focus:ring-2 focus:ring-sky-100",
                        ),
                        class_name="relative mt-3",
                    ),
                    rx.el.div(
                        rx.el.span(
                            f"{MessagesState.selected_count} selected",
                            class_name="text-[11px] font-semibold text-slate-500",
                        ),
                        rx.el.span(
                            "Minimum 2 friends",
                            class_name="text-[11px] font-medium text-slate-400",
                        ),
                        class_name="mt-3 flex items-center justify-between gap-2",
                    ),
                    rx.cond(
                        MessagesState.selected_people.length() > 0,
                        rx.el.div(
                            rx.foreach(
                                MessagesState.selected_people,
                                lambda person: selected_chip(
                                    person, key=person["id"].to_string()
                                ),
                            ),
                            class_name="mt-2 flex flex-wrap gap-1.5",
                        ),
                    ),
                    rx.cond(
                        MessagesState.friends_loading,
                        rx.el.div(
                            rx.foreach(
                                [0, 1, 2, 3],
                                lambda _: rx.el.div(
                                    class_name="h-12 w-full animate-pulse rounded-xl bg-slate-100"
                                ),
                            ),
                            class_name="mt-3 flex flex-col gap-2",
                        ),
                        rx.cond(
                            MessagesState.friend_options.length() > 0,
                            rx.el.div(
                                rx.foreach(
                                    MessagesState.friend_options,
                                    lambda person: friend_pick_row(
                                        person, key=person["id"].to_string()
                                    ),
                                ),
                                class_name="mt-3 flex max-h-56 flex-col gap-2 overflow-y-auto pr-1",
                            ),
                            rx.el.div(
                                rx.icon(
                                    "user-round-search",
                                    class_name="h-5 w-5 text-slate-300",
                                ),
                                rx.el.p(
                                    "No friends match that search.",
                                    class_name="mt-1 text-xs font-medium text-slate-500",
                                ),
                                rx.el.a(
                                    "Find people",
                                    href="/friends",
                                    class_name="mt-2 text-[11px] font-semibold text-[#1E9EF5]",
                                ),
                                class_name="mt-3 flex flex-col items-center justify-center rounded-xl border border-dashed border-slate-200 px-4 py-8 text-center",
                            ),
                        ),
                    ),
                    rx.cond(
                        MessagesState.group_error != "",
                        rx.el.p(
                            MessagesState.group_error,
                            class_name="mt-2 text-[11px] font-semibold text-red-500",
                        ),
                    ),
                    class_name="px-4 py-3",
                ),
                rx.el.div(
                    rx.el.button(
                        "Cancel",
                        on_click=MessagesState.close_group_modal,
                        class_name="flex-1 rounded-full border border-slate-200 px-3 py-2 text-xs font-semibold text-[#0D1420] hover:border-slate-300",
                    ),
                    rx.el.button(
                        rx.cond(
                            MessagesState.group_saving,
                            rx.el.span("Creating…"),
                            rx.el.span("Create group"),
                        ),
                        on_click=MessagesState.create_group,
                        disabled=(~MessagesState.can_create_group)
                        | MessagesState.group_saving,
                        class_name="flex-1 rounded-full bg-[#1E9EF5] px-3 py-2 text-xs font-semibold text-white hover:bg-[#1888d6] disabled:cursor-not-allowed disabled:bg-slate-200 disabled:text-slate-400",
                    ),
                    class_name="flex items-center gap-2 border-t border-slate-200 px-4 py-3 pb-[max(0.75rem,env(safe-area-inset-bottom))]",
                ),
                class_name="w-full max-w-md overflow-hidden rounded-t-2xl border border-slate-200 bg-white shadow-sm sm:rounded-2xl",
            ),
            class_name="fixed inset-0 z-50 flex items-end justify-center bg-[#0D1420]/50 sm:items-center sm:p-4",
        ),
    )


def member_row(person: MemberRow, **props) -> rx.Component:
    return rx.el.div(
        rx.el.div(
            avatar(person["avatar_url"], person["avatar_remote"], "size-9"),
            presence_dot(person["is_online"]),
            class_name="relative shrink-0",
        ),
        rx.el.div(
            rx.el.div(
                rx.el.p(
                    person["display_name"],
                    class_name="truncate text-sm font-semibold text-[#0D1420]",
                ),
                rx.cond(
                    person["is_me"],
                    rx.el.span(
                        "You",
                        class_name="rounded-full bg-slate-100 px-1.5 py-0.5 text-[10px] font-semibold text-slate-500",
                    ),
                ),
                class_name="flex items-center gap-1.5",
            ),
            rx.el.p(
                f"@{person['username']} · {person['presence']}",
                class_name="truncate text-[11px] text-slate-500",
            ),
            class_name="min-w-0 flex-1",
        ),
        rx.el.span(
            person["role"],
            class_name=rx.cond(
                person["role"] == "admin",
                "w-fit shrink-0 rounded-full bg-cyan-50 px-2 py-0.5 text-[10px] font-bold uppercase tracking-wide text-[#0D1420]",
                "w-fit shrink-0 rounded-full bg-slate-50 px-2 py-0.5 text-[10px] font-semibold uppercase tracking-wide text-slate-400",
            ),
        ),
        class_name="flex items-center gap-3 border-b border-slate-100 px-4 py-2.5 last:border-b-0",
        **props,
    )


def members_panel() -> rx.Component:
    return rx.cond(
        MessagesState.members_open,
        rx.el.div(
            rx.el.div(
                rx.el.div(
                    rx.el.div(
                        rx.el.p(
                            MessagesState.group_title_active,
                            class_name="truncate text-sm font-bold text-[#0D1420]",
                        ),
                        rx.el.p(
                            MessagesState.group_summary,
                            class_name="text-[11px] font-medium text-slate-500",
                        ),
                        class_name="min-w-0",
                    ),
                    rx.el.button(
                        rx.icon("x", class_name="h-4 w-4"),
                        on_click=MessagesState.toggle_members_panel,
                        aria_label="Close members",
                        class_name="text-slate-400 hover:text-[#0D1420]",
                    ),
                    class_name="flex items-start justify-between gap-3 border-b border-slate-200 px-4 py-3",
                ),
                rx.el.div(
                    rx.foreach(
                        MessagesState.group_avatars,
                        lambda bit: cluster_avatar(bit),
                    ),
                    class_name="flex items-center px-4 pt-3",
                ),
                rx.el.div(
                    rx.foreach(
                        MessagesState.group_members,
                        lambda person: member_row(
                            person, key=person["id"].to_string()
                        ),
                    ),
                    class_name="mt-2 max-h-72 overflow-y-auto",
                ),
                class_name="w-full max-w-md overflow-hidden rounded-t-2xl border border-slate-200 bg-white pb-[max(0.5rem,env(safe-area-inset-bottom))] shadow-sm sm:rounded-2xl",
            ),
            class_name="fixed inset-0 z-50 flex items-end justify-center bg-[#0D1420]/50 sm:items-center sm:p-4",
        ),
    )


def message_bubble(item: ThreadMessage) -> rx.Component:
    return rx.el.div(
        rx.cond(
            item["show_date"],
            rx.el.div(
                rx.el.span(
                    item["date_label"],
                    class_name="rounded-full bg-slate-100 px-2 py-0.5 text-[10px] font-semibold text-slate-500",
                ),
                class_name="my-2 flex justify-center",
            ),
        ),
        rx.el.div(
            rx.cond(
                item["show_sender"],
                rx.el.div(
                    avatar(
                        item["sender_avatar"],
                        item["sender_avatar_remote"],
                        "size-6",
                    ),
                    class_name="mr-1.5 shrink-0 self-end",
                ),
                rx.cond(
                    item["mine"],
                    rx.fragment(),
                    rx.el.div(
                        class_name=rx.cond(
                            MessagesState.active_is_group,
                            "mr-1.5 size-6 shrink-0",
                            "hidden",
                        )
                    ),
                ),
            ),
            rx.el.div(
                rx.cond(
                    item["show_sender"],
                    rx.el.p(
                        item["sender_name"],
                        class_name="mb-0.5 text-[11px] font-bold text-[#1E9EF5]",
                    ),
                ),
                rx.el.p(
                    item["body"],
                    class_name="whitespace-pre-wrap text-sm font-medium",
                ),
                rx.el.div(
                    rx.el.span(
                        item["time_label"],
                        class_name=rx.cond(
                            item["mine"],
                            "text-[10px] text-white/70",
                            "text-[10px] text-slate-400",
                        ),
                    ),
                    rx.cond(
                        item["mine"],
                        rx.match(
                            item["receipt"],
                            (
                                "read",
                                rx.icon(
                                    "check-check",
                                    class_name="h-3 w-3 text-[#22D3EE]",
                                ),
                            ),
                            (
                                "delivered",
                                rx.icon(
                                    "check-check",
                                    class_name="h-3 w-3 text-white/70",
                                ),
                            ),
                            rx.icon(
                                "check", class_name="h-3 w-3 text-white/70"
                            ),
                        ),
                    ),
                    class_name="mt-1 flex items-center justify-end gap-1",
                ),
                class_name=rx.cond(
                    item["mine"],
                    "max-w-[78%] rounded-2xl rounded-br-sm bg-[#1E9EF5] px-3 py-2 text-white",
                    "max-w-[78%] rounded-2xl rounded-bl-sm border border-slate-200 bg-white px-3 py-2 text-[#0D1420]",
                ),
            ),
            class_name=rx.cond(
                item["mine"],
                "flex justify-end",
                "flex items-end justify-start",
            ),
        ),
        class_name="w-full",
    )


def thread_header() -> rx.Component:
    return rx.el.div(
        rx.el.button(
            rx.icon("arrow-left", class_name="h-4 w-4"),
            on_click=MessagesState.back_to_list,
            class_name="flex size-8 items-center justify-center rounded-full text-slate-500 hover:bg-slate-100 md:hidden",
        ),
        rx.cond(
            MessagesState.active_is_group,
            avatar_cluster(
                MessagesState.group_avatars, MessagesState.group_member_count
            ),
            rx.el.div(
                avatar(
                    MessagesState.other_avatar,
                    MessagesState.other_avatar_remote,
                    "size-10",
                ),
                presence_dot(MessagesState.other_online),
                class_name="relative shrink-0",
            ),
        ),
        rx.el.div(
            rx.el.p(
                rx.cond(
                    MessagesState.active_is_group,
                    MessagesState.group_title_active,
                    MessagesState.other_name,
                ),
                class_name="truncate text-sm font-semibold text-[#0D1420]",
            ),
            rx.cond(
                MessagesState.active_is_group,
                rx.cond(
                    MessagesState.group_typing != "",
                    rx.el.p(
                        MessagesState.group_typing,
                        class_name="truncate text-[11px] font-semibold text-[#22D3EE]",
                    ),
                    rx.el.p(
                        MessagesState.group_summary,
                        class_name="truncate text-[11px] font-medium text-slate-500",
                    ),
                ),
                rx.cond(
                    MessagesState.other_typing,
                    rx.el.p(
                        "typing…",
                        class_name="text-[11px] font-semibold text-[#22D3EE]",
                    ),
                    rx.el.p(
                        MessagesState.other_status,
                        class_name="text-[11px] font-medium text-slate-500",
                    ),
                ),
            ),
            class_name="min-w-0 flex-1",
        ),
        rx.cond(
            MessagesState.active_is_group,
            rx.el.button(
                rx.icon("users-round", class_name="h-4 w-4"),
                on_click=MessagesState.toggle_members_panel,
                aria_label="View group members",
                title="View group members",
                class_name="flex size-9 items-center justify-center rounded-full border border-slate-200 text-slate-500 hover:border-[#1E9EF5] hover:text-[#1E9EF5]",
            ),
            rx.el.a(
                rx.icon("user", class_name="h-4 w-4"),
                href="/friends",
                class_name="flex size-9 items-center justify-center rounded-full border border-slate-200 text-slate-500 hover:border-[#1E9EF5] hover:text-[#1E9EF5]",
            ),
        ),
        class_name="flex shrink-0 items-center gap-3 border-b border-slate-200 bg-white px-3 py-2.5",
    )


def composer_bar() -> rx.Component:
    return rx.el.div(
        rx.cond(
            MessagesState.error != "",
            rx.el.p(
                MessagesState.error,
                class_name="mb-1 text-[11px] font-semibold text-red-500",
            ),
        ),
        rx.el.div(
            rx.el.input(
                placeholder=rx.cond(
                    MessagesState.active_is_group,
                    "Message this private group…",
                    "Write a private message…",
                ),
                default_value="",
                on_change=MessagesState.change_draft.debounce(300),
                class_name="min-w-0 flex-1 rounded-full border border-slate-200 bg-slate-50 px-4 py-2.5 text-sm font-medium text-[#0D1420] placeholder:text-slate-400 outline-hidden focus:border-[#1E9EF5] focus:bg-white focus:ring-2 focus:ring-sky-100",
            ),
            rx.el.button(
                rx.icon("send", class_name="h-4 w-4"),
                on_click=MessagesState.send_message,
                class_name="flex size-10 shrink-0 items-center justify-center rounded-full bg-[#1E9EF5] text-white hover:bg-[#1888d6]",
            ),
            class_name="flex items-center gap-2",
        ),
        class_name="shrink-0 border-t border-slate-200 bg-white px-3 py-2.5",
    )


def thread_panel() -> rx.Component:
    return rx.el.section(
        rx.cond(
            MessagesState.has_active,
            rx.el.div(
                thread_header(),
                rx.el.div(
                    rx.cond(
                        MessagesState.has_more,
                        rx.el.div(
                            rx.el.button(
                                "Load earlier messages",
                                on_click=MessagesState.load_older,
                                class_name="rounded-full border border-slate-200 bg-white px-3 py-1 text-[11px] font-semibold text-slate-500 hover:border-[#1E9EF5] hover:text-[#1E9EF5]",
                            ),
                            class_name="flex justify-center pb-2",
                        ),
                    ),
                    rx.cond(
                        MessagesState.messages.length() > 0,
                        rx.el.div(
                            rx.foreach(MessagesState.messages, message_bubble),
                            class_name="flex flex-col gap-1.5",
                        ),
                        rx.el.div(
                            rx.icon(
                                "message-circle-plus",
                                class_name="h-6 w-6 text-slate-300",
                            ),
                            rx.el.p(
                                "No messages yet — say hello.",
                                class_name="mt-2 text-sm font-medium text-slate-500",
                            ),
                            class_name="flex h-full flex-col items-center justify-center text-center",
                        ),
                    ),
                    rx.cond(
                        MessagesState.active_is_group,
                        rx.cond(
                            MessagesState.group_typing != "",
                            rx.el.div(
                                rx.el.span(
                                    MessagesState.group_typing,
                                    class_name="rounded-full border border-slate-200 bg-white px-3 py-1 text-[11px] font-medium text-slate-500",
                                ),
                                class_name="mt-2 flex justify-start",
                            ),
                        ),
                        rx.cond(
                            MessagesState.other_typing,
                            rx.el.div(
                                rx.el.span(
                                    f"{MessagesState.other_name} is typing…",
                                    class_name="rounded-full border border-slate-200 bg-white px-3 py-1 text-[11px] font-medium text-slate-500",
                                ),
                                class_name="mt-2 flex justify-start",
                            ),
                        ),
                    ),
                    class_name="min-h-0 flex-1 overflow-y-auto bg-slate-50 px-3 py-3",
                ),
                composer_bar(),
                class_name="flex h-full min-h-0 flex-1 flex-col",
            ),
            rx.el.div(
                rx.icon("messages-square", class_name="h-8 w-8 text-slate-300"),
                rx.el.p(
                    "Select a conversation",
                    class_name="mt-3 text-base font-semibold text-[#0D1420]",
                ),
                rx.el.p(
                    "Private direct and group conversations stay between you and the members you chat with.",
                    class_name="mt-1 max-w-xs text-xs text-slate-500",
                ),
                rx.el.button(
                    rx.icon("users-round", class_name="h-3.5 w-3.5"),
                    rx.el.span("New group"),
                    on_click=MessagesState.open_group_modal,
                    class_name="mt-3 flex items-center gap-1.5 rounded-full bg-[#1E9EF5] px-3 py-1.5 text-xs font-semibold text-white hover:bg-[#1888d6]",
                ),
                class_name="flex h-full flex-1 flex-col items-center justify-center bg-slate-50 px-6 text-center",
            ),
        ),
        class_name=rx.cond(
            MessagesState.has_active,
            "flex h-full min-w-0 flex-1 flex-col",
            "hidden md:flex h-full min-w-0 flex-1 flex-col",
        ),
    )


def messages_page() -> rx.Component:
    return rx.el.main(
        header(),
        rx.el.div(
            rx.el.div(
                conversation_list(),
                thread_panel(),
                class_name="flex h-full w-full overflow-hidden rounded-2xl border border-slate-200 bg-white shadow-sm",
            ),
            class_name="mx-auto h-[calc(100dvh-4rem)] w-full max-w-7xl px-0 py-0 pb-14 md:px-4 md:py-4 md:pb-4",
        ),
        group_create_sheet(),
        members_panel(),
        rx.moment(
            interval=6000,
            on_change=lambda _value: MessagesState.poll(),
            class_name="hidden",
        ),
        mobile_nav(),
        class_name="h-dvh overflow-hidden bg-slate-50 font-['Inter'] text-[#0D1420]",
    )
