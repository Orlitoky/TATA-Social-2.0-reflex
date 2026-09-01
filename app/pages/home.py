"""Social-first Home: story rail flowing into a dense realistic feed."""

from __future__ import annotations

import reflex as rx

from app.components.composer import composer
from app.components.danger_zone import danger_zone
from app.components.feed import feed
from app.components.header import header, mobile_nav
from app.components.rails import contacts_rail, primary_rail
from app.components.story_rail import story_rail
from app.states.auth_state import AuthState


def home_page() -> rx.Component:
    return rx.el.main(
        header(),
        rx.el.div(
            rx.el.div(
                primary_rail(),
                danger_zone(),
                class_name="hidden lg:flex lg:flex-col",
            ),
            rx.el.div(
                story_rail(),
                composer(),
                feed(),
                class_name="flex min-w-0 flex-1 flex-col gap-3",
            ),
            contacts_rail(),
            class_name="mx-auto flex w-full max-w-7xl gap-4 px-3 py-4 pb-20 md:px-4 md:pb-6",
        ),
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
