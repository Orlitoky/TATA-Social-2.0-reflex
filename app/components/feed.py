"""Dense social feed: media layouts, reactions, threaded comments, sharing."""

from __future__ import annotations

import reflex as rx

from app.components.ui import (
    avatar,
    media_image,
    media_video,
    privacy_icon,
    skeleton_card,
)
from app.constants import REACTION_CHOICES
from app.states.feed_state import CommentRow, FeedState, MediaRow, PostRow


def reaction_glyph(kind: rx.Var | str) -> rx.Component:
    return rx.match(
        kind,
        ("like", rx.el.span("\U0001f44d")),
        ("love", rx.el.span("\u2764\ufe0f")),
        ("haha", rx.el.span("\U0001f602")),
        ("wow", rx.el.span("\U0001f62e")),
        ("sad", rx.el.span("\U0001f622")),
        ("angry", rx.el.span("\U0001f621")),
        rx.el.span("\U0001f44d"),
    )


def media_cell(item: MediaRow) -> rx.Component:
    return rx.cond(
        item["kind"] == "video",
        media_video(item["url"], item["is_remote"], "h-64 w-full rounded-xl"),
        media_image(item["url"], item["is_remote"], "h-48 w-full rounded-xl"),
    )


def media_grid(post: PostRow) -> rx.Component:
    return rx.cond(
        post["media"].length() > 0,
        rx.el.div(
            rx.foreach(post["media"], media_cell),
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


def reaction_bar(post: PostRow) -> rx.Component:
    return rx.el.div(
        rx.foreach(
            REACTION_CHOICES,
            lambda choice: rx.el.button(
                rx.el.span(choice["emoji"], class_name="text-base"),
                on_click=lambda: FeedState.react(post["id"], choice["kind"]),
                title=choice["label"],
                class_name=rx.cond(
                    post["my_reaction"] == choice["kind"],
                    "rounded-full border border-[#1E9EF5] bg-sky-50 px-2 py-1",
                    "rounded-full border border-transparent px-2 py-1 hover:bg-slate-50",
                ),
            ),
        ),
        class_name="flex flex-wrap items-center gap-1",
    )


def comment_row(comment: CommentRow) -> rx.Component:
    return rx.el.div(
        avatar(comment["avatar_url"], comment["avatar_remote"], "size-8"),
        rx.el.div(
            rx.el.div(
                rx.el.span(
                    comment["author_name"],
                    class_name="text-xs font-semibold text-[#0D1420]",
                ),
                rx.el.span(
                    f"@{comment['author_username']}",
                    class_name="text-xs text-slate-400",
                ),
                rx.el.span(
                    comment["time_label"], class_name="text-xs text-slate-400"
                ),
                class_name="flex flex-wrap items-center gap-2",
            ),
            rx.el.p(
                comment["body"],
                class_name="mt-0.5 text-sm text-slate-700 whitespace-pre-wrap",
            ),
            rx.el.button(
                "Reply",
                on_click=lambda: FeedState.set_reply_parent(comment["id"]),
                class_name="mt-1 text-xs font-semibold text-[#1E9EF5] hover:underline",
            ),
            class_name="min-w-0 flex-1 rounded-xl bg-slate-50 px-3 py-2",
        ),
        class_name=rx.cond(
            comment["depth"] > 0,
            "mt-2 ml-8 flex items-start gap-2",
            "mt-2 flex items-start gap-2",
        ),
    )


def comment_panel(post: PostRow) -> rx.Component:
    return rx.cond(
        FeedState.open_post_id == post["id"],
        rx.el.div(
            rx.cond(
                post["comments"].length() > 0,
                rx.el.div(rx.foreach(post["comments"], comment_row)),
                rx.el.p(
                    "No comments yet. Start the conversation.",
                    class_name="py-2 text-sm text-slate-500",
                ),
            ),
            rx.cond(
                FeedState.reply_parent_id > 0,
                rx.el.div(
                    rx.icon("reply", class_name="h-3.5 w-3.5 text-[#1E9EF5]"),
                    rx.el.span(
                        "Replying to a comment",
                        class_name="text-xs font-semibold text-[#1E9EF5]",
                    ),
                    rx.el.button(
                        rx.icon("x", class_name="h-3 w-3"),
                        on_click=lambda: FeedState.set_reply_parent(0),
                        class_name="text-slate-400",
                    ),
                    class_name="mt-2 flex items-center gap-2",
                ),
            ),
            rx.el.div(
                rx.el.input(
                    placeholder="Write a comment...",
                    default_value=FeedState.comment_draft,
                    on_change=FeedState.set_comment_draft.debounce(300),
                    class_name="flex-1 rounded-full border border-slate-200 bg-slate-50 px-4 py-2 text-sm text-[#0D1420] focus:border-[#1E9EF5] focus:bg-white focus:ring-2 focus:ring-sky-100 outline-hidden",
                ),
                rx.el.button(
                    rx.icon("send", class_name="h-4 w-4 text-white"),
                    on_click=lambda: FeedState.submit_comment(post["id"]),
                    class_name="rounded-full bg-[#1E9EF5] p-2.5 hover:bg-sky-600",
                ),
                class_name="mt-3 flex items-center gap-2",
            ),
            class_name="mt-3 border-t border-slate-100 pt-2",
        ),
    )


def owner_controls(post: PostRow) -> rx.Component:
    return rx.cond(
        post["is_owner"],
        rx.el.div(
            rx.el.button(
                rx.icon("pencil", class_name="h-4 w-4"),
                on_click=lambda: FeedState.start_edit(post["id"], post["body"]),
                class_name="rounded-full p-2 text-slate-400 hover:bg-slate-50 hover:text-[#1E9EF5]",
            ),
            rx.el.button(
                rx.icon("trash-2", class_name="h-4 w-4"),
                on_click=lambda: FeedState.delete_post(post["id"]),
                class_name="rounded-full p-2 text-slate-400 hover:bg-red-50 hover:text-red-500",
            ),
            class_name="flex items-center",
        ),
    )


def post_body(post: PostRow) -> rx.Component:
    return rx.cond(
        FeedState.editing_post_id == post["id"],
        rx.el.div(
            rx.el.textarea(
                default_value=FeedState.edit_body,
                on_change=FeedState.set_edit_body.debounce(300),
                rows="3",
                class_name="w-full resize-none rounded-xl border border-slate-200 p-3 text-sm text-[#0D1420] focus:border-[#1E9EF5] focus:ring-2 focus:ring-sky-100 outline-hidden",
            ),
            rx.el.div(
                rx.el.button(
                    "Save",
                    on_click=FeedState.save_edit,
                    class_name="rounded-full bg-[#1E9EF5] px-4 py-1.5 text-xs font-semibold text-white hover:bg-sky-600",
                ),
                rx.el.button(
                    "Cancel",
                    on_click=FeedState.cancel_edit,
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


def shared_block(post: PostRow) -> rx.Component:
    return rx.cond(
        post["shared_author"] != "",
        rx.el.div(
            rx.el.p(
                f"Shared from @{post['shared_author']}",
                class_name="text-xs font-semibold text-[#22D3EE]",
            ),
            rx.el.p(
                post["shared_body"],
                class_name="mt-1 text-sm text-slate-600 whitespace-pre-wrap",
            ),
            class_name="mt-3 rounded-xl border border-slate-200 bg-slate-50 p-3",
        ),
    )


def post_card(post: PostRow) -> rx.Component:
    return rx.el.article(
        rx.el.div(
            avatar(post["avatar_url"], post["avatar_remote"], "size-10"),
            rx.el.div(
                rx.el.div(
                    rx.el.span(
                        post["author_name"],
                        class_name="text-sm font-semibold text-[#0D1420]",
                    ),
                    rx.el.span(
                        f"@{post['author_username']}",
                        class_name="text-xs text-slate-400",
                    ),
                    class_name="flex flex-wrap items-center gap-2",
                ),
                rx.el.div(
                    rx.el.span(
                        post["time_label"], class_name="text-xs text-slate-400"
                    ),
                    rx.el.span("·", class_name="text-xs text-slate-300"),
                    privacy_icon(post["privacy"]),
                    rx.cond(
                        post["is_edited"],
                        rx.el.span(
                            "edited", class_name="text-xs italic text-slate-400"
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
            owner_controls(post),
            class_name="flex items-start gap-3",
        ),
        post_body(post),
        shared_block(post),
        media_grid(post),
        rx.el.div(
            rx.el.span(
                reaction_glyph(post["my_reaction"]),
                class_name="text-sm",
            ),
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
        rx.el.div(
            reaction_bar(post),
            rx.el.div(
                rx.el.button(
                    rx.icon("message-circle", class_name="h-4 w-4"),
                    rx.el.span("Comment", class_name="text-xs font-semibold"),
                    on_click=lambda: FeedState.toggle_comments(post["id"]),
                    class_name="flex items-center gap-1.5 rounded-full px-3 py-1.5 text-slate-600 hover:bg-slate-50",
                ),
                rx.el.button(
                    rx.icon("share-2", class_name="h-4 w-4"),
                    rx.el.span("Share", class_name="text-xs font-semibold"),
                    on_click=lambda: FeedState.open_share(post["id"]),
                    class_name="flex items-center gap-1.5 rounded-full px-3 py-1.5 text-slate-600 hover:bg-slate-50",
                ),
                class_name="flex items-center gap-1",
            ),
            class_name="mt-1 flex flex-wrap items-center justify-between gap-2",
        ),
        comment_panel(post),
        class_name="w-full rounded-2xl border border-slate-200 bg-white p-4",
    )


def share_dialog() -> rx.Component:
    return rx.cond(
        FeedState.share_post_id > 0,
        rx.el.div(
            rx.el.div(
                rx.el.div(
                    rx.el.h2(
                        "Share to your feed",
                        class_name="text-base font-semibold text-[#0D1420]",
                    ),
                    rx.el.button(
                        rx.icon("x", class_name="h-4 w-4"),
                        on_click=FeedState.close_share,
                        class_name="text-slate-400 hover:text-[#0D1420]",
                    ),
                    class_name="flex items-center justify-between border-b border-slate-200 px-4 py-3",
                ),
                rx.el.div(
                    rx.el.textarea(
                        placeholder="Add your thoughts (optional)",
                        default_value=FeedState.share_message,
                        on_change=FeedState.set_share_message.debounce(300),
                        rows="3",
                        class_name="w-full resize-none rounded-xl border border-slate-200 p-3 text-sm text-[#0D1420] focus:border-[#1E9EF5] focus:ring-2 focus:ring-sky-100 outline-hidden",
                    ),
                    rx.el.button(
                        "Share now",
                        on_click=FeedState.confirm_share,
                        class_name="mt-3 w-full rounded-xl bg-[#1E9EF5] py-2.5 text-sm font-semibold text-white hover:bg-sky-600",
                    ),
                    class_name="p-4",
                ),
                class_name="w-full max-w-md overflow-hidden rounded-2xl border border-slate-200 bg-white shadow-sm",
            ),
            class_name="fixed inset-0 z-50 flex items-center justify-center bg-[#0D1420]/60 p-4",
        ),
    )


def feed() -> rx.Component:
    return rx.el.section(
        rx.cond(
            FeedState.loading,
            rx.el.div(
                skeleton_card(),
                skeleton_card(),
                class_name="flex flex-col gap-3",
            ),
            rx.cond(
                FeedState.posts.length() > 0,
                rx.el.div(
                    rx.foreach(FeedState.posts, post_card),
                    class_name="flex flex-col gap-3",
                ),
                rx.el.div(
                    rx.icon("newspaper", class_name="h-8 w-8 text-[#1E9EF5]"),
                    rx.el.p(
                        "Your feed is empty",
                        class_name="mt-2 text-base font-semibold text-[#0D1420]",
                    ),
                    rx.el.p(
                        "Share your first post or add a story to get things moving.",
                        class_name="text-sm text-slate-500",
                    ),
                    class_name="flex flex-col items-center rounded-2xl border border-dashed border-slate-300 bg-white px-6 py-12 text-center",
                ),
            ),
        ),
        rx.cond(
            FeedState.has_more,
            rx.el.button(
                rx.cond(
                    FeedState.loading_more,
                    rx.el.span("Loading more..."),
                    rx.el.span("Load more posts"),
                ),
                on_click=FeedState.load_more,
                disabled=FeedState.loading_more,
                class_name="mt-3 w-full rounded-xl border border-slate-200 bg-white py-2.5 text-sm font-semibold text-[#1E9EF5] hover:border-[#1E9EF5] disabled:opacity-60",
            ),
            rx.cond(
                FeedState.posts.length() > 0,
                rx.el.p(
                    "You're all caught up.",
                    class_name="mt-3 text-center text-xs font-medium text-slate-400",
                ),
            ),
        ),
        share_dialog(),
        class_name="w-full",
    )
