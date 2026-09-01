"""Personal profile: identity, social counts, editing, uploads, own posts."""

from __future__ import annotations

import logging
from typing import Any, TypedDict

import reflex as rx
from sqlalchemy import bindparam, text

from app.media import (
    UploadError,
    avatar_source,
    media_source,
    relative_time,
    store_upload,
)
from app.states.auth_state import AuthState

PROFILE_PAGE_SIZE = 6
MAX_BIO = 280


class ProfileMedia(TypedDict):
    kind: str
    url: str
    is_remote: bool


class ProfilePost(TypedDict):
    id: int
    body: str
    privacy: str
    location: str
    is_edited: bool
    reaction_count: int
    comment_count: int
    share_count: int
    time_label: str
    media: list[ProfileMedia]


IDENTITY_SQL = """
SELECT a.username,
       COALESCE(p.display_name, ''),
       COALESCE(p.bio, ''),
       COALESCE(p.location, ''),
       COALESCE(p.website, ''),
       COALESCE(p.avatar_key, ''),
       COALESCE(p.cover_key, ''),
       a.created_at
FROM account a
LEFT JOIN profile p ON p.account_id = a.id
WHERE a.id = :me
"""

COUNTS_SQL = """
SELECT
    (SELECT COUNT(*) FROM post
      WHERE author_id = :me AND is_deleted = false) AS posts,
    (SELECT COUNT(*) FROM friendship
      WHERE account_low_id = :me OR account_high_id = :me) AS friends,
    (SELECT COUNT(*) FROM follow WHERE followee_id = :me) AS followers,
    (SELECT COUNT(*) FROM follow WHERE follower_id = :me) AS following
"""

OWN_POSTS_SQL = """
SELECT p.id, p.body, p.privacy, COALESCE(p.location, ''), p.is_edited,
       p.reaction_count, p.comment_count, p.share_count, p.created_at
FROM post p
WHERE p.author_id = :me AND p.is_deleted = false
ORDER BY p.created_at DESC, p.id DESC
LIMIT :limit OFFSET :offset
"""


def _valid_website(value: str) -> bool:
    if not value:
        return True
    lowered = value.lower()
    if not (lowered.startswith("http://") or lowered.startswith("https://")):
        return False
    remainder = value.split("://", 1)[1]
    return "." in remainder and " " not in remainder and len(remainder) > 3


class ProfileState(rx.State):
    username: str = ""
    display_name: str = ""
    bio: str = ""
    location: str = ""
    website: str = ""
    avatar_url: str = ""
    avatar_remote: bool = True
    cover_key: str = ""
    joined_label: str = ""

    post_count: int = 0
    friend_count: int = 0
    follower_count: int = 0
    following_count: int = 0

    posts: list[ProfilePost] = []
    loading: bool = False
    loading_more: bool = False
    has_more: bool = False
    offset: int = 0

    edit_open: bool = False
    edit_error: str = ""
    saving: bool = False
    form_display_name: str = ""
    form_bio: str = ""
    form_location: str = ""
    form_website: str = ""

    avatar_uploading: bool = False
    cover_uploading: bool = False
    upload_error: str = ""
    upload_success: str = ""

    editing_post_id: int = 0
    edit_body: str = ""

    @rx.var
    def has_cover(self) -> bool:
        return self.cover_key != ""

    @rx.var
    def cover_is_remote(self) -> bool:
        return self.cover_key.startswith("http")

    @rx.var
    def bio_remaining(self) -> int:
        return MAX_BIO - len(self.form_bio)

    async def _me(self) -> int:
        auth = await self.get_state(AuthState)
        return auth.account_id

    async def _fetch_posts(
        self, asession, me: int, offset: int
    ) -> list[ProfilePost]:
        rows = (
            await asession.execute(
                text(OWN_POSTS_SQL),
                {"me": me, "limit": PROFILE_PAGE_SIZE + 1, "offset": offset},
            )
        ).all()
        self.has_more = len(rows) > PROFILE_PAGE_SIZE
        rows = rows[:PROFILE_PAGE_SIZE]
        posts: list[ProfilePost] = [
            {
                "id": int(row[0]),
                "body": str(row[1]),
                "privacy": str(row[2]),
                "location": str(row[3]),
                "is_edited": bool(row[4]),
                "reaction_count": int(row[5] or 0),
                "comment_count": int(row[6] or 0),
                "share_count": int(row[7] or 0),
                "time_label": relative_time(row[8]),
                "media": [],
            }
            for row in rows
        ]
        if not posts:
            return posts
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
                {"ids": [post["id"] for post in posts]},
            )
        ).all()
        by_post: dict[int, list[ProfileMedia]] = {}
        for media in media_rows:
            url, is_remote = media_source(media[2])
            by_post.setdefault(int(media[0]), []).append(
                {"kind": str(media[1]), "url": url, "is_remote": is_remote}
            )
        for post in posts:
            post["media"] = by_post.get(post["id"], [])
        return posts

    @rx.event
    async def load_profile(self):
        me = await self._me()
        if not me:
            return
        self.loading = True
        self.offset = 0
        self.upload_error = ""
        self.upload_success = ""
        yield
        async with rx.asession() as asession:
            identity = (
                await asession.execute(text(IDENTITY_SQL), {"me": me})
            ).first()
            counts = (
                await asession.execute(text(COUNTS_SQL), {"me": me})
            ).first()
            posts = await self._fetch_posts(asession, me, 0)
        if identity is not None:
            self.username = str(identity[0])
            self.display_name = str(identity[1]) or str(identity[0])
            self.bio = str(identity[2])
            self.location = str(identity[3])
            self.website = str(identity[4])
            url, remote = avatar_source(identity[5], identity[0])
            self.avatar_url = url
            self.avatar_remote = remote
            self.cover_key = str(identity[6])
            self.joined_label = relative_time(identity[7])
        if counts is not None:
            self.post_count = int(counts[0] or 0)
            self.friend_count = int(counts[1] or 0)
            self.follower_count = int(counts[2] or 0)
            self.following_count = int(counts[3] or 0)
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
            posts = await self._fetch_posts(asession, me, self.offset)
        self.posts = self.posts + posts
        self.offset += len(posts)
        self.loading_more = False

    # ------------------------------------------------------------ edit profile

    @rx.event
    def open_edit(self):
        self.edit_open = True
        self.edit_error = ""
        self.form_display_name = self.display_name
        self.form_bio = self.bio
        self.form_location = self.location
        self.form_website = self.website

    @rx.event
    def close_edit(self):
        self.edit_open = False
        self.edit_error = ""

    @rx.event
    def set_form_bio(self, value: str):
        self.form_bio = value

    @rx.event
    async def save_profile(self, form_data: dict[str, Any]):
        me = await self._me()
        if not me:
            self.edit_error = "You are not signed in."
            return
        display_name = str(form_data.get("display_name", "")).strip()
        bio = str(form_data.get("bio", "")).strip()
        location = str(form_data.get("location", "")).strip()
        website = str(form_data.get("website", "")).strip()

        if len(display_name) < 2 or len(display_name) > 80:
            self.edit_error = "Display name must be 2-80 characters."
            return
        if len(bio) > MAX_BIO:
            self.edit_error = f"Bio must be {MAX_BIO} characters or fewer."
            return
        if len(location) > 120:
            self.edit_error = "Location must be 120 characters or fewer."
            return
        if len(website) > 255 or not _valid_website(website):
            self.edit_error = (
                "Website must be a full http:// or https:// address."
            )
            return

        self.saving = True
        self.edit_error = ""
        yield
        async with rx.asession() as asession:
            await asession.execute(
                text(
                    """
                    UPDATE profile
                    SET display_name = :display_name, bio = :bio,
                        location = :location, website = :website,
                        updated_at = NOW()
                    WHERE account_id = :me
                    """
                ),
                {
                    "display_name": display_name,
                    "bio": bio,
                    "location": location,
                    "website": website,
                    "me": me,
                },
            )
            auth = await self.get_state(AuthState)
            await auth._load_identity(asession, me)
            await asession.commit()
        self.display_name = display_name
        self.bio = bio
        self.location = location
        self.website = website
        self.saving = False
        self.edit_open = False
        yield rx.toast("Profile updated.", duration=2500)

    # ------------------------------------------------------------- image uploads

    async def _store_image(self, files: list[rx.UploadFile]) -> str:
        if not files:
            raise UploadError("Choose an image first.")
        meta = await store_upload(files[0])
        if str(meta["kind"]) != "image":
            raise UploadError("Only PNG, JPG, WEBP or GIF images are allowed.")
        return str(meta["storage_key"])

    @rx.event
    async def upload_avatar(self, files: list[rx.UploadFile]):
        me = await self._me()
        if not me:
            return
        self.avatar_uploading = True
        self.upload_error = ""
        self.upload_success = ""
        yield
        try:
            storage_key = await self._store_image(files)
        except UploadError as error:
            logging.exception(f"Avatar upload rejected: {error}")
            self.upload_error = str(error)
            self.avatar_uploading = False
            return
        async with rx.asession() as asession:
            await asession.execute(
                text(
                    """
                    UPDATE profile
                    SET avatar_key = :key, updated_at = NOW()
                    WHERE account_id = :me
                    """
                ),
                {"key": storage_key, "me": me},
            )
            auth = await self.get_state(AuthState)
            await auth._load_identity(asession, me)
            await asession.commit()
        url, remote = avatar_source(storage_key, self.username)
        self.avatar_url = url
        self.avatar_remote = remote
        self.avatar_uploading = False
        self.upload_success = "New profile photo saved."
        yield rx.toast("Profile photo updated.", duration=2500)

    @rx.event
    async def upload_cover(self, files: list[rx.UploadFile]):
        me = await self._me()
        if not me:
            return
        self.cover_uploading = True
        self.upload_error = ""
        self.upload_success = ""
        yield
        try:
            storage_key = await self._store_image(files)
        except UploadError as error:
            logging.exception(f"Cover upload rejected: {error}")
            self.upload_error = str(error)
            self.cover_uploading = False
            return
        async with rx.asession() as asession:
            await asession.execute(
                text(
                    """
                    UPDATE profile
                    SET cover_key = :key, updated_at = NOW()
                    WHERE account_id = :me
                    """
                ),
                {"key": storage_key, "me": me},
            )
            await asession.commit()
        self.cover_key = storage_key
        self.cover_uploading = False
        self.upload_success = "New cover image saved."
        yield rx.toast("Cover image updated.", duration=2500)

    # --------------------------------------------------------- post edit/delete

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
    async def save_post_edit(self):
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
                {"body": body[:4000], "id": post_id, "me": me},
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
        self.post_count = max(self.post_count - 1, 0)
        return rx.toast("Post deleted.", duration=2000)
