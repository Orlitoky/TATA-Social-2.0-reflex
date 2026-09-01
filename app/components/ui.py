"""Small shared UI primitives for the TATA interface."""

from __future__ import annotations

import reflex as rx


def avatar(
    url: rx.Var | str, is_remote: rx.Var | bool, class_name: str = "size-10"
) -> rx.Component:
    """Render an avatar from either a remote URL or an uploaded storage key."""
    return rx.image(
        src=rx.cond(is_remote, url, rx.get_upload_url(url)),
        alt="Avatar",
        class_name=f"{class_name} rounded-full object-cover bg-slate-100",
    )


def media_image(
    url: rx.Var | str, is_remote: rx.Var | bool, class_name: str
) -> rx.Component:
    return rx.image(
        src=rx.cond(is_remote, url, rx.get_upload_url(url)),
        alt="Post media",
        class_name=f"{class_name} object-cover bg-slate-100",
    )


def media_video(
    url: rx.Var | str, is_remote: rx.Var | bool, class_name: str
) -> rx.Component:
    return rx.el.video(
        src=rx.cond(is_remote, url, rx.get_upload_url(url)),
        controls=True,
        class_name=f"{class_name} bg-black object-cover",
    )


def privacy_icon(privacy: rx.Var | str) -> rx.Component:
    return rx.match(
        privacy,
        ("public", rx.icon("globe", class_name="h-3.5 w-3.5 text-slate-400")),
        ("friends", rx.icon("users", class_name="h-3.5 w-3.5 text-slate-400")),
        rx.icon("lock", class_name="h-3.5 w-3.5 text-slate-400"),
    )


def skeleton_card() -> rx.Component:
    return rx.el.div(
        rx.el.div(class_name="h-10 w-10 rounded-full bg-slate-200"),
        rx.el.div(
            rx.el.div(class_name="h-3 w-32 rounded bg-slate-200"),
            rx.el.div(class_name="h-3 w-20 rounded bg-slate-200 mt-2"),
            rx.el.div(class_name="h-32 w-full rounded-xl bg-slate-200 mt-4"),
            class_name="flex-1",
        ),
        class_name="flex gap-3 rounded-2xl border border-slate-200 bg-white p-4 animate-pulse",
    )
