"""Global search suggestions, activity notifications and contacts rail."""

from __future__ import annotations

from typing import TypedDict

import reflex as rx
from sqlalchemy import text

from app.media import avatar_source, relative_time
from app.states.auth_state import AuthState


class PersonRow(TypedDict):
    id: int
    display_name: str
    username: str
    avatar_url: str
    avatar_remote: bool
    is_online: bool
    subtitle: str


class SuggestionRow(TypedDict):
    kind: str
    label: str
    detail: str
    avatar_url: str
    avatar_remote: bool


class NotificationRow(TypedDict):
    id: str
    kind: str
    icon: str
    actor: str
    text: str
    time_label: str
    avatar_url: str
    avatar_remote: bool


NOTIFICATIONS_SQL = """
SELECT 'reaction' AS kind, r.created_at AS at, a.username,
       COALESCE(p.display_name, ''), COALESCE(p.avatar_key, ''),
       r.kind AS detail, r.id AS ref
FROM post_reaction r
JOIN post po ON po.id = r.post_id
JOIN account a ON a.id = r.account_id
LEFT JOIN profile p ON p.account_id = a.id
WHERE po.author_id = :me AND r.account_id <> :me
UNION ALL
SELECT 'comment', c.created_at, a.username, COALESCE(p.display_name, ''),
       COALESCE(p.avatar_key, ''), c.body, c.id
FROM comment c
JOIN post po ON po.id = c.post_id
JOIN account a ON a.id = c.author_id
LEFT JOIN profile p ON p.account_id = a.id
WHERE po.author_id = :me AND c.author_id <> :me AND c.is_deleted = false
UNION ALL
SELECT 'follow', f.created_at, a.username, COALESCE(p.display_name, ''),
       COALESCE(p.avatar_key, ''), '', f.id
FROM follow f
JOIN account a ON a.id = f.follower_id
LEFT JOIN profile p ON p.account_id = a.id
WHERE f.followee_id = :me
UNION ALL
SELECT 'story', sr.created_at, a.username, COALESCE(p.display_name, ''),
       COALESCE(p.avatar_key, ''), sr.kind, sr.id
FROM story_reaction sr
JOIN story s ON s.id = sr.story_id
JOIN account a ON a.id = sr.account_id
LEFT JOIN profile p ON p.account_id = a.id
WHERE s.author_id = :me AND sr.account_id <> :me
ORDER BY at DESC
LIMIT 12
"""


class SocialState(rx.State):
    contacts: list[PersonRow] = []
    notifications: list[NotificationRow] = []
    unread_messages: int = 0

    query: str = ""
    suggestions: list[SuggestionRow] = []
    search_open: bool = False
    notifications_open: bool = False
    mobile_menu_open: bool = False

    @rx.var
    def notification_count(self) -> int:
        return len(self.notifications)

    async def _me(self) -> int:
        auth = await self.get_state(AuthState)
        return auth.account_id

    @rx.event
    async def load_side_data(self):
        me = await self._me()
        if not me:
            return
        async with rx.asession() as asession:
            contact_rows = (
                await asession.execute(
                    text(
                        """
                        SELECT a.id, a.username, COALESCE(p.display_name, ''),
                               COALESCE(p.avatar_key, ''), a.is_online,
                               a.last_seen_at
                        FROM friendship f
                        JOIN account a
                          ON a.id = CASE WHEN f.account_low_id = :me
                                         THEN f.account_high_id
                                         ELSE f.account_low_id END
                        LEFT JOIN profile p ON p.account_id = a.id
                        WHERE (f.account_low_id = :me OR f.account_high_id = :me)
                          AND a.status = 'active'
                        ORDER BY a.is_online DESC, a.last_seen_at DESC NULLS LAST
                        LIMIT 12
                        """
                    ),
                    {"me": me},
                )
            ).all()
            notification_rows = (
                await asession.execute(text(NOTIFICATIONS_SQL), {"me": me})
            ).all()
            unread = await asession.scalar(
                text(
                    """
                    SELECT COALESCE(SUM(unread_count), 0)
                    FROM conversation_participant
                    WHERE account_id = :me
                    """
                ),
                {"me": me},
            )
        contacts: list[PersonRow] = []
        for row in contact_rows:
            avatar_url, avatar_remote = avatar_source(row[3], row[1])
            contacts.append(
                {
                    "id": int(row[0]),
                    "display_name": str(row[2]) or str(row[1]),
                    "username": str(row[1]),
                    "avatar_url": avatar_url,
                    "avatar_remote": avatar_remote,
                    "is_online": bool(row[4]),
                    "subtitle": (
                        "Active now"
                        if bool(row[4])
                        else relative_time(row[5]) or "Offline"
                    ),
                }
            )
        notifications: list[NotificationRow] = []
        for row in notification_rows:
            kind = str(row[0])
            actor = str(row[3]) or str(row[2])
            avatar_url, avatar_remote = avatar_source(row[4], row[2])
            detail = str(row[5])
            if kind == "reaction":
                message = f"reacted {detail} to your post"
                icon = "heart"
            elif kind == "comment":
                snippet = detail[:60]
                message = f'commented: "{snippet}"'
                icon = "message-circle"
            elif kind == "story":
                message = f"reacted {detail} to your story"
                icon = "circle-play"
            else:
                message = "started following you"
                icon = "user-plus"
            notifications.append(
                {
                    "id": f"{kind}-{row[6]}",
                    "kind": kind,
                    "icon": icon,
                    "actor": actor,
                    "text": message,
                    "time_label": relative_time(row[1]),
                    "avatar_url": avatar_url,
                    "avatar_remote": avatar_remote,
                }
            )
        self.contacts = contacts
        self.notifications = notifications
        self.unread_messages = int(unread or 0)

    @rx.event
    async def search(self, value: str):
        self.query = value
        self.search_open = True
        term = value.strip().lower()
        if len(term) < 2:
            self.suggestions = []
            return
        me = await self._me()
        pattern = f"%{term}%"
        async with rx.asession() as asession:
            people = (
                await asession.execute(
                    text(
                        """
                        SELECT a.username, COALESCE(p.display_name, ''),
                               COALESCE(p.avatar_key, '')
                        FROM account a
                        LEFT JOIN profile p ON p.account_id = a.id
                        WHERE a.status = 'active'
                          AND (LOWER(a.username) LIKE :pattern
                               OR LOWER(COALESCE(p.display_name, '')) LIKE :pattern)
                        ORDER BY a.username
                        LIMIT 5
                        """
                    ),
                    {"pattern": pattern},
                )
            ).all()
            posts = (
                await asession.execute(
                    text(
                        """
                        SELECT po.body, a.username
                        FROM post po
                        JOIN account a ON a.id = po.author_id
                        WHERE po.is_deleted = false
                          AND LOWER(po.body) LIKE :pattern
                          AND (po.privacy = 'public' OR po.author_id = :me)
                        ORDER BY po.created_at DESC
                        LIMIT 4
                        """
                    ),
                    {"pattern": pattern, "me": me},
                )
            ).all()
        suggestions: list[SuggestionRow] = []
        for row in people:
            avatar_url, avatar_remote = avatar_source(row[2], row[0])
            suggestions.append(
                {
                    "kind": "person",
                    "label": str(row[1]) or str(row[0]),
                    "detail": f"@{row[0]}",
                    "avatar_url": avatar_url,
                    "avatar_remote": avatar_remote,
                }
            )
        for row in posts:
            suggestions.append(
                {
                    "kind": "post",
                    "label": str(row[0])[:64],
                    "detail": f"post by @{row[1]}",
                    "avatar_url": "",
                    "avatar_remote": False,
                }
            )
        self.suggestions = suggestions

    @rx.event
    def close_search(self):
        self.search_open = False

    @rx.event
    def toggle_notifications(self):
        self.notifications_open = not self.notifications_open

    @rx.event
    def toggle_mobile_menu(self):
        self.mobile_menu_open = not self.mobile_menu_open
