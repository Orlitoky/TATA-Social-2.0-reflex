"""Post composer: text, privacy, photo / multi-photo / video uploads."""

from __future__ import annotations

import reflex as rx

from app.components.ui import avatar, media_image, media_video
from app.constants import PRIVACY_CHOICES
from app.states.auth_state import AuthState
from app.states.feed_state import FeedState, PendingMedia

PHOTO_UPLOAD_ID = "post_photos"
VIDEO_UPLOAD_ID = "post_video"


def pending_tile(item: PendingMedia) -> rx.Component:
    return rx.el.div(
        rx.cond(
            item["kind"] == "video",
            media_video(
                item["url"], item["is_remote"], "h-24 w-full rounded-xl"
            ),
            media_image(
                item["url"], item["is_remote"], "h-24 w-full rounded-xl"
            ),
        ),
        rx.el.button(
            rx.icon("x", class_name="h-3.5 w-3.5 text-white"),
            on_click=lambda: FeedState.remove_composer_media(
                item["storage_key"]
            ),
            class_name="absolute right-1 top-1 rounded-full bg-black/60 p-1",
        ),
        class_name="relative",
    )


def upload_button(
    upload_id: str,
    icon: str,
    label: str,
    accept: dict[str, list[str]],
    multiple: bool,
) -> rx.Component:
    return rx.upload.root(
        rx.el.div(
            rx.icon(icon, class_name="h-4 w-4 text-[#1E9EF5]"),
            rx.el.span(
                label, class_name="text-xs font-semibold text-slate-600"
            ),
            class_name="flex items-center gap-1.5 rounded-full border border-slate-200 px-3 py-1.5 hover:border-[#1E9EF5]",
        ),
        id=upload_id,
        multiple=multiple,
        max_files=6 if multiple else 1,
        accept=accept,
        on_drop=FeedState.handle_composer_upload(
            rx.upload_files(upload_id=upload_id)
        ),
        class_name="cursor-pointer",
    )


def composer() -> rx.Component:
    return rx.el.section(
        rx.el.div(
            avatar(AuthState.avatar_url, AuthState.avatar_remote, "size-10"),
            rx.el.textarea(
                placeholder=f"What's happening, {AuthState.display_name}?",
                default_value=FeedState.composer_body,
                on_change=FeedState.set_composer_body.debounce(300),
                rows="2",
                class_name="flex-1 resize-none rounded-xl border border-slate-200 bg-slate-50 p-3 text-sm font-medium text-[#0D1420] placeholder:text-slate-400 focus:border-[#1E9EF5] focus:bg-white focus:ring-2 focus:ring-sky-100 outline-hidden",
            ),
            class_name="flex items-start gap-3",
        ),
        rx.cond(
            FeedState.composer_media.length() > 0,
            rx.el.div(
                rx.foreach(FeedState.composer_media, pending_tile),
                class_name="mt-3 grid grid-cols-3 gap-2",
            ),
        ),
        rx.el.div(
            rx.el.div(
                upload_button(
                    PHOTO_UPLOAD_ID,
                    "image",
                    "Photos",
                    {
                        "image/png": [".png"],
                        "image/jpeg": [".jpg", ".jpeg"],
                        "image/webp": [".webp"],
                        "image/gif": [".gif"],
                    },
                    True,
                ),
                upload_button(
                    VIDEO_UPLOAD_ID,
                    "video",
                    "Video",
                    {"video/mp4": [".mp4"], "video/webm": [".webm"]},
                    False,
                ),
                class_name="flex flex-wrap items-center gap-2",
            ),
            rx.el.div(
                rx.foreach(
                    PRIVACY_CHOICES,
                    lambda choice: rx.el.button(
                        rx.icon(choice["icon"], class_name="h-3.5 w-3.5"),
                        rx.el.span(
                            choice["label"], class_name="text-xs font-semibold"
                        ),
                        on_click=lambda: FeedState.set_composer_privacy(
                            choice["value"]
                        ),
                        class_name=rx.cond(
                            FeedState.composer_privacy == choice["value"],
                            "flex items-center gap-1.5 rounded-full border border-[#1E9EF5] bg-sky-50 px-3 py-1.5 text-[#1E9EF5]",
                            "flex items-center gap-1.5 rounded-full border border-slate-200 px-3 py-1.5 text-slate-600",
                        ),
                    ),
                ),
                class_name="flex flex-wrap items-center gap-2",
            ),
            rx.el.button(
                rx.cond(FeedState.posting, "Posting...", "Post"),
                on_click=FeedState.submit_post,
                disabled=FeedState.posting,
                class_name="rounded-full bg-[#1E9EF5] px-5 py-2 text-sm font-semibold text-white hover:bg-sky-600 disabled:opacity-60",
            ),
            class_name="mt-3 flex flex-wrap items-center justify-between gap-2 border-t border-slate-100 pt-3",
        ),
        rx.cond(
            FeedState.composer_error != "",
            rx.el.p(
                FeedState.composer_error,
                class_name="mt-2 text-sm font-medium text-red-500",
            ),
        ),
        class_name="w-full rounded-2xl border border-slate-200 bg-white p-3",
    )
