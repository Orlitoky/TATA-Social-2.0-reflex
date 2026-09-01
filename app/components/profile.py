"""Cover-led personal profile header, edit panel and owner post timeline."""

from __future__ import annotations

import reflex as rx

from app.components.ui import (
    avatar,
    media_image,
    media_video,
    privacy_icon,
    skeleton_card,
)
from app.states.profile_state import ProfileMedia, ProfilePost, ProfileState

AVATAR_UPLOAD_ID = "profile_avatar_upload"
COVER_UPLOAD_ID = "profile_cover_upload"
IMAGE_ACCEPT = {
    "image/png": [".png"],
    "image/jpeg": [".jpg", ".jpeg"],
    "image/webp": [".webp"],
    "image/gif": [".gif"],
}


def count_tile(label: str, value: rx.Var | int, icon: str) -> rx.Component:
    return rx.el.div(
        rx.el.div(
            rx.icon(icon, class_name="h-4 w-4 text-[#1E9EF5]"),
            rx.el.span(
                label,
                class_name="text-[11px] font-semibold uppercase tracking-wide text-slate-500",
            ),
            class_name="flex items-center gap-1.5",
        ),
        rx.el.p(
            value,
            class_name="mt-1 text-xl font-bold leading-tight text-[#0D1420]",
        ),
        class_name="w-full rounded-xl border border-slate-200 bg-white px-3 py-2",
    )


def counts_row() -> rx.Component:
    return rx.el.div(
        count_tile("Posts", ProfileState.post_count, "newspaper"),
        count_tile("Friends", ProfileState.friend_count, "users"),
        count_tile("Followers", ProfileState.follower_count, "user-plus"),
        count_tile("Following", ProfileState.following_count, "compass"),
        class_name="mt-4 grid w-full grid-cols-2 gap-2 md:grid-cols-4 md:gap-3",
    )


def cover_band() -> rx.Component:
    return rx.el.div(
        rx.cond(
            ProfileState.has_cover,
            media_image(
                ProfileState.cover_key,
                ProfileState.cover_is_remote,
                "h-40 w-full md:h-56",
            ),
            rx.el.div(
                rx.icon("image", class_name="h-6 w-6 text-white/80"),
                rx.el.span(
                    "Add a cover image",
                    class_name="text-xs font-semibold text-white/90",
                ),
                class_name="flex h-40 w-full flex-col items-center justify-center gap-1 bg-[#1E9EF5] md:h-56",
            ),
        ),
        rx.el.div(
            rx.upload.root(
                rx.el.div(
                    rx.icon("camera", class_name="h-4 w-4 text-[#0D1420]"),
                    rx.el.span(
                        "Change cover",
                        class_name="hidden text-xs font-semibold text-[#0D1420] sm:block",
                    ),
                    class_name="flex items-center gap-1.5",
                ),
                id=COVER_UPLOAD_ID,
                accept=IMAGE_ACCEPT,
                max_files=1,
                multiple=False,
                on_drop=ProfileState.upload_cover(
                    rx.upload_files(upload_id=COVER_UPLOAD_ID)
                ),
                class_name="cursor-pointer rounded-full border border-slate-200 bg-white/95 px-3 py-2 hover:border-[#1E9EF5]",
            ),
            class_name="absolute right-3 top-3",
        ),
        rx.cond(
            ProfileState.cover_uploading,
            rx.el.div(
                rx.el.span(
                    "Uploading cover...",
                    class_name="text-xs font-semibold text-white",
                ),
                class_name="absolute inset-0 flex items-center justify-center bg-[#0D1420]/50",
            ),
        ),
        class_name="relative overflow-hidden rounded-2xl bg-slate-100",
    )


def avatar_block() -> rx.Component:
    return rx.el.div(
        rx.el.div(
            avatar(
                ProfileState.avatar_url,
                ProfileState.avatar_remote,
                "size-24 md:size-28 ring-4 ring-white",
            ),
            rx.upload.root(
                rx.icon("camera", class_name="h-4 w-4 text-white"),
                id=AVATAR_UPLOAD_ID,
                accept=IMAGE_ACCEPT,
                max_files=1,
                multiple=False,
                on_drop=ProfileState.upload_avatar(
                    rx.upload_files(upload_id=AVATAR_UPLOAD_ID)
                ),
                class_name="absolute bottom-0 right-0 flex size-8 cursor-pointer items-center justify-center rounded-full bg-[#1E9EF5] hover:bg-sky-600",
            ),
            rx.cond(
                ProfileState.avatar_uploading,
                rx.el.div(
                    rx.icon(
                        "loader-circle",
                        class_name="h-5 w-5 animate-spin text-white",
                    ),
                    class_name="absolute inset-0 flex items-center justify-center rounded-full bg-[#0D1420]/50",
                ),
            ),
            class_name="relative",
        ),
        class_name="-mt-14 px-1 md:-mt-16",
    )


def website_link() -> rx.Component:
    return rx.cond(
        ProfileState.website != "",
        rx.el.a(
            rx.icon("link", class_name="h-3.5 w-3.5 text-[#22D3EE]"),
            rx.el.span(ProfileState.website, class_name="truncate"),
            href=ProfileState.website,
            target="_blank",
            rel="noopener noreferrer nofollow",
            class_name="flex min-w-0 items-center gap-1.5 text-xs font-semibold text-[#1E9EF5] hover:underline",
        ),
    )


def upload_feedback() -> rx.Component:
    return rx.el.div(
        rx.cond(
            ProfileState.upload_error != "",
            rx.el.p(
                ProfileState.upload_error,
                class_name="mt-2 rounded-xl bg-red-100 px-3 py-2 text-xs font-semibold text-red-500",
            ),
        ),
        rx.cond(
            ProfileState.upload_success != "",
            rx.el.p(
                ProfileState.upload_success,
                class_name="mt-2 rounded-xl bg-green-100 px-3 py-2 text-xs font-semibold text-green-500",
            ),
        ),
        class_name="w-full",
    )


def profile_header() -> rx.Component:
    return rx.el.section(
        cover_band(),
        rx.el.div(
            avatar_block(),
            rx.el.div(
                rx.el.div(
                    rx.el.div(
                        rx.el.h1(
                            ProfileState.display_name,
                            class_name="text-xl font-bold leading-tight text-[#0D1420] md:text-2xl",
                        ),
                        rx.el.p(
                            f"@{ProfileState.username}",
                            class_name="text-sm font-medium text-slate-500",
                        ),
                        class_name="min-w-0",
                    ),
                    rx.el.button(
                        rx.icon("pencil", class_name="h-4 w-4"),
                        rx.el.span("Edit Profile"),
                        on_click=ProfileState.open_edit,
                        class_name="flex w-fit shrink-0 items-center gap-2 rounded-full bg-[#1E9EF5] px-4 py-2 text-sm font-semibold text-white hover:bg-sky-600",
                    ),
                    class_name="flex flex-wrap items-start justify-between gap-3",
                ),
                rx.cond(
                    ProfileState.bio != "",
                    rx.el.p(
                        ProfileState.bio,
                        class_name="mt-2 text-sm font-medium leading-relaxed text-slate-700 whitespace-pre-wrap",
                    ),
                ),
                rx.el.div(
                    rx.cond(
                        ProfileState.location != "",
                        rx.el.span(
                            rx.icon(
                                "map-pin",
                                class_name="mr-1 inline h-3.5 w-3.5 text-slate-400",
                            ),
                            ProfileState.location,
                            class_name="text-xs font-medium text-slate-500",
                        ),
                    ),
                    website_link(),
                    rx.cond(
                        ProfileState.joined_label != "",
                        rx.el.span(
                            rx.icon(
                                "calendar",
                                class_name="mr-1 inline h-3.5 w-3.5 text-slate-400",
                            ),
                            f"Joined {ProfileState.joined_label}",
                            class_name="text-xs font-medium text-slate-500",
                        ),
                    ),
                    class_name="mt-2 flex flex-wrap items-center gap-x-4 gap-y-1.5",
                ),
                upload_feedback(),
                counts_row(),
                class_name="mt-2 min-w-0 flex-1",
            ),
            class_name="px-3 pb-4 md:px-5",
        ),
        class_name="w-full overflow-hidden rounded-2xl border border-slate-200 bg-white",
    )


def edit_panel() -> rx.Component:
    return rx.cond(
        ProfileState.edit_open,
        rx.el.div(
            rx.el.div(
                rx.el.div(
                    rx.el.h2(
                        "Edit profile",
                        class_name="text-base font-semibold text-[#0D1420]",
                    ),
                    rx.el.button(
                        rx.icon("x", class_name="h-4 w-4"),
                        on_click=ProfileState.close_edit,
                        class_name="text-slate-400 hover:text-[#0D1420]",
                    ),
                    class_name="flex items-center justify-between border-b border-slate-200 px-4 py-3",
                ),
                rx.el.form(
                    rx.el.label(
                        "Display name",
                        class_name="text-xs font-semibold uppercase tracking-wide text-slate-500",
                    ),
                    rx.el.input(
                        name="display_name",
                        default_value=ProfileState.form_display_name,
                        key=ProfileState.form_display_name,
                        placeholder="Your name",
                        class_name="mt-1 w-full rounded-xl border border-slate-200 px-3 py-2 text-sm text-[#0D1420] focus:border-[#1E9EF5] focus:ring-2 focus:ring-sky-100 outline-hidden",
                    ),
                    rx.el.div(
                        rx.el.label(
                            "Bio",
                            class_name="text-xs font-semibold uppercase tracking-wide text-slate-500",
                        ),
                        rx.el.span(
                            f"{ProfileState.bio_remaining} left",
                            class_name="text-xs font-medium text-slate-400",
                        ),
                        class_name="mt-3 flex items-center justify-between",
                    ),
                    rx.el.textarea(
                        name="bio",
                        default_value=ProfileState.form_bio,
                        on_change=ProfileState.set_form_bio.debounce(300),
                        rows="3",
                        max_length=280,
                        placeholder="Tell people about you",
                        class_name="mt-1 w-full resize-none rounded-xl border border-slate-200 p-3 text-sm text-[#0D1420] focus:border-[#1E9EF5] focus:ring-2 focus:ring-sky-100 outline-hidden",
                    ),
                    rx.el.label(
                        "Location",
                        class_name="mt-3 block text-xs font-semibold uppercase tracking-wide text-slate-500",
                    ),
                    rx.el.input(
                        name="location",
                        default_value=ProfileState.form_location,
                        key=ProfileState.form_location,
                        placeholder="City, Country",
                        class_name="mt-1 w-full rounded-xl border border-slate-200 px-3 py-2 text-sm text-[#0D1420] focus:border-[#1E9EF5] focus:ring-2 focus:ring-sky-100 outline-hidden",
                    ),
                    rx.el.label(
                        "Website",
                        class_name="mt-3 block text-xs font-semibold uppercase tracking-wide text-slate-500",
                    ),
                    rx.el.input(
                        name="website",
                        default_value=ProfileState.form_website,
                        key=ProfileState.form_website,
                        placeholder="https://example.com",
                        class_name="mt-1 w-full rounded-xl border border-slate-200 px-3 py-2 text-sm text-[#0D1420] focus:border-[#1E9EF5] focus:ring-2 focus:ring-sky-100 outline-hidden",
                    ),
                    rx.cond(
                        ProfileState.edit_error != "",
                        rx.el.p(
                            ProfileState.edit_error,
                            class_name="mt-3 rounded-xl bg-red-100 px-3 py-2 text-xs font-semibold text-red-500",
                        ),
                    ),
                    rx.el.div(
                        rx.el.button(
                            rx.cond(
                                ProfileState.saving,
                                rx.el.span("Saving..."),
                                rx.el.span("Save changes"),
                            ),
                            type="submit",
                            disabled=ProfileState.saving,
                            class_name="flex-1 rounded-xl bg-[#1E9EF5] py-2.5 text-sm font-semibold text-white hover:bg-sky-600 disabled:opacity-60",
                        ),
                        rx.el.button(
                            "Cancel",
                            type="button",
                            on_click=ProfileState.close_edit,
                            class_name="rounded-xl border border-slate-200 px-4 py-2.5 text-sm font-semibold text-slate-600 hover:border-slate-300",
                        ),
                        class_name="mt-4 flex items-center gap-2",
                    ),
                    on_submit=ProfileState.save_profile,
                    class_name="p-4",
                ),
                class_name="w-full max-w-md overflow-hidden rounded-2xl border border-slate-200 bg-white shadow-sm",
            ),
            class_name="fixed inset-0 z-50 flex items-center justify-center overflow-y-auto bg-[#0D1420]/60 p-4",
        ),
    )


def timeline_media_cell(item: ProfileMedia) -> rx.Component:
    return rx.cond(
        item["kind"] == "video",
        media_video(item["url"], item["is_remote"], "h-64 w-full rounded-xl"),
        media_image(item["url"], item["is_remote"], "h-48 w-full rounded-xl"),
    )


def timeline_media(post: ProfilePost) -> rx.Component:
    return rx.cond(
        post["media"].length() > 0,
        rx.el.div(
            rx.foreach(post["media"], timeline_media_cell),
            class_name=rx.cond(
                post["media"].length() == 1,
                "mt-3 grid grid-cols-1 gap-1.5",
                rx.cond(
                    post["media"].length() == 2,
                    "mt-3 grid grid-cols-2 gap-1.5",
                    "mt-3 grid grid-cols-3 gap-1.5",
                ),
            ),
        ),
    )


def timeline_body(post: ProfilePost) -> rx.Component:
    return rx.cond(
        ProfileState.editing_post_id == post["id"],
        rx.el.div(
            rx.el.textarea(
                default_value=ProfileState.edit_body,
                on_change=ProfileState.set_edit_body.debounce(300),
                rows="3",
                class_name="w-full resize-none rounded-xl border border-slate-200 p-3 text-sm text-[#0D1420] focus:border-[#1E9EF5] focus:ring-2 focus:ring-sky-100 outline-hidden",
            ),
            rx.el.div(
                rx.el.button(
                    "Save",
                    on_click=ProfileState.save_post_edit,
                    class_name="rounded-full bg-[#1E9EF5] px-4 py-1.5 text-xs font-semibold text-white hover:bg-sky-600",
                ),
                rx.el.button(
                    "Cancel",
                    on_click=ProfileState.cancel_edit,
                    class_name="rounded-full border border-slate-200 px-4 py-1.5 text-xs font-semibold text-slate-600",
                ),
                class_name="mt-2 flex items-center gap-2",
            ),
            class_name="mt-2",
        ),
        rx.cond(
            post["body"] != "",
            rx.el.p(
                post["body"],
                class_name="mt-2 text-sm font-medium leading-relaxed text-[#0D1420] whitespace-pre-wrap",
            ),
        ),
    )


def timeline_card(post: ProfilePost) -> rx.Component:
    return rx.el.article(
        rx.el.div(
            avatar(
                ProfileState.avatar_url, ProfileState.avatar_remote, "size-10"
            ),
            rx.el.div(
                rx.el.p(
                    ProfileState.display_name,
                    class_name="text-sm font-semibold text-[#0D1420]",
                ),
                rx.el.div(
                    rx.el.span(
                        post["time_label"],
                        class_name="text-xs text-slate-400",
                    ),
                    rx.el.span("·", class_name="text-xs text-slate-300"),
                    privacy_icon(post["privacy"]),
                    rx.cond(
                        post["is_edited"],
                        rx.el.span(
                            "edited",
                            class_name="text-xs italic text-slate-400",
                        ),
                    ),
                    rx.cond(
                        post["location"] != "",
                        rx.el.span(
                            post["location"],
                            class_name="text-xs text-slate-400",
                        ),
                    ),
                    class_name="mt-0.5 flex items-center gap-1.5",
                ),
                class_name="min-w-0 flex-1",
            ),
            rx.el.div(
                rx.el.button(
                    rx.icon("pencil", class_name="h-4 w-4"),
                    on_click=lambda: ProfileState.start_edit(
                        post["id"], post["body"]
                    ),
                    class_name="rounded-full p-2 text-slate-400 hover:bg-slate-50 hover:text-[#1E9EF5]",
                ),
                rx.el.button(
                    rx.icon("trash-2", class_name="h-4 w-4"),
                    on_click=lambda: ProfileState.delete_post(post["id"]),
                    class_name="rounded-full p-2 text-slate-400 hover:bg-red-50 hover:text-red-500",
                ),
                class_name="flex items-center",
            ),
            class_name="flex items-start gap-3",
        ),
        timeline_body(post),
        timeline_media(post),
        rx.el.div(
            rx.el.span(
                f"{post['reaction_count']} reactions",
                class_name="text-xs font-medium text-slate-500",
            ),
            rx.el.span("·", class_name="text-xs text-slate-300"),
            rx.el.span(
                f"{post['comment_count']} comments",
                class_name="text-xs font-medium text-slate-500",
            ),
            rx.el.span("·", class_name="text-xs text-slate-300"),
            rx.el.span(
                f"{post['share_count']} shares",
                class_name="text-xs font-medium text-slate-500",
            ),
            class_name="mt-3 flex items-center gap-1.5 border-t border-slate-100 pt-2",
        ),
        class_name="w-full rounded-2xl border border-slate-200 bg-white p-4",
    )


def profile_timeline() -> rx.Component:
    return rx.el.section(
        rx.el.div(
            rx.icon("clock", class_name="h-4 w-4 text-[#1E9EF5]"),
            rx.el.h2(
                "Your posts",
                class_name="text-sm font-semibold text-[#0D1420]",
            ),
            rx.el.span(
                f"{ProfileState.post_count} total",
                class_name="text-xs font-medium text-slate-400",
            ),
            class_name="flex items-center gap-2 px-1",
        ),
        rx.cond(
            ProfileState.loading,
            rx.el.div(
                skeleton_card(),
                skeleton_card(),
                class_name="mt-3 flex flex-col gap-3",
            ),
            rx.cond(
                ProfileState.posts.length() > 0,
                rx.el.div(
                    rx.foreach(ProfileState.posts, timeline_card),
                    class_name="mt-3 flex flex-col gap-3",
                ),
                rx.el.div(
                    rx.icon("pen-line", class_name="h-8 w-8 text-[#1E9EF5]"),
                    rx.el.p(
                        "You haven't posted yet",
                        class_name="mt-2 text-base font-semibold text-[#0D1420]",
                    ),
                    rx.el.p(
                        "Share a photo or a thought from Home and it will appear right here.",
                        class_name="text-sm text-slate-500",
                    ),
                    rx.el.a(
                        "Go to Home",
                        href="/",
                        class_name="mt-3 w-fit rounded-full bg-[#1E9EF5] px-4 py-2 text-sm font-semibold text-white hover:bg-sky-600",
                    ),
                    class_name="mt-3 flex flex-col items-center rounded-2xl border border-dashed border-slate-300 bg-white px-6 py-12 text-center",
                ),
            ),
        ),
        rx.cond(
            ProfileState.has_more,
            rx.el.button(
                rx.cond(
                    ProfileState.loading_more,
                    rx.el.span("Loading more..."),
                    rx.el.span("Load more posts"),
                ),
                on_click=ProfileState.load_more,
                disabled=ProfileState.loading_more,
                class_name="mt-3 w-full rounded-xl border border-slate-200 bg-white py-2.5 text-sm font-semibold text-[#1E9EF5] hover:border-[#1E9EF5] disabled:opacity-60",
            ),
            rx.cond(
                ProfileState.posts.length() > 0,
                rx.el.p(
                    "That's your whole timeline.",
                    class_name="mt-3 text-center text-xs font-medium text-slate-400",
                ),
            ),
        ),
        class_name="w-full",
    )
