"""Protected personal profile page: cover-led header + owner timeline."""

from __future__ import annotations

import reflex as rx

from app.components.header import header, mobile_nav
from app.components.profile import (
    edit_panel,
    profile_header,
    profile_timeline,
)
from app.components.rails import primary_rail
from app.states.auth_state import AuthState


def profile_page() -> rx.Component:
    return rx.el.main(
        header(),
        rx.el.div(
            primary_rail("profile"),
            rx.el.div(
                profile_header(),
                profile_timeline(),
                class_name="flex min-w-0 flex-1 flex-col gap-4",
            ),
            class_name="mx-auto flex w-full max-w-5xl gap-4 px-3 py-4 pb-20 md:px-4 md:pb-6",
        ),
        edit_panel(),
        mobile_nav(),
        rx.cond(
            ~AuthState.is_authenticated & AuthState.checked,
            rx.el.div(
                rx.el.p(
                    "Redirecting to login...",
                    class_name="text-sm font-medium text-slate-500",
                ),
                class_name="fixed inset-0 z-50 flex items-center justify-center bg-white",
            ),
        ),
        class_name="min-h-screen bg-slate-50 font-['Inter'] text-[#0D1420]",
    )
