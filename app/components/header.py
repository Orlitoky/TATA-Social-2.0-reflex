"""Sticky TATA header: logo, global search, notifications, messages, avatar."""

from __future__ import annotations

import reflex as rx

from app.components.ui import avatar
from app.states.auth_state import AuthState
from app.states.social_state import NotificationRow, SocialState, SuggestionRow


def logo() -> rx.Component:
    return rx.el.a(
        rx.el.div(
            rx.icon("radio-tower", class_name="h-4 w-4 text-white"),
            class_name="flex size-9 items-center justify-center rounded-xl bg-[#1E9EF5]",
        ),
        rx.el.span(
            "TATA",
            class_name="hidden sm:block text-lg font-bold tracking-tight text-[#0D1420]",
        ),
        href="/",
        class_name="flex items-center gap-2",
    )


def suggestion_item(item: SuggestionRow) -> rx.Component:
    return rx.el.div(
        rx.cond(
            item["kind"] == "person",
            avatar(item["avatar_url"], item["avatar_remote"], "size-8"),
            rx.el.div(
                rx.icon("file-text", class_name="h-4 w-4 text-[#1E9EF5]"),
                class_name="flex size-8 items-center justify-center rounded-full bg-sky-50",
            ),
        ),
        rx.el.div(
            rx.el.p(
                item["label"],
                class_name="text-sm font-semibold text-[#0D1420] truncate",
            ),
            rx.el.p(
                item["detail"], class_name="text-xs text-slate-500 truncate"
            ),
            class_name="min-w-0 flex-1",
        ),
        class_name="flex items-center gap-3 px-3 py-2 hover:bg-sky-50 cursor-pointer",
    )


def search_box() -> rx.Component:
    return rx.el.div(
        rx.el.div(
            rx.icon(
                "search",
                class_name="absolute left-3 top-2.5 h-4 w-4 text-slate-400",
            ),
            rx.el.input(
                placeholder="Search people and posts",
                default_value=SocialState.query,
                on_change=SocialState.search.debounce(350),
                class_name="w-full rounded-full border border-slate-200 bg-slate-50 py-2 pl-9 pr-3 text-sm font-medium text-[#0D1420] placeholder:text-slate-400 focus:border-[#1E9EF5] focus:bg-white focus:ring-2 focus:ring-sky-100 outline-hidden",
            ),
            class_name="relative",
        ),
        rx.cond(
            SocialState.search_open & (SocialState.suggestions.length() > 0),
            rx.el.div(
                rx.el.div(
                    rx.el.span(
                        "Suggestions",
                        class_name="text-xs font-semibold uppercase tracking-wide text-slate-400",
                    ),
                    rx.el.button(
                        rx.icon("x", class_name="h-3.5 w-3.5"),
                        on_click=SocialState.close_search,
                        class_name="text-slate-400 hover:text-[#0D1420]",
                    ),
                    class_name="flex items-center justify-between border-b border-slate-100 px-3 py-2",
                ),
                rx.foreach(SocialState.suggestions, suggestion_item),
                class_name="absolute z-40 mt-2 w-full overflow-hidden rounded-2xl border border-slate-200 bg-white shadow-sm",
            ),
        ),
        class_name="relative w-full max-w-md",
    )


def notification_item(item: NotificationRow) -> rx.Component:
    return rx.el.div(
        avatar(item["avatar_url"], item["avatar_remote"], "size-9"),
        rx.el.div(
            rx.el.p(
                rx.el.span(
                    item["actor"], class_name="font-semibold text-[#0D1420]"
                ),
                " ",
                rx.el.span(item["text"], class_name="text-slate-600"),
                class_name="text-sm",
            ),
            rx.el.p(
                item["time_label"], class_name="text-xs text-slate-400 mt-0.5"
            ),
            class_name="min-w-0 flex-1",
        ),
        rx.icon(item["icon"], class_name="h-4 w-4 text-[#22D3EE] shrink-0"),
        class_name="flex items-start gap-3 border-b border-slate-100 px-3 py-3 last:border-0 hover:bg-sky-50/60",
    )


def notifications_menu() -> rx.Component:
    return rx.el.div(
        rx.el.button(
            rx.icon("bell", class_name="h-5 w-5 text-[#0D1420]"),
            rx.cond(
                SocialState.notification_count > 0,
                rx.el.span(
                    SocialState.notification_count,
                    class_name="absolute -right-0.5 -top-0.5 flex h-4 min-w-4 items-center justify-center rounded-full bg-[#1E9EF5] px-1 text-[10px] font-bold text-white",
                ),
            ),
            on_click=SocialState.toggle_notifications,
            class_name="relative flex size-10 items-center justify-center rounded-full bg-slate-50 hover:bg-sky-50",
        ),
        rx.cond(
            SocialState.notifications_open,
            rx.el.div(
                rx.el.div(
                    rx.el.span(
                        "Activity",
                        class_name="text-sm font-semibold text-[#0D1420]",
                    ),
                    rx.el.button(
                        rx.icon("x", class_name="h-4 w-4"),
                        on_click=SocialState.toggle_notifications,
                        class_name="text-slate-400 hover:text-[#0D1420]",
                    ),
                    class_name="flex items-center justify-between border-b border-slate-100 px-3 py-2",
                ),
                rx.cond(
                    SocialState.notification_count > 0,
                    rx.el.div(
                        rx.foreach(
                            SocialState.notifications, notification_item
                        ),
                        class_name="max-h-96 overflow-y-auto",
                    ),
                    rx.el.p(
                        "No activity yet. Post something to get started.",
                        class_name="px-4 py-6 text-sm text-slate-500",
                    ),
                ),
                class_name="absolute right-0 z-40 mt-2 w-80 overflow-hidden rounded-2xl border border-slate-200 bg-white shadow-sm",
            ),
        ),
        class_name="relative",
    )


def account_menu() -> rx.Component:
    return rx.el.div(
        rx.el.a(
            avatar(AuthState.avatar_url, AuthState.avatar_remote, "size-10"),
            rx.el.div(
                rx.el.p(
                    AuthState.display_name,
                    class_name="text-sm font-semibold text-[#0D1420] leading-tight",
                ),
                rx.el.p(
                    f"@{AuthState.username}",
                    class_name="text-xs text-slate-500 leading-tight",
                ),
                class_name="hidden lg:block",
            ),
            href="/profile",
            title="Your profile",
            class_name="flex items-center gap-3 rounded-full pr-1 hover:opacity-90",
        ),
        rx.el.button(
            rx.icon("log-out", class_name="h-4 w-4"),
            rx.el.span("Log out", class_name="hidden lg:block"),
            on_click=AuthState.logout,
            class_name="flex items-center gap-2 rounded-full border border-slate-200 px-3 py-2 text-sm font-semibold text-[#0D1420] hover:border-[#1E9EF5] hover:text-[#1E9EF5]",
        ),
        class_name="flex items-center gap-3",
    )


def mobile_nav() -> rx.Component:
    return rx.el.nav(
        rx.el.a(
            rx.icon("house", class_name="h-5 w-5"),
            rx.el.span("Home", class_name="text-[10px] font-semibold"),
            href="/",
            class_name="flex flex-1 flex-col items-center gap-0.5 py-2 text-[#1E9EF5]",
        ),
        rx.el.button(
            rx.icon("search", class_name="h-5 w-5"),
            rx.el.span("Search", class_name="text-[10px] font-semibold"),
            on_click=SocialState.toggle_mobile_menu,
            class_name="flex flex-1 flex-col items-center gap-0.5 py-2 text-slate-500",
        ),
        rx.el.a(
            rx.icon("users", class_name="h-5 w-5"),
            rx.el.span("People", class_name="text-[10px] font-semibold"),
            href="/friends",
            class_name="flex flex-1 flex-col items-center gap-0.5 py-2 text-slate-500",
        ),
        rx.el.a(
            rx.icon("message-circle", class_name="h-5 w-5"),
            rx.cond(
                SocialState.unread_messages > 0,
                rx.el.span(
                    SocialState.unread_messages,
                    class_name="absolute -top-0.5 rounded-full bg-[#1E9EF5] px-1 text-[10px] font-bold text-white",
                ),
            ),
            rx.el.span("Chats", class_name="text-[10px] font-semibold"),
            href="/messages",
            class_name="relative flex flex-1 flex-col items-center gap-0.5 py-2 text-slate-500",
        ),
        rx.el.a(
            rx.icon("user", class_name="h-5 w-5"),
            rx.el.span("Profile", class_name="text-[10px] font-semibold"),
            href="/profile",
            class_name="flex flex-1 flex-col items-center gap-0.5 py-2 text-slate-500",
        ),
        rx.el.button(
            rx.icon("log-out", class_name="h-5 w-5"),
            rx.el.span("Log out", class_name="text-[10px] font-semibold"),
            on_click=AuthState.logout,
            class_name="flex flex-1 flex-col items-center gap-0.5 py-2 text-slate-500",
        ),
        class_name="fixed bottom-0 left-0 right-0 z-30 flex border-t border-slate-200 bg-white md:hidden",
    )


def header() -> rx.Component:
    return rx.el.header(
        rx.el.div(
            logo(),
            rx.el.div(
                search_box(),
                class_name="hidden md:flex flex-1 justify-center px-4",
            ),
            rx.el.div(
                rx.el.a(
                    rx.icon("users", class_name="h-5 w-5 text-[#0D1420]"),
                    href="/friends",
                    title="Friends",
                    class_name="hidden sm:flex size-10 items-center justify-center rounded-full bg-slate-50 hover:bg-sky-50",
                ),
                rx.el.a(
                    rx.icon(
                        "message-circle", class_name="h-5 w-5 text-[#0D1420]"
                    ),
                    rx.cond(
                        SocialState.unread_messages > 0,
                        rx.el.span(
                            SocialState.unread_messages,
                            class_name="absolute -right-0.5 -top-0.5 flex h-4 min-w-4 items-center justify-center rounded-full bg-[#22D3EE] px-1 text-[10px] font-bold text-[#0D1420]",
                        ),
                    ),
                    href="/messages",
                    title="Messages",
                    class_name="relative hidden sm:flex size-10 items-center justify-center rounded-full bg-slate-50 hover:bg-sky-50",
                ),
                notifications_menu(),
                account_menu(),
                class_name="flex items-center gap-2",
            ),
            class_name="mx-auto flex h-16 w-full max-w-7xl items-center justify-between gap-3 px-4",
        ),
        rx.cond(
            SocialState.mobile_menu_open,
            rx.el.div(
                search_box(),
                class_name="border-t border-slate-200 bg-white px-4 py-3 md:hidden",
            ),
        ),
        class_name="sticky top-0 z-30 w-full border-b border-slate-200 bg-white/95 backdrop-blur",
    )
