"""Expiring stories: rail, creation, full-screen viewer, reactions, replies."""

from __future__ import annotations

import datetime as dt
import logging
from typing import TypedDict

import reflex as rx
from sqlalchemy import text

from app.media import (
    UploadError,
    avatar_source,
    media_source,
    relative_time,
    store_upload,
)
from app.models import Story, StoryMedia, StoryReply
from app.states.auth_state import AuthState

STORY_HOURS = 24


class StoryRow(TypedDict):
    id: int
    author_id: int
    author_name: str
    author_username: str
    avatar_url: str
    avatar_remote: bool
    caption: str
    background_color: str
    media_url: str
    media_remote: bool
    media_kind: str
    has_media: bool
    view_count: int
    reaction_count: int
    reply_count: int
    time_label: str
    my_reaction: str
    is_mine: bool
    seen: bool


class StoryReplyRow(TypedDict):
    id: int
    author_name: str
    body: str
    time_label: str


STORY_SQL = """
SELECT s.id, s.author_id, a.username, COALESCE(pr.display_name, ''),
       COALESCE(pr.avatar_key, ''), s.caption, COALESCE(s.background_color, ''),
       s.view_count, s.reaction_count, s.reply_count, s.created_at,
       COALESCE(sm.kind, '') AS media_kind,
       COALESCE(sm.storage_key, '') AS media_key,
       COALESCE((SELECT r.kind FROM story_reaction r
                 WHERE r.story_id = s.id AND r.account_id = :me), '') AS my_reaction,
       EXISTS (SELECT 1 FROM story_view v
               WHERE v.story_id = s.id AND v.account_id = :me) AS seen
FROM story s
JOIN account a ON a.id = s.author_id
LEFT JOIN profile pr ON pr.account_id = a.id
LEFT JOIN story_media sm ON sm.story_id = s.id AND sm.position = 0
WHERE s.is_deleted = false
  AND s.expires_at > NOW()
  AND (
    s.privacy = 'public'
    OR s.author_id = :me
    OR (s.privacy = 'friends' AND EXISTS (
        SELECT 1 FROM friendship f
        WHERE f.account_low_id = LEAST(s.author_id, :me)
          AND f.account_high_id = GREATEST(s.author_id, :me)
    ))
  )
ORDER BY (s.author_id = :me) DESC, s.created_at DESC
LIMIT 40
"""


class StoryState(rx.State):
    stories: list[StoryRow] = []
    loading: bool = False

    viewer_open: bool = False
    viewer_index: int = 0
    viewer_replies: list[StoryReplyRow] = []
    reply_draft: str = ""

    create_open: bool = False
    caption: str = ""
    background_color: str = "#1E9EF5"
    privacy: str = "public"
    pending_kind: str = ""
    pending_key: str = ""
    pending_url: str = ""
    pending_remote: bool = False
    pending_name: str = ""
    pending_mime: str = ""
    pending_size: int = 0
    create_error: str = ""
    creating: bool = False

    @rx.var
    def story_count(self) -> int:
        return len(self.stories)

    @rx.var
    def current_story(self) -> StoryRow:
        if 0 <= self.viewer_index < len(self.stories):
            return self.stories[self.viewer_index]
        return {
            "id": 0,
            "author_id": 0,
            "author_name": "",
            "author_username": "",
            "avatar_url": "",
            "avatar_remote": True,
            "caption": "",
            "background_color": "#1E9EF5",
            "media_url": "",
            "media_remote": False,
            "media_kind": "",
            "has_media": False,
            "view_count": 0,
            "reaction_count": 0,
            "reply_count": 0,
            "time_label": "",
            "my_reaction": "",
            "is_mine": False,
            "seen": False,
        }

    async def _me(self) -> int:
        auth = await self.get_state(AuthState)
        return auth.account_id

    @rx.event
    async def load_stories(self):
        me = await self._me()
        if not me:
            return
        self.loading = True
        yield
        async with rx.asession() as asession:
            rows = (await asession.execute(text(STORY_SQL), {"me": me})).all()
        stories: list[StoryRow] = []
        for row in rows:
            avatar_url, avatar_remote = avatar_source(row[4], row[2])
            media_url, media_remote = media_source(row[12])
            stories.append(
                {
                    "id": int(row[0]),
                    "author_id": int(row[1]),
                    "author_name": str(row[3]) or str(row[2]),
                    "author_username": str(row[2]),
                    "avatar_url": avatar_url,
                    "avatar_remote": avatar_remote,
                    "caption": str(row[5]),
                    "background_color": str(row[6]) or "#1E9EF5",
                    "media_url": media_url,
                    "media_remote": media_remote,
                    "media_kind": str(row[11]),
                    "has_media": bool(row[12]),
                    "view_count": int(row[7]),
                    "reaction_count": int(row[8]),
                    "reply_count": int(row[9]),
                    "time_label": relative_time(row[10]),
                    "my_reaction": str(row[13]),
                    "is_mine": int(row[1]) == me,
                    "seen": bool(row[14]),
                }
            )
        self.stories = stories
        self.loading = False

    # ------------------------------------------------------------------ viewer

    @rx.event
    async def open_viewer(self, index: int):
        if index < 0 or index >= len(self.stories):
            return
        self.viewer_index = index
        self.viewer_open = True
        self.reply_draft = ""
        async for update in self._register_view():
            yield update

    async def _register_view(self):
        me = await self._me()
        story = self.current_story
        story_id = int(story["id"])
        if not me or not story_id:
            return
        async with rx.asession() as asession:
            inserted = await asession.execute(
                text(
                    """
                    INSERT INTO story_view (story_id, account_id, viewed_at)
                    VALUES (:story_id, :me, NOW())
                    ON CONFLICT (story_id, account_id) DO NOTHING
                    """
                ),
                {"story_id": story_id, "me": me},
            )
            if inserted.rowcount:
                await asession.execute(
                    text(
                        """
                        UPDATE story SET view_count = view_count + 1
                        WHERE id = :id
                        """
                    ),
                    {"id": story_id},
                )
            replies = (
                await asession.execute(
                    text(
                        """
                        SELECT r.id, COALESCE(p.display_name, a.username),
                               r.body, r.created_at
                        FROM story_reply r
                        JOIN account a ON a.id = r.author_id
                        LEFT JOIN profile p ON p.account_id = a.id
                        WHERE r.story_id = :story_id AND r.is_deleted = false
                        ORDER BY r.created_at DESC
                        LIMIT 20
                        """
                    ),
                    {"story_id": story_id},
                )
            ).all()
            await asession.commit()
        self.viewer_replies = [
            {
                "id": int(row[0]),
                "author_name": str(row[1]),
                "body": str(row[2]),
                "time_label": relative_time(row[3]),
            }
            for row in replies
        ]
        self.stories = [
            {
                **item,
                "seen": True,
                "view_count": item["view_count"]
                + (1 if not item["seen"] else 0),
            }
            if item["id"] == story_id
            else item
            for item in self.stories
        ]
        yield

    @rx.event
    def close_viewer(self):
        self.viewer_open = False
        self.viewer_replies = []
        self.reply_draft = ""

    @rx.event
    async def next_story(self):
        if self.viewer_index + 1 >= len(self.stories):
            self.viewer_open = False
            return
        self.viewer_index += 1
        self.reply_draft = ""
        async for update in self._register_view():
            yield update

    @rx.event
    async def prev_story(self):
        if self.viewer_index == 0:
            return
        self.viewer_index -= 1
        self.reply_draft = ""
        async for update in self._register_view():
            yield update

    @rx.event
    async def react_to_story(self, kind: str):
        me = await self._me()
        story_id = int(self.current_story["id"])
        if not me or not story_id:
            return
        async with rx.asession() as asession:
            existing = (
                await asession.execute(
                    text(
                        """
                        SELECT kind FROM story_reaction
                        WHERE story_id = :story_id AND account_id = :me
                        """
                    ),
                    {"story_id": story_id, "me": me},
                )
            ).first()
            if existing is None:
                await asession.execute(
                    text(
                        """
                        INSERT INTO story_reaction
                            (story_id, account_id, kind, created_at)
                        VALUES (:story_id, :me, :kind, NOW())
                        """
                    ),
                    {"story_id": story_id, "me": me, "kind": kind},
                )
                await asession.execute(
                    text(
                        """
                        UPDATE story SET reaction_count = reaction_count + 1
                        WHERE id = :id
                        """
                    ),
                    {"id": story_id},
                )
                delta, new_kind = 1, kind
            elif str(existing[0]) == kind:
                await asession.execute(
                    text(
                        """
                        DELETE FROM story_reaction
                        WHERE story_id = :story_id AND account_id = :me
                        """
                    ),
                    {"story_id": story_id, "me": me},
                )
                await asession.execute(
                    text(
                        """
                        UPDATE story
                        SET reaction_count = GREATEST(reaction_count - 1, 0)
                        WHERE id = :id
                        """
                    ),
                    {"id": story_id},
                )
                delta, new_kind = -1, ""
            else:
                await asession.execute(
                    text(
                        """
                        UPDATE story_reaction SET kind = :kind
                        WHERE story_id = :story_id AND account_id = :me
                        """
                    ),
                    {"story_id": story_id, "me": me, "kind": kind},
                )
                delta, new_kind = 0, kind
            await asession.commit()
        self.stories = [
            {
                **item,
                "my_reaction": new_kind,
                "reaction_count": max(item["reaction_count"] + delta, 0),
            }
            if item["id"] == story_id
            else item
            for item in self.stories
        ]

    @rx.event
    def set_reply_draft(self, value: str):
        self.reply_draft = value

    @rx.event
    async def submit_story_reply(self):
        me = await self._me()
        story_id = int(self.current_story["id"])
        body = self.reply_draft.strip()
        if not me or not story_id or not body:
            return
        now = dt.datetime.now(dt.UTC)
        async with rx.asession() as asession:
            asession.add(
                StoryReply(
                    story_id=story_id,
                    author_id=me,
                    body=body[:2000],
                    created_at=now,
                )
            )
            await asession.execute(
                text(
                    """
                    UPDATE story SET reply_count = reply_count + 1
                    WHERE id = :id
                    """
                ),
                {"id": story_id},
            )
            await asession.commit()
        auth = await self.get_state(AuthState)
        self.viewer_replies = [
            {
                "id": 0,
                "author_name": auth.display_name,
                "body": body,
                "time_label": "just now",
            }
        ] + self.viewer_replies
        self.reply_draft = ""
        self.stories = [
            {**item, "reply_count": item["reply_count"] + 1}
            if item["id"] == story_id
            else item
            for item in self.stories
        ]

    # ---------------------------------------------------------------- creation

    @rx.event
    def open_create(self):
        self.create_open = True
        self.create_error = ""

    @rx.event
    def close_create(self):
        self.create_open = False
        self.caption = ""
        self.pending_kind = ""
        self.pending_key = ""
        self.pending_url = ""
        self.pending_name = ""
        self.create_error = ""

    @rx.event
    def set_caption(self, value: str):
        self.caption = value

    @rx.event
    def set_background_color(self, value: str):
        self.background_color = value

    @rx.event
    def set_privacy(self, value: str):
        self.privacy = value

    @rx.event
    async def handle_story_upload(self, files: list[rx.UploadFile]):
        self.create_error = ""
        if not files:
            return
        try:
            meta = await store_upload(files[0])
        except UploadError as error:
            logging.exception(f"Story upload rejected: {error}")
            self.create_error = str(error)
            return
        url, remote = media_source(meta["storage_key"])
        self.pending_kind = str(meta["kind"])
        self.pending_key = str(meta["storage_key"])
        self.pending_name = str(meta["original_name"])
        self.pending_mime = str(meta["mime_type"])
        self.pending_size = int(meta["size_bytes"])
        self.pending_url = url
        self.pending_remote = remote

    @rx.event
    async def submit_story(self):
        me = await self._me()
        if not me:
            return
        if not self.caption.strip() and not self.pending_key:
            self.create_error = "Add a caption, photo or video."
            return
        self.creating = True
        yield
        now = dt.datetime.now(dt.UTC)
        async with rx.asession() as asession:
            story = Story(
                author_id=me,
                caption=self.caption.strip()[:2000],
                background_color=(
                    "" if self.pending_key else self.background_color
                ),
                privacy=self.privacy,
                expires_at=now + dt.timedelta(hours=STORY_HOURS),
                created_at=now,
                updated_at=now,
            )
            asession.add(story)
            await asession.flush()
            if self.pending_key:
                asession.add(
                    StoryMedia(
                        story_id=story.id,
                        kind=self.pending_kind,
                        storage_key=self.pending_key,
                        original_name=self.pending_name,
                        mime_type=self.pending_mime,
                        size_bytes=self.pending_size,
                        position=0,
                        created_at=now,
                    )
                )
            await asession.commit()
        self.creating = False
        self.create_open = False
        self.caption = ""
        self.pending_key = ""
        self.pending_url = ""
        self.pending_kind = ""
        yield StoryState.load_stories
        yield rx.toast("Story added - live for 24 hours.", duration=2500)
