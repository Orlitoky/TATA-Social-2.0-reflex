"""People directory: search, requests, friendships, follows and suggestions."""

from __future__ import annotations

from typing import TypedDict

import reflex as rx
from sqlalchemy import text

from app.media import avatar_source, relative_time
from app.states.auth_state import AuthState


class PersonCard(TypedDict):
    id: int
    display_name: str
    username: str
    avatar_url: str
    avatar_remote: bool
    is_online: bool
    status_label: str
    relation: str
    is_following: bool
    mutuals: int
    bio: str


class ProfileDetail(TypedDict):
    id: int
    display_name: str
    username: str
    avatar_url: str
    avatar_remote: bool
    is_online: bool
    status_label: str
    relation: str
    is_following: bool
    mutuals: int
    bio: str
    location: str
    friend_count: int
    follower_count: int
    following_count: int
    post_count: int


EMPTY_PROFILE: ProfileDetail = {
    "id": 0,
    "display_name": "",
    "username": "",
    "avatar_url": "",
    "avatar_remote": True,
    "is_online": False,
    "status_label": "",
    "relation": "none",
    "is_following": False,
    "mutuals": 0,
    "bio": "",
    "location": "",
    "friend_count": 0,
    "follower_count": 0,
    "following_count": 0,
    "post_count": 0,
}

PERSON_COLUMNS = """
    a.id, a.username, COALESCE(p.display_name, ''), COALESCE(p.avatar_key, ''),
    a.is_online, a.last_seen_at, COALESCE(p.bio, ''),
    CASE WHEN fr.id IS NOT NULL THEN 'friend'
         WHEN ri.id IS NOT NULL THEN 'incoming'
         WHEN ro.id IS NOT NULL THEN 'outgoing'
         ELSE 'none' END AS relation,
    CASE WHEN fo.id IS NOT NULL THEN true ELSE false END AS is_following,
    (SELECT COUNT(*) FROM friendship x
       JOIN friendship y
         ON (CASE WHEN x.account_low_id = :me THEN x.account_high_id
                  ELSE x.account_low_id END)
          = (CASE WHEN y.account_low_id = a.id THEN y.account_high_id
                  ELSE y.account_low_id END)
      WHERE (x.account_low_id = :me OR x.account_high_id = :me)
        AND (y.account_low_id = a.id OR y.account_high_id = a.id)
    ) AS mutuals
"""

PERSON_JOINS = """
FROM account a
LEFT JOIN profile p ON p.account_id = a.id
LEFT JOIN friendship fr
       ON fr.account_low_id = LEAST(a.id, :me)
      AND fr.account_high_id = GREATEST(a.id, :me)
LEFT JOIN friend_request ri
       ON ri.sender_id = a.id AND ri.receiver_id = :me AND ri.status = 'pending'
LEFT JOIN friend_request ro
       ON ro.sender_id = :me AND ro.receiver_id = a.id AND ro.status = 'pending'
LEFT JOIN follow fo
       ON fo.follower_id = :me AND fo.followee_id = a.id
WHERE a.status = 'active' AND a.id <> :me
"""


def people_sql(condition: str, order_by: str, limit: int) -> str:
    return (
        f"SELECT {PERSON_COLUMNS} {PERSON_JOINS} AND ({condition}) "
        f"ORDER BY {order_by} LIMIT {int(limit)}"
    )


def _status_label(is_online: bool, last_seen) -> str:
    if is_online:
        return "Active now"
    seen = relative_time(last_seen)
    return f"Active {seen}" if seen else "Offline"


def _to_card(row) -> PersonCard:
    avatar_url, avatar_remote = avatar_source(row[3], row[1])
    return {
        "id": int(row[0]),
        "display_name": str(row[2]) or str(row[1]),
        "username": str(row[1]),
        "avatar_url": avatar_url,
        "avatar_remote": avatar_remote,
        "is_online": bool(row[4]),
        "status_label": _status_label(bool(row[4]), row[5]),
        "relation": str(row[7]),
        "is_following": bool(row[8]),
        "mutuals": int(row[9] or 0),
        "bio": str(row[6]),
    }


class FriendsState(rx.State):
    tab: str = "friends"
    query: str = ""

    loading: bool = True
    searching: bool = False

    friends: list[PersonCard] = []
    incoming: list[PersonCard] = []
    outgoing: list[PersonCard] = []
    suggestions: list[PersonCard] = []
    results: list[PersonCard] = []

    friend_count: int = 0
    incoming_count: int = 0
    outgoing_count: int = 0
    following_count: int = 0

    profile_open: bool = False
    profile: ProfileDetail = EMPTY_PROFILE

    notice: str = ""

    async def _me(self) -> int:
        auth = await self.get_state(AuthState)
        return auth.account_id

    @rx.event
    def set_tab(self, value: str):
        self.tab = value
        self.notice = ""

    @rx.event
    async def load_all(self):
        me = await self._me()
        if not me:
            self.loading = False
            return
        async with rx.asession() as asession:
            friend_rows = (
                await asession.execute(
                    text(
                        people_sql(
                            "fr.id IS NOT NULL",
                            "a.is_online DESC, LOWER(COALESCE(p.display_name, a.username))",
                            60,
                        )
                    ),
                    {"me": me},
                )
            ).all()
            incoming_rows = (
                await asession.execute(
                    text(
                        people_sql(
                            "ri.id IS NOT NULL", "ri.created_at DESC", 40
                        )
                    ),
                    {"me": me},
                )
            ).all()
            outgoing_rows = (
                await asession.execute(
                    text(
                        people_sql(
                            "ro.id IS NOT NULL", "ro.created_at DESC", 40
                        )
                    ),
                    {"me": me},
                )
            ).all()
            suggestion_rows = (
                await asession.execute(
                    text(
                        people_sql(
                            "fr.id IS NULL AND ri.id IS NULL AND ro.id IS NULL",
                            "mutuals DESC, a.is_online DESC, a.created_at DESC",
                            18,
                        )
                    ),
                    {"me": me},
                )
            ).all()
            counts = (
                await asession.execute(
                    text(
                        """
                        SELECT
                          (SELECT COUNT(*) FROM friendship
                            WHERE account_low_id = :me OR account_high_id = :me),
                          (SELECT COUNT(*) FROM friend_request
                            WHERE receiver_id = :me AND status = 'pending'),
                          (SELECT COUNT(*) FROM friend_request
                            WHERE sender_id = :me AND status = 'pending'),
                          (SELECT COUNT(*) FROM follow WHERE follower_id = :me)
                        """
                    ),
                    {"me": me},
                )
            ).first()
        self.friends = [_to_card(r) for r in friend_rows]
        self.incoming = [_to_card(r) for r in incoming_rows]
        self.outgoing = [_to_card(r) for r in outgoing_rows]
        self.suggestions = [_to_card(r) for r in suggestion_rows]
        if counts is not None:
            self.friend_count = int(counts[0] or 0)
            self.incoming_count = int(counts[1] or 0)
            self.outgoing_count = int(counts[2] or 0)
            self.following_count = int(counts[3] or 0)
        self.loading = False
        if self.query.strip():
            yield FriendsState.search_people(self.query)

    @rx.event
    async def search_people(self, value: str):
        self.query = value
        term = value.strip().lower()
        if len(term) < 2:
            self.results = []
            self.searching = False
            return
        self.searching = True
        self.tab = "search"
        yield
        me = await self._me()
        if not me:
            self.searching = False
            return
        async with rx.asession() as asession:
            rows = (
                await asession.execute(
                    text(
                        people_sql(
                            "LOWER(a.username) LIKE :pattern"
                            " OR LOWER(COALESCE(p.display_name, '')) LIKE :pattern",
                            "a.is_online DESC, LOWER(a.username)",
                            30,
                        )
                    ),
                    {"me": me, "pattern": f"%{term}%"},
                )
            ).all()
        self.results = [_to_card(r) for r in rows]
        self.searching = False

    @rx.event
    def clear_search(self):
        self.query = ""
        self.results = []
        self.searching = False
        self.tab = "friends"

    # ------------------------------------------------------------------
    # Relationship actions (transactional)
    # ------------------------------------------------------------------

    @rx.event
    async def send_request(self, other_id: int):
        me = await self._me()
        if not me or other_id == me or other_id <= 0:
            self.notice = "You cannot send a request to yourself."
            return
        async with rx.asession() as asession:
            existing = (
                await asession.execute(
                    text(
                        """
                        SELECT 1 FROM friendship
                        WHERE account_low_id = LEAST(:me, :other)
                          AND account_high_id = GREATEST(:me, :other)
                        """
                    ),
                    {"me": me, "other": other_id},
                )
            ).first()
            if existing is not None:
                self.notice = "You are already friends."
                return
            reverse = (
                await asession.execute(
                    text(
                        """
                        SELECT id FROM friend_request
                        WHERE sender_id = :other AND receiver_id = :me
                          AND status = 'pending'
                        """
                    ),
                    {"me": me, "other": other_id},
                )
            ).first()
            if reverse is not None:
                await asession.rollback()
                yield FriendsState.accept_request(other_id)
                return
            await asession.execute(
                text(
                    """
                    INSERT INTO friend_request
                        (sender_id, receiver_id, status, message,
                         created_at, updated_at)
                    VALUES (:me, :other, 'pending', '', NOW(), NOW())
                    ON CONFLICT (sender_id, receiver_id)
                    DO UPDATE SET status = 'pending', responded_at = NULL,
                                  updated_at = NOW()
                    """
                ),
                {"me": me, "other": other_id},
            )
            await asession.commit()
        self.notice = "Friend request sent."
        yield FriendsState.load_all
        yield FriendsState.refresh_profile

    @rx.event
    async def accept_request(self, other_id: int):
        me = await self._me()
        if not me or other_id == me:
            return
        async with rx.asession() as asession:
            await asession.execute(
                text(
                    """
                    UPDATE friend_request
                    SET status = 'accepted', responded_at = NOW(),
                        updated_at = NOW()
                    WHERE sender_id = :other AND receiver_id = :me
                      AND status = 'pending'
                    """
                ),
                {"me": me, "other": other_id},
            )
            await asession.execute(
                text(
                    """
                    INSERT INTO friendship
                        (account_low_id, account_high_id, is_favorite, created_at)
                    VALUES (LEAST(:me, :other), GREATEST(:me, :other), false, NOW())
                    ON CONFLICT (account_low_id, account_high_id) DO NOTHING
                    """
                ),
                {"me": me, "other": other_id},
            )
            await asession.commit()
        self.notice = "You are now friends."
        yield FriendsState.load_all
        yield FriendsState.refresh_profile

    @rx.event
    async def decline_request(self, other_id: int):
        me = await self._me()
        if not me:
            return
        async with rx.asession() as asession:
            await asession.execute(
                text(
                    """
                    UPDATE friend_request
                    SET status = 'declined', responded_at = NOW(),
                        updated_at = NOW()
                    WHERE sender_id = :other AND receiver_id = :me
                      AND status = 'pending'
                    """
                ),
                {"me": me, "other": other_id},
            )
            await asession.commit()
        self.notice = "Request declined."
        yield FriendsState.load_all
        yield FriendsState.refresh_profile

    @rx.event
    async def cancel_request(self, other_id: int):
        me = await self._me()
        if not me:
            return
        async with rx.asession() as asession:
            await asession.execute(
                text(
                    """
                    UPDATE friend_request
                    SET status = 'cancelled', responded_at = NOW(),
                        updated_at = NOW()
                    WHERE sender_id = :me AND receiver_id = :other
                      AND status = 'pending'
                    """
                ),
                {"me": me, "other": other_id},
            )
            await asession.commit()
        self.notice = "Request cancelled."
        yield FriendsState.load_all
        yield FriendsState.refresh_profile

    @rx.event
    async def unfriend(self, other_id: int):
        me = await self._me()
        if not me:
            return
        async with rx.asession() as asession:
            await asession.execute(
                text(
                    """
                    DELETE FROM friendship
                    WHERE account_low_id = LEAST(:me, :other)
                      AND account_high_id = GREATEST(:me, :other)
                    """
                ),
                {"me": me, "other": other_id},
            )
            await asession.execute(
                text(
                    """
                    UPDATE friend_request
                    SET status = 'cancelled', responded_at = NOW(),
                        updated_at = NOW()
                    WHERE (sender_id = :me AND receiver_id = :other)
                       OR (sender_id = :other AND receiver_id = :me)
                    """
                ),
                {"me": me, "other": other_id},
            )
            await asession.commit()
        self.notice = "Friend removed."
        yield FriendsState.load_all
        yield FriendsState.refresh_profile

    @rx.event
    async def follow(self, other_id: int):
        me = await self._me()
        if not me or other_id == me:
            self.notice = "You cannot follow yourself."
            return
        async with rx.asession() as asession:
            await asession.execute(
                text(
                    """
                    INSERT INTO follow
                        (follower_id, followee_id, notifications_enabled, created_at)
                    VALUES (:me, :other, true, NOW())
                    ON CONFLICT (follower_id, followee_id) DO NOTHING
                    """
                ),
                {"me": me, "other": other_id},
            )
            await asession.commit()
        yield FriendsState.load_all
        yield FriendsState.refresh_profile

    @rx.event
    async def unfollow(self, other_id: int):
        me = await self._me()
        if not me:
            return
        async with rx.asession() as asession:
            await asession.execute(
                text(
                    """
                    DELETE FROM follow
                    WHERE follower_id = :me AND followee_id = :other
                    """
                ),
                {"me": me, "other": other_id},
            )
            await asession.commit()
        yield FriendsState.load_all
        yield FriendsState.refresh_profile

    # ------------------------------------------------------------------
    # Compact profile drawer
    # ------------------------------------------------------------------

    @rx.event
    async def open_profile(self, other_id: int):
        me = await self._me()
        if not me or other_id == me:
            return
        self.profile_open = True
        await self._load_profile(me, other_id)

    @rx.event
    async def refresh_profile(self):
        if not self.profile_open or self.profile["id"] <= 0:
            return
        me = await self._me()
        if me:
            await self._load_profile(me, int(self.profile["id"]))

    async def _load_profile(self, me: int, other_id: int) -> None:
        async with rx.asession() as asession:
            row = (
                await asession.execute(
                    text(people_sql("a.id = :other", "a.id", 1)),
                    {"me": me, "other": other_id},
                )
            ).first()
            if row is None:
                self.profile = EMPTY_PROFILE
                self.profile_open = False
                return
            extra = (
                await asession.execute(
                    text(
                        """
                        SELECT
                          COALESCE((SELECT location FROM profile
                                     WHERE account_id = :other), ''),
                          (SELECT COUNT(*) FROM friendship
                            WHERE account_low_id = :other OR account_high_id = :other),
                          (SELECT COUNT(*) FROM follow WHERE followee_id = :other),
                          (SELECT COUNT(*) FROM follow WHERE follower_id = :other),
                          (SELECT COUNT(*) FROM post
                            WHERE author_id = :other AND is_deleted = false)
                        """
                    ),
                    {"other": other_id},
                )
            ).first()
        card = _to_card(row)
        self.profile = {
            **card,
            "location": str(extra[0]) if extra else "",
            "friend_count": int(extra[1] or 0) if extra else 0,
            "follower_count": int(extra[2] or 0) if extra else 0,
            "following_count": int(extra[3] or 0) if extra else 0,
            "post_count": int(extra[4] or 0) if extra else 0,
        }

    @rx.event
    def close_profile(self):
        self.profile_open = False

    @rx.event
    def message_person(self, other_id: int):
        self.profile_open = False
        return rx.redirect(f"/messages?to={other_id}")
