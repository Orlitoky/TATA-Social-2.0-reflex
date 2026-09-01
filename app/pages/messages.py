"""Messages: a focused two-pane private conversation workspace."""

from __future__ import annotations

import reflex as rx

from app.components.header import header, mobile_nav
from app.components.people import presence_dot
from app.components.ui import avatar
from app.states.messages_state import (
    ConversationRow,
    MessagesState,
    ThreadMessage,
)


def conversation_item(row: ConversationRow, **props) -> rx.Component:
    return rx.el.button(
        rx.el.div(
            avatar(row["avatar_url"], row["avatar_remote"], "size-11"),
            presence_dot(row["is_online"]),
            class_name="relative shrink-0",
        ),
        rx.el.div(
            rx.el.div(
                rx.el.p(
                    row["display_name"],
                    class_name="truncate text-sm font-semibold text-[#0D1420]",
                ),
                rx.el.span(
                    row["time_label"],
                    class_name="shrink-0 text-[10px] font-medium text-slate-400",
                ),
                class_name="flex items-center justify-between gap-2",
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
                rx.cond(
                    MessagesState.total_unread > 0,
                    rx.el.span(
                        f"{MessagesState.total_unread} unread",
                        class_name="rounded-full bg-cyan-50 px-2 py-0.5 text-[10px] font-bold text-[#0D1420]",
                    ),
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
                        "Start a private chat from the People directory.",
                        class_name="mt-1 text-xs text-slate-500",
                    ),
                    rx.el.a(
                        rx.icon("users", class_name="h-3.5 w-3.5"),
                        rx.el.span("Find people"),
                        href="/friends",
                        class_name="mt-3 flex items-center gap-1.5 rounded-full bg-[#1E9EF5] px-3 py-1.5 text-xs font-semibold text-white hover:bg-[#1888d6]",
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
            rx.el.div(
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
                item["mine"], "flex justify-end", "flex justify-start"
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
        rx.el.div(
            avatar(
                MessagesState.other_avatar,
                MessagesState.other_avatar_remote,
                "size-10",
            ),
            presence_dot(MessagesState.other_online),
            class_name="relative shrink-0",
        ),
        rx.el.div(
            rx.el.p(
                MessagesState.other_name,
                class_name="truncate text-sm font-semibold text-[#0D1420]",
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
            class_name="min-w-0 flex-1",
        ),
        rx.el.a(
            rx.icon("user", class_name="h-4 w-4"),
            href="/friends",
            class_name="flex size-9 items-center justify-center rounded-full border border-slate-200 text-slate-500 hover:border-[#1E9EF5] hover:text-[#1E9EF5]",
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
                placeholder="Write a private message…",
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
                        MessagesState.other_typing,
                        rx.el.div(
                            rx.el.span(
                                f"{MessagesState.other_name} is typing…",
                                class_name="rounded-full border border-slate-200 bg-white px-3 py-1 text-[11px] font-medium text-slate-500",
                            ),
                            class_name="mt-2 flex justify-start",
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
                    "Private threads stay between you and the person you chat with.",
                    class_name="mt-1 max-w-xs text-xs text-slate-500",
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
        rx.moment(
            interval=6000,
            on_change=lambda _value: MessagesState.poll(),
            class_name="hidden",
        ),
        mobile_nav(),
        class_name="h-dvh overflow-hidden bg-slate-50 font-['Inter'] text-[#0D1420]",
    )
