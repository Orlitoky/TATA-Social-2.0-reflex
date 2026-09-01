"""Login and signup routes."""

from __future__ import annotations

import reflex as rx

from app.states.auth_state import AuthState


def brand_panel() -> rx.Component:
    return rx.el.div(
        rx.el.div(
            rx.el.div(
                rx.icon("radio-tower", class_name="h-5 w-5 text-white"),
                class_name="flex size-11 items-center justify-center rounded-2xl bg-white/15",
            ),
            rx.el.span(
                "TATA",
                class_name="text-2xl font-bold tracking-tight text-white",
            ),
            class_name="flex items-center gap-3",
        ),
        rx.el.h1(
            "Stories, posts and people — all in one crisp feed.",
            class_name="mt-8 text-3xl font-bold leading-tight text-white",
        ),
        rx.el.p(
            "Share moments that expire in 24 hours, post photos and video, "
            "react six ways and keep the conversation threaded.",
            class_name="mt-3 text-sm font-medium text-white/80",
        ),
        rx.el.div(
            rx.el.div(
                rx.icon("circle-play", class_name="h-4 w-4 text-[#22D3EE]"),
                rx.el.span(
                    "Immersive story rail",
                    class_name="text-sm font-semibold text-white",
                ),
                class_name="flex items-center gap-2",
            ),
            rx.el.div(
                rx.icon("shield-check", class_name="h-4 w-4 text-[#22D3EE]"),
                rx.el.span(
                    "PBKDF2 hashed credentials",
                    class_name="text-sm font-semibold text-white",
                ),
                class_name="flex items-center gap-2",
            ),
            rx.el.div(
                rx.icon("coins", class_name="h-4 w-4 text-[#22D3EE]"),
                rx.el.span(
                    "500 virtual TATA Coins on signup",
                    class_name="text-sm font-semibold text-white",
                ),
                class_name="flex items-center gap-2",
            ),
            class_name="mt-8 flex flex-col gap-3",
        ),
        class_name="hidden md:flex md:w-1/2 md:flex-col md:justify-center bg-[#1E9EF5] p-10",
    )


def field(
    label: str, name: str, placeholder: str, field_type: str = "text"
) -> rx.Component:
    return rx.el.div(
        rx.el.label(
            label, class_name="block text-xs font-semibold text-[#0D1420]"
        ),
        rx.el.input(
            name=name,
            type=field_type,
            placeholder=placeholder,
            class_name="mt-1 w-full rounded-xl border border-slate-200 bg-slate-50 px-3 py-2.5 text-sm font-medium text-[#0D1420] placeholder:text-slate-400 outline-hidden focus:border-[#1E9EF5] focus:bg-white focus:ring-2 focus:ring-sky-100",
        ),
        class_name="mt-3",
    )


def error_banner() -> rx.Component:
    return rx.cond(
        AuthState.error != "",
        rx.el.div(
            rx.icon("circle-alert", class_name="h-4 w-4 text-red-500"),
            rx.el.span(
                AuthState.error, class_name="text-sm font-medium text-red-600"
            ),
            class_name="mt-3 flex items-center gap-2 rounded-xl bg-red-50 px-3 py-2",
        ),
    )


def auth_shell(card: rx.Component) -> rx.Component:
    return rx.el.main(
        brand_panel(),
        rx.el.div(
            card,
            class_name="flex w-full items-center justify-center p-6 md:w-1/2",
        ),
        class_name="flex min-h-screen bg-white font-['Inter'] text-[#0D1420]",
    )


def login_page() -> rx.Component:
    return auth_shell(
        rx.el.div(
            rx.el.h2(
                "Welcome back", class_name="text-2xl font-bold text-[#0D1420]"
            ),
            rx.el.p(
                "Log in with your email or username.",
                class_name="mt-1 text-sm text-slate-500",
            ),
            rx.el.form(
                field("Email or username", "identifier", "you@tata.app"),
                field("Password", "password", "••••••••", "password"),
                error_banner(),
                rx.el.button(
                    rx.cond(AuthState.processing, "Signing in...", "Log in"),
                    type="submit",
                    disabled=AuthState.processing,
                    class_name="mt-5 w-full rounded-xl bg-[#1E9EF5] py-2.5 text-sm font-semibold text-white hover:bg-sky-600 disabled:opacity-60",
                ),
                on_submit=AuthState.login,
                reset_on_submit=False,
            ),
            rx.el.p(
                rx.el.span("New to TATA? ", class_name="text-slate-500"),
                rx.el.a(
                    "Create an account",
                    href="/signup",
                    class_name="font-semibold text-[#1E9EF5] hover:underline",
                ),
                class_name="mt-4 text-sm",
            ),
            class_name="w-full max-w-sm rounded-2xl border border-slate-200 bg-white p-6",
        )
    )


def signup_page() -> rx.Component:
    return auth_shell(
        rx.el.div(
            rx.el.h2(
                "Create your account",
                class_name="text-2xl font-bold text-[#0D1420]",
            ),
            rx.el.p(
                "Join the feed in under a minute.",
                class_name="mt-1 text-sm text-slate-500",
            ),
            rx.el.form(
                field("Display name", "display_name", "Ada Lovelace"),
                field("Username", "username", "ada.lovelace"),
                field("Email", "email", "ada@tata.app", "email"),
                field(
                    "Password", "password", "At least 8 characters", "password"
                ),
                field(
                    "Confirm password",
                    "confirm_password",
                    "Repeat password",
                    "password",
                ),
                error_banner(),
                rx.el.button(
                    rx.cond(
                        AuthState.processing,
                        "Creating account...",
                        "Sign up",
                    ),
                    type="submit",
                    disabled=AuthState.processing,
                    class_name="mt-5 w-full rounded-xl bg-[#1E9EF5] py-2.5 text-sm font-semibold text-white hover:bg-sky-600 disabled:opacity-60",
                ),
                on_submit=AuthState.signup,
                reset_on_submit=False,
            ),
            rx.el.p(
                rx.el.span(
                    "Already have an account? ", class_name="text-slate-500"
                ),
                rx.el.a(
                    "Log in",
                    href="/login",
                    class_name="font-semibold text-[#1E9EF5] hover:underline",
                ),
                class_name="mt-4 text-sm",
            ),
            class_name="w-full max-w-sm rounded-2xl border border-slate-200 bg-white p-6",
        )
    )
