"""Paginated social feed: composer, reactions, threaded comments, sharing."""

from __future__ import annotations

import datetime as dt
import logging
from typing import TypedDict

import reflex as rx
from sqlalchemy import bindparam, text

from app.media import (
    UploadError,
    avatar_source,
    media_source,
    relative_time,
    store_upload,
)
from app.models import Comment, Post, PostMedia, PostShare
from app.states.auth_state import AuthState

PAGE_SIZE = 5


class MediaRow(TypedDict):
    kind: str
    url: str
    is_remote: bool


class CommentRow(TypedDict):
    id: int
    author_name: str
    author_username: str
    avatar_url: str
    avatar_remote: bool
    body: str
    time_label: str
    depth: int
    is_owner: bool


class PostRow(TypedDict):
    id: int
    author_id: int
    author_name: str
    author_username: str
    avatar_url: str
    avatar_remote: bool
    body: str
    privacy: str
    location: str
    is_edited: bool
    reaction_count: int
    comment_count: int
    share_count: int
    time_label: str
    my_reaction: str
    is_owner: bool
    shared_author: str
    shared_body: str
    media: list[MediaRow]
    comments: list[CommentRow]


class PendingMedia(TypedDict):
    kind: str
    storage_key: str
    original_name: str
    mime_type: str
    size_bytes: int
    url: str
    is_remote: bool


FEED_SQL = """
SELECT p.id, p.author_id, a.username, COALESCE(pr.display_name, ''),
       COALESCE(pr.avatar_key, ''), p.body, p.privacy, COALESCE(p.location, ''),
       p.is_edited, p.reaction_count, p.comment_count, p.share_count,
       p.created_at,
       COALESCE((SELECT r.kind FROM post_reaction r
                 WHERE r.post_id = p.id AND r.account_id = :me), '') AS my_reaction,
       COALESCE(sa.username, '') AS shared_author,
       COALESCE(sp.body, '') AS shared_body
FROM post p
JOIN account a ON a.id = p.author_id
LEFT JOIN profile pr ON pr.account_id = a.id
LEFT JOIN post sp ON sp.id = p.shared_post_id
LEFT JOIN account sa ON sa.id = sp.author_id
WHERE p.is_deleted = false
  AND (
    p.privacy = 'public'
    OR p.author_id = :me
    OR (p.privacy = 'friends' AND EXISTS (
        SELECT 1 FROM friendship f
        WHERE f.account_low_id = LEAST(p.author_id, :me)
          AND f.account_high_id = GREATEST(p.author_id, :me)
    ))
  )
ORDER BY p.created_at DESC, p.id DESC
LIMIT :limit OFFSET :offset
"""

COMMENT_SQL = """
SELECT c.id, c.author_id, a.username, COALESCE(pr.display_name, ''),
       COALESCE(pr.avatar_key, ''), c.body, c.created_at, c.depth
FROM comment c
JOIN account a ON a.id = c.author_id
LEFT JOIN profile pr ON pr.account_id = a.id
WHERE c.post_id = :post_id AND c.is_deleted = false
ORDER BY COALESCE(c.parent_id, c.id) ASC, c.created_at ASC
LIMIT 60
"""


class FeedState(rx.State):
    posts: list[PostRow] = []
    loading: bool = False
    loading_more: bool = False
    has_more: bool = False
    offset: int = 0

    composer_body: str = ""
    composer_privacy: str = "public"
    composer_media: list[PendingMedia] = []
    composer_error: str = ""
    posting: bool = False

    open_post_id: int = 0
    comment_draft: str = ""
    reply_parent_id: int = 0

    editing_post_id: int = 0
    edit_body: str = ""

    share_post_id: int = 0
    share_message: str = ""

    async def _me(self) -> int:
        auth = await self.get_state(AuthState)
        return auth.account_id

    def _row_to_post(self, row, me: int) -> PostRow:
        avatar_url, avatar_remote = avatar_source(row[4], row[2])
        return {
            "id": int(row[0]),
            "author_id": int(row[1]),
            "author_name": str(row[3]) or str(row[2]),
            "author_username": str(row[2]),
            "avatar_url": avatar_url,
            "avatar_remote": avatar_remote,
            "body": str(row[5]),
            "privacy": str(row[6]),
            "location": str(row[7]),
            "is_edited": bool(row[8]),
            "reaction_count": int(row[9]),
            "comment_count": int(row[10]),
            "share_count": int(row[11]),
            "time_label": relative_time(row[12]),
            "my_reaction": str(row[13]),
            "is_owner": int(row[1]) == me,
            "shared_author": str(row[14]),
            "shared_body": str(row[15]),
            "media": [],
            "comments": [],
        }

    async def _fetch_page(
        self, asession, me: int, offset: int
    ) -> list[PostRow]:
        rows = (
            await asession.execute(
                text(FEED_SQL),
                {"me": me, "limit": PAGE_SIZE + 1, "offset": offset},
            )
        ).all()
        self.has_more = len(rows) > PAGE_SIZE
        rows = rows[:PAGE_SIZE]
        posts = [self._row_to_post(row, me) for row in rows]
        if not posts:
            return posts
        ids = [post["id"] for post in posts]
        media_rows = (
            await asession.execute(
                text(
                    """
                    SELECT post_id, kind, storage_key
                    FROM post_media
                    WHERE post_id IN :ids
                    ORDER BY post_id, position
                    """
                ).bindparams(bindparam("ids", expanding=True)),
                {"ids": ids},
            )
        ).all()
        by_post: dict[int, list[MediaRow]] = {}
        for media in media_rows:
            url, is_remote = media_source(media[2])
            by_post.setdefault(int(media[0]), []).append(
                {"kind": str(media[1]), "url": url, "is_remote": is_remote}
            )
        for post in posts:
            post["media"] = by_post.get(post["id"], [])
        return posts

    @rx.event
    async def load_feed(self):
        me = await self._me()
        if not me:
            return
        self.loading = True
        self.offset = 0
        yield
        async with rx.asession() as asession:
            posts = await self._fetch_page(asession, me, 0)
        self.posts = posts
        self.offset = len(posts)
        self.loading = False

    @rx.event
    async def load_more(self):
        me = await self._me()
        if not me or self.loading_more:
            return
        self.loading_more = True
        yield
        async with rx.asession() as asession:
            posts = await self._fetch_page(asession, me, self.offset)
        self.posts = self.posts + posts
        self.offset += len(posts)
        self.loading_more = False

    # ---------------------------------------------------------------- composer

    @rx.event
    def set_composer_body(self, value: str):
        self.composer_body = value

    @rx.event
    def set_composer_privacy(self, value: str):
        self.composer_privacy = value

    @rx.event
    async def handle_composer_upload(self, files: list[rx.UploadFile]):
        self.composer_error = ""
        for file in files[:6]:
            try:
                meta = await store_upload(file)
            except UploadError as error:
                logging.exception(f"Upload rejected: {error}")
                self.composer_error = str(error)
                continue
            url, is_remote = media_source(meta["storage_key"])
            self.composer_media.append(
                {
                    "kind": str(meta["kind"]),
                    "storage_key": str(meta["storage_key"]),
                    "original_name": str(meta["original_name"]),
                    "mime_type": str(meta["mime_type"]),
                    "size_bytes": int(meta["size_bytes"]),
                    "url": url,
                    "is_remote": is_remote,
                }
            )

    @rx.event
    def remove_composer_media(self, storage_key: str):
        self.composer_media = [
            item
            for item in self.composer_media
            if item["storage_key"] != storage_key
        ]

    @rx.event
    async def submit_post(self):
        me = await self._me()
        if not me:
            return
        if not self.composer_body.strip() and not self.composer_media:
            self.composer_error = "Write something or add a photo or video."
            return
        self.posting = True
        self.composer_error = ""
        yield
        now = dt.datetime.now(dt.UTC)
        async with rx.asession() as asession:
            post = Post(
                author_id=me,
                body=self.composer_body.strip(),
                privacy=self.composer_privacy,
                created_at=now,
                updated_at=now,
            )
            asession.add(post)
            await asession.flush()
            for position, item in enumerate(self.composer_media):
                asession.add(
                    PostMedia(
                        post_id=post.id,
                        kind=item["kind"],
                        storage_key=item["storage_key"],
                        original_name=item["original_name"],
                        mime_type=item["mime_type"],
                        size_bytes=item["size_bytes"],
                        position=position,
                        created_at=now,
                    )
                )
            await asession.commit()
        self.composer_body = ""
        self.composer_media = []
        self.posting = False
        yield FeedState.load_feed
        yield rx.toast("Your post is live.", duration=2500)

    # --------------------------------------------------------------- reactions

    @rx.event
    async def react(self, post_id: int, kind: str):
        me = await self._me()
        if not me:
            return
        async with rx.asession() as asession:
            existing = (
                await asession.execute(
                    text(
                        """
                        SELECT kind FROM post_reaction
                        WHERE post_id = :post_id AND account_id = :me
                        """
                    ),
                    {"post_id": post_id, "me": me},
                )
            ).first()
            if existing is None:
                await asession.execute(
                    text(
                        """
                        INSERT INTO post_reaction
                            (post_id, account_id, kind, created_at, updated_at)
                        VALUES (:post_id, :me, :kind, NOW(), NOW())
                        """
                    ),
                    {"post_id": post_id, "me": me, "kind": kind},
                )
                await asession.execute(
                    text(
                        """
                        UPDATE post SET reaction_count = reaction_count + 1
                        WHERE id = :post_id
                        """
                    ),
                    {"post_id": post_id},
                )
                new_kind = kind
            elif str(existing[0]) == kind:
                await asession.execute(
                    text(
                        """
                        DELETE FROM post_reaction
                        WHERE post_id = :post_id AND account_id = :me
                        """
                    ),
                    {"post_id": post_id, "me": me},
                )
                await asession.execute(
                    text(
                        """
                        UPDATE post
                        SET reaction_count = GREATEST(reaction_count - 1, 0)
                        WHERE id = :post_id
                        """
                    ),
                    {"post_id": post_id},
                )
                new_kind = ""
            else:
                await asession.execute(
                    text(
                        """
                        UPDATE post_reaction SET kind = :kind, updated_at = NOW()
                        WHERE post_id = :post_id AND account_id = :me
                        """
                    ),
                    {"post_id": post_id, "me": me, "kind": kind},
                )
                new_kind = kind
            row = (
                await asession.execute(
                    text("SELECT reaction_count FROM post WHERE id = :id"),
                    {"id": post_id},
                )
            ).first()
            await asession.commit()
        total = int(row[0]) if row else 0
        self.posts = [
            {**post, "my_reaction": new_kind, "reaction_count": total}
            if post["id"] == post_id
            else post
            for post in self.posts
        ]

    # ---------------------------------------------------------------- comments

    async def _load_comments(self, post_id: int) -> list[CommentRow]:
        me = await self._me()
        async with rx.asession() as asession:
            rows = (
                await asession.execute(text(COMMENT_SQL), {"post_id": post_id})
            ).all()
        comments: list[CommentRow] = []
        for row in rows:
            avatar_url, avatar_remote = avatar_source(row[4], row[2])
            comments.append(
                {
                    "id": int(row[0]),
                    "author_name": str(row[3]) or str(row[2]),
                    "author_username": str(row[2]),
                    "avatar_url": avatar_url,
                    "avatar_remote": avatar_remote,
                    "body": str(row[5]),
                    "time_label": relative_time(row[6]),
                    "depth": int(row[7]),
                    "is_owner": int(row[1]) == me,
                }
            )
        return comments

    def _apply_comments(self, post_id: int, comments: list[CommentRow]):
        self.posts = [
            {**post, "comments": comments} if post["id"] == post_id else post
            for post in self.posts
        ]

    @rx.event
    async def toggle_comments(self, post_id: int):
        self.reply_parent_id = 0
        self.comment_draft = ""
        if self.open_post_id == post_id:
            self.open_post_id = 0
            return
        self.open_post_id = post_id
        comments = await self._load_comments(post_id)
        self._apply_comments(post_id, comments)

    @rx.event
    def set_comment_draft(self, value: str):
        self.comment_draft = value

    @rx.event
    def set_reply_parent(self, comment_id: int):
        self.reply_parent_id = comment_id
        self.comment_draft = ""

    @rx.event
    async def submit_comment(self, post_id: int):
        me = await self._me()
        body = self.comment_draft.strip()
        if not me or not body:
            return
        now = dt.datetime.now(dt.UTC)
        parent_id = self.reply_parent_id or None
        async with rx.asession() as asession:
            comment = Comment(
                post_id=post_id,
                author_id=me,
                parent_id=parent_id,
                depth=1 if parent_id else 0,
                body=body[:4000],
                created_at=now,
                updated_at=now,
            )
            asession.add(comment)
            await asession.flush()
            await asession.execute(
                text(
                    """
                    UPDATE post SET comment_count = comment_count + 1
                    WHERE id = :post_id
                    """
                ),
                {"post_id": post_id},
            )
            if parent_id:
                await asession.execute(
                    text(
                        """
                        UPDATE comment SET reply_count = reply_count + 1
                        WHERE id = :parent_id
                        """
                    ),
                    {"parent_id": parent_id},
                )
            await asession.commit()
        self.comment_draft = ""
        self.reply_parent_id = 0
        comments = await self._load_comments(post_id)
        self.posts = [
            {
                **post,
                "comments": comments,
                "comment_count": post["comment_count"] + 1,
            }
            if post["id"] == post_id
            else post
            for post in self.posts
        ]

    # ------------------------------------------------- owner edit/delete/share

    @rx.event
    def start_edit(self, post_id: int, body: str):
        self.editing_post_id = post_id
        self.edit_body = body

    @rx.event
    def set_edit_body(self, value: str):
        self.edit_body = value

    @rx.event
    def cancel_edit(self):
        self.editing_post_id = 0
        self.edit_body = ""

    @rx.event
    async def save_edit(self):
        me = await self._me()
        post_id = self.editing_post_id
        body = self.edit_body.strip()
        if not me or not post_id or not body:
            return
        async with rx.asession() as asession:
            await asession.execute(
                text(
                    """
                    UPDATE post
                    SET body = :body, is_edited = true, updated_at = NOW()
                    WHERE id = :id AND author_id = :me
                    """
                ),
                {"body": body, "id": post_id, "me": me},
            )
            await asession.commit()
        self.posts = [
            {**post, "body": body, "is_edited": True}
            if post["id"] == post_id
            else post
            for post in self.posts
        ]
        self.editing_post_id = 0
        self.edit_body = ""
        return rx.toast("Post updated.", duration=2000)

    @rx.event
    async def delete_post(self, post_id: int):
        me = await self._me()
        if not me:
            return
        async with rx.asession() as asession:
            await asession.execute(
                text(
                    """
                    UPDATE post SET is_deleted = true, updated_at = NOW()
                    WHERE id = :id AND author_id = :me
                    """
                ),
                {"id": post_id, "me": me},
            )
            await asession.commit()
        self.posts = [post for post in self.posts if post["id"] != post_id]
        return rx.toast("Post deleted.", duration=2000)

    @rx.event
    def open_share(self, post_id: int):
        self.share_post_id = post_id
        self.share_message = ""

    @rx.event
    def close_share(self):
        self.share_post_id = 0
        self.share_message = ""

    @rx.event
    def set_share_message(self, value: str):
        self.share_message = value

    @rx.event
    async def confirm_share(self):
        me = await self._me()
        post_id = self.share_post_id
        if not me or not post_id:
            return
        now = dt.datetime.now(dt.UTC)
        async with rx.asession() as asession:
            asession.add(
                PostShare(
                    post_id=post_id,
                    account_id=me,
                    channel="feed",
                    message=self.share_message.strip()[:255],
                    privacy="public",
                    created_at=now,
                )
            )
            repost = Post(
                author_id=me,
                body=self.share_message.strip(),
                privacy="public",
                shared_post_id=post_id,
                created_at=now,
                updated_at=now,
            )
            asession.add(repost)
            await asession.execute(
                text(
                    """
                    UPDATE post SET share_count = share_count + 1
                    WHERE id = :id
                    """
                ),
                {"id": post_id},
            )
            await asession.commit()
        self.share_post_id = 0
        self.share_message = ""
        yield FeedState.load_feed
        yield rx.toast("Shared to your feed.", duration=2500)
