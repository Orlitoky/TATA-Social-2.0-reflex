"""Guarded account deletion control and confirmation dialog."""

from __future__ import annotations

import reflex as rx

from app.states.auth_state import AuthState


def delete_account_dialog() -> rx.Component:
    return rx.cond(
        AuthState.delete_open,
        rx.el.div(
            rx.el.div(
                rx.el.div(
                    rx.el.h2(
                        "Delete account",
                        class_name="text-base font-semibold text-[#0D1420]",
                    ),
                    rx.el.button(
                        rx.icon("x", class_name="h-4 w-4"),
                        on_click=AuthState.toggle_delete_dialog,
                        class_name="text-slate-400 hover:text-[#0D1420]",
                    ),
                    class_name="flex items-center justify-between border-b border-slate-200 px-4 py-3",
                ),
                rx.el.form(
                    rx.el.p(
                        "This permanently removes your profile, posts, stories, "
                        "messages and wallet history. This cannot be undone.",
                        class_name="text-sm text-slate-600",
                    ),
                    rx.el.label(
                        "Confirm your username",
                        class_name="mt-3 block text-xs font-semibold text-[#0D1420]",
                    ),
                    rx.el.input(
                        name="confirm_username",
                        placeholder=AuthState.username,
                        class_name="mt-1 w-full rounded-xl border border-slate-200 px-3 py-2 text-sm outline-hidden focus:border-[#1E9EF5] focus:ring-2 focus:ring-sky-100",
                    ),
                    rx.el.label(
                        "Password",
                        class_name="mt-3 block text-xs font-semibold text-[#0D1420]",
                    ),
                    rx.el.input(
                        name="password",
                        type="password",
                        placeholder="••••••••",
                        class_name="mt-1 w-full rounded-xl border border-slate-200 px-3 py-2 text-sm outline-hidden focus:border-[#1E9EF5] focus:ring-2 focus:ring-sky-100",
                    ),
                    rx.cond(
                        AuthState.delete_error != "",
                        rx.el.p(
                            AuthState.delete_error,
                            class_name="mt-2 text-sm font-medium text-red-500",
                        ),
                    ),
                    rx.el.button(
                        "Delete my account",
                        type="submit",
                        class_name="mt-4 w-full rounded-xl bg-red-500 py-2.5 text-sm font-semibold text-white hover:bg-red-600",
                    ),
                    on_submit=AuthState.delete_account,
                    reset_on_submit=True,
                    class_name="p-4",
                ),
                class_name="w-full max-w-md overflow-hidden rounded-2xl border border-slate-200 bg-white shadow-sm",
            ),
            class_name="fixed inset-0 z-50 flex items-center justify-center bg-[#0D1420]/60 p-4",
        ),
    )


def danger_zone() -> rx.Component:
    return rx.el.div(
        rx.el.button(
            rx.icon("triangle-alert", class_name="h-4 w-4"),
            rx.el.span("Delete account", class_name="text-xs font-semibold"),
            on_click=AuthState.toggle_delete_dialog,
            class_name="flex w-full items-center gap-2 rounded-xl border border-slate-200 bg-white px-3 py-2 text-slate-500 hover:border-red-300 hover:text-red-500",
        ),
        delete_account_dialog(),
        class_name="mt-3",
    )
