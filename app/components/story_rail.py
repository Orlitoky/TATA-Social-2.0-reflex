"""Immersive horizontal story rail, creation sheet and full-screen viewer."""

from __future__ import annotations

import reflex as rx

from app.components.ui import avatar, media_image, media_video
from app.constants import PRIVACY_CHOICES, REACTION_CHOICES, STORY_COLORS
from app.states.auth_state import AuthState
from app.states.story_state import StoryReplyRow, StoryRow, StoryState

STORY_UPLOAD_ID = "story_upload"


def add_story_tile() -> rx.Component:
    return rx.el.button(
        rx.el.div(
            avatar(AuthState.avatar_url, AuthState.avatar_remote, "size-full"),
            class_name="h-28 w-full overflow-hidden rounded-t-2xl opacity-90",
        ),
        rx.el.div(
            rx.el.div(
                rx.icon("plus", class_name="h-4 w-4 text-white"),
                class_name="flex size-8 items-center justify-center rounded-full border-2 border-white bg-[#1E9EF5]",
            ),
            rx.el.span(
                "Add Story",
                class_name="text-xs font-semibold text-[#0D1420]",
            ),
            class_name="flex flex-col items-center gap-1 -mt-4 pb-3",
        ),
        on_click=StoryState.open_create,
        class_name="w-[104px] shrink-0 overflow-hidden rounded-2xl border border-slate-200 bg-white hover:border-[#1E9EF5]",
    )


def story_tile(story: StoryRow, index: int) -> rx.Component:
    return rx.el.button(
        rx.cond(
            story["has_media"],
            rx.cond(
                story["media_kind"] == "video",
                media_video(
                    story["media_url"],
                    story["media_remote"],
                    "h-full w-full",
                ),
                media_image(
                    story["media_url"],
                    story["media_remote"],
                    "h-full w-full",
                ),
            ),
            rx.el.div(
                rx.el.p(
                    story["caption"],
                    class_name="line-clamp-4 px-2 text-center text-[11px] font-semibold text-white",
                ),
                class_name="flex h-full w-full items-center justify-center",
                style={"backgroundColor": story["background_color"]},
            ),
        ),
        rx.el.div(
            avatar(
                story["avatar_url"],
                story["avatar_remote"],
                "size-8 ring-2 ring-[#22D3EE]",
            ),
            class_name="absolute left-2 top-2",
        ),
        rx.el.div(
            rx.el.p(
                story["author_name"],
                class_name="truncate text-[11px] font-semibold text-white",
            ),
            rx.el.p(
                story["time_label"],
                class_name="truncate text-[10px] text-white/80",
            ),
            class_name="absolute bottom-0 left-0 right-0 bg-gradient-to-t from-black/70 to-transparent p-2 text-left",
        ),
        on_click=lambda: StoryState.open_viewer(index),
        class_name=rx.cond(
            story["seen"],
            "relative h-40 w-[104px] shrink-0 overflow-hidden rounded-2xl border border-slate-200",
            "relative h-40 w-[104px] shrink-0 overflow-hidden rounded-2xl border-2 border-[#1E9EF5]",
        ),
    )


def create_story_sheet() -> rx.Component:
    return rx.cond(
        StoryState.create_open,
        rx.el.div(
            rx.el.div(
                rx.el.div(
                    rx.el.h2(
                        "Create story",
                        class_name="text-base font-semibold text-[#0D1420]",
                    ),
                    rx.el.button(
                        rx.icon("x", class_name="h-4 w-4"),
                        on_click=StoryState.close_create,
                        class_name="text-slate-400 hover:text-[#0D1420]",
                    ),
                    class_name="flex items-center justify-between border-b border-slate-200 px-4 py-3",
                ),
                rx.el.div(
                    rx.el.textarea(
                        placeholder="Say something...",
                        default_value=StoryState.caption,
                        on_change=StoryState.set_caption.debounce(300),
                        rows="3",
                        class_name="w-full resize-none rounded-xl border border-slate-200 p-3 text-sm text-[#0D1420] focus:border-[#1E9EF5] focus:ring-2 focus:ring-sky-100 outline-hidden",
                    ),
                    rx.el.div(
                        rx.foreach(
                            STORY_COLORS,
                            lambda color: rx.el.button(
                                on_click=lambda: (
                                    StoryState.set_background_color(color)
                                ),
                                style={"backgroundColor": color},
                                class_name=rx.cond(
                                    StoryState.background_color == color,
                                    "size-7 rounded-full ring-2 ring-offset-2 ring-[#0D1420]",
                                    "size-7 rounded-full",
                                ),
                            ),
                        ),
                        class_name="mt-3 flex items-center gap-2",
                    ),
                    rx.upload.root(
                        rx.el.div(
                            rx.icon(
                                "image-plus",
                                class_name="h-5 w-5 text-[#1E9EF5]",
                            ),
                            rx.el.p(
                                "Add a photo or video (max 8MB / 64MB)",
                                class_name="text-xs font-medium text-slate-500",
                            ),
                            class_name="flex flex-col items-center gap-1 py-4",
                        ),
                        id=STORY_UPLOAD_ID,
                        multiple=False,
                        max_files=1,
                        accept={
                            "image/png": [".png"],
                            "image/jpeg": [".jpg", ".jpeg"],
                            "image/webp": [".webp"],
                            "image/gif": [".gif"],
                            "video/mp4": [".mp4"],
                            "video/webm": [".webm"],
                        },
                        on_drop=StoryState.handle_story_upload(
                            rx.upload_files(upload_id=STORY_UPLOAD_ID)
                        ),
                        class_name="mt-3 block w-full cursor-pointer rounded-xl border-2 border-dashed border-sky-200 bg-sky-50/50 hover:border-[#1E9EF5]",
                    ),
                    rx.cond(
                        StoryState.pending_key != "",
                        rx.el.div(
                            rx.icon(
                                "circle_check",
                                class_name="h-4 w-4 text-emerald-500",
                            ),
                            rx.el.span(
                                StoryState.pending_name,
                                class_name="truncate text-xs font-medium text-slate-600",
                            ),
                            class_name="mt-2 flex items-center gap-2",
                        ),
                    ),
                    rx.el.div(
                        rx.foreach(
                            PRIVACY_CHOICES,
                            lambda choice: rx.el.button(
                                rx.icon(
                                    choice["icon"], class_name="h-3.5 w-3.5"
                                ),
                                rx.el.span(
                                    choice["label"],
                                    class_name="text-xs font-semibold",
                                ),
                                on_click=lambda: StoryState.set_privacy(
                                    choice["value"]
                                ),
                                class_name=rx.cond(
                                    StoryState.privacy == choice["value"],
                                    "flex items-center gap-1.5 rounded-full border border-[#1E9EF5] bg-sky-50 px-3 py-1.5 text-[#1E9EF5]",
                                    "flex items-center gap-1.5 rounded-full border border-slate-200 px-3 py-1.5 text-slate-600",
                                ),
                            ),
                        ),
                        class_name="mt-3 flex flex-wrap items-center gap-2",
                    ),
                    rx.cond(
                        StoryState.create_error != "",
                        rx.el.p(
                            StoryState.create_error,
                            class_name="mt-2 text-sm font-medium text-red-500",
                        ),
                    ),
                    rx.el.button(
                        rx.cond(
                            StoryState.creating, "Publishing...", "Share story"
                        ),
                        on_click=StoryState.submit_story,
                        disabled=StoryState.creating,
                        class_name="mt-4 w-full rounded-xl bg-[#1E9EF5] py-2.5 text-sm font-semibold text-white hover:bg-sky-600 disabled:opacity-60",
                    ),
                    class_name="p-4",
                ),
                class_name="w-full max-w-md overflow-hidden rounded-2xl border border-slate-200 bg-white shadow-sm",
            ),
            class_name="fixed inset-0 z-50 flex items-center justify-center bg-[#0D1420]/60 p-4",
        ),
    )


def reply_row(reply: StoryReplyRow) -> rx.Component:
    return rx.el.div(
        rx.el.span(
            reply["author_name"], class_name="text-xs font-semibold text-white"
        ),
        rx.el.span(reply["body"], class_name="text-xs text-white/80"),
        rx.el.span(reply["time_label"], class_name="text-[10px] text-white/50"),
        class_name="flex flex-col rounded-xl bg-white/10 px-3 py-2",
    )


def story_viewer() -> rx.Component:
    return rx.cond(
        StoryState.viewer_open,
        rx.el.div(
            rx.el.div(
                rx.el.div(
                    avatar(
                        StoryState.current_story["avatar_url"],
                        StoryState.current_story["avatar_remote"],
                        "size-9",
                    ),
                    rx.el.div(
                        rx.el.p(
                            StoryState.current_story["author_name"],
                            class_name="text-sm font-semibold text-white",
                        ),
                        rx.el.p(
                            StoryState.current_story["time_label"],
                            class_name="text-xs text-white/70",
                        ),
                        class_name="min-w-0",
                    ),
                    rx.el.div(class_name="flex-1"),
                    rx.el.div(
                        rx.icon("eye", class_name="h-4 w-4 text-white/80"),
                        rx.el.span(
                            StoryState.current_story["view_count"],
                            class_name="text-xs font-semibold text-white/80",
                        ),
                        class_name="flex items-center gap-1",
                    ),
                    rx.el.button(
                        rx.icon("x", class_name="h-5 w-5 text-white"),
                        on_click=StoryState.close_viewer,
                    ),
                    class_name="flex items-center gap-3 p-3",
                ),
                rx.el.div(
                    rx.cond(
                        StoryState.current_story["has_media"],
                        rx.cond(
                            StoryState.current_story["media_kind"] == "video",
                            media_video(
                                StoryState.current_story["media_url"],
                                StoryState.current_story["media_remote"],
                                "h-full w-full",
                            ),
                            media_image(
                                StoryState.current_story["media_url"],
                                StoryState.current_story["media_remote"],
                                "h-full w-full",
                            ),
                        ),
                        rx.el.div(
                            rx.el.p(
                                StoryState.current_story["caption"],
                                class_name="px-6 text-center text-lg font-semibold text-white",
                            ),
                            class_name="flex h-full w-full items-center justify-center",
                            style={
                                "backgroundColor": StoryState.current_story[
                                    "background_color"
                                ]
                            },
                        ),
                    ),
                    rx.el.button(
                        rx.icon(
                            "chevron-left", class_name="h-5 w-5 text-white"
                        ),
                        on_click=StoryState.prev_story,
                        class_name="absolute left-2 top-1/2 -translate-y-1/2 rounded-full bg-black/40 p-2",
                    ),
                    rx.el.button(
                        rx.icon(
                            "chevron-right", class_name="h-5 w-5 text-white"
                        ),
                        on_click=StoryState.next_story,
                        class_name="absolute right-2 top-1/2 -translate-y-1/2 rounded-full bg-black/40 p-2",
                    ),
                    class_name="relative h-[60vh] w-full overflow-hidden bg-black",
                ),
                rx.cond(
                    StoryState.current_story["has_media"]
                    & (StoryState.current_story["caption"] != ""),
                    rx.el.p(
                        StoryState.current_story["caption"],
                        class_name="px-4 pt-3 text-sm text-white/90",
                    ),
                ),
                rx.el.div(
                    rx.foreach(
                        REACTION_CHOICES,
                        lambda choice: rx.el.button(
                            choice["emoji"],
                            on_click=lambda: StoryState.react_to_story(
                                choice["kind"]
                            ),
                            class_name=rx.cond(
                                StoryState.current_story["my_reaction"]
                                == choice["kind"],
                                "rounded-full bg-[#1E9EF5] px-3 py-1.5 text-lg",
                                "rounded-full bg-white/10 px-3 py-1.5 text-lg hover:bg-white/20",
                            ),
                        ),
                    ),
                    class_name="flex flex-wrap items-center gap-2 px-4 py-3",
                ),
                rx.el.div(
                    rx.el.input(
                        placeholder="Reply to this story",
                        default_value=StoryState.reply_draft,
                        on_change=StoryState.set_reply_draft.debounce(300),
                        class_name="flex-1 rounded-full bg-white/10 px-4 py-2 text-sm text-white placeholder:text-white/50 outline-hidden focus:ring-2 focus:ring-[#22D3EE]",
                    ),
                    rx.el.button(
                        rx.icon("send", class_name="h-4 w-4 text-white"),
                        on_click=StoryState.submit_story_reply,
                        class_name="rounded-full bg-[#1E9EF5] p-2.5 hover:bg-sky-600",
                    ),
                    class_name="flex items-center gap-2 px-4 pb-3",
                ),
                rx.cond(
                    StoryState.viewer_replies.length() > 0,
                    rx.el.div(
                        rx.foreach(StoryState.viewer_replies, reply_row),
                        class_name="flex max-h-32 flex-col gap-2 overflow-y-auto px-4 pb-4",
                    ),
                ),
                class_name="w-full max-w-sm overflow-hidden rounded-2xl bg-[#0D1420]",
            ),
            class_name="fixed inset-0 z-50 flex items-center justify-center bg-black/85 p-3",
        ),
    )


def story_rail() -> rx.Component:
    return rx.el.section(
        rx.el.div(
            rx.el.h2(
                "Stories",
                class_name="text-sm font-semibold text-[#0D1420]",
            ),
            rx.el.span(
                f"{StoryState.story_count} live",
                class_name="text-xs font-medium text-[#22D3EE]",
            ),
            class_name="mb-2 flex items-center justify-between px-1",
        ),
        rx.cond(
            StoryState.loading,
            rx.el.div(
                rx.el.div(
                    class_name="h-40 w-[104px] shrink-0 rounded-2xl bg-slate-200 animate-pulse"
                ),
                rx.el.div(
                    class_name="h-40 w-[104px] shrink-0 rounded-2xl bg-slate-200 animate-pulse"
                ),
                rx.el.div(
                    class_name="h-40 w-[104px] shrink-0 rounded-2xl bg-slate-200 animate-pulse"
                ),
                class_name="flex gap-3",
            ),
            rx.el.div(
                add_story_tile(),
                rx.foreach(
                    StoryState.stories,
                    lambda story, index: story_tile(story, index),
                ),
                class_name="flex gap-3 overflow-x-auto pb-2",
            ),
        ),
        create_story_sheet(),
        story_viewer(),
        class_name="w-full rounded-2xl border border-slate-200 bg-white p-3",
    )
