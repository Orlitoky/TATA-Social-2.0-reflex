"""Private conversations: deterministic threads, receipts and typing presence."""

from __future__ import annotations

import datetime as dt
from typing import TypedDict

import reflex as rx
from sqlalchemy import text

from app.media import avatar_source, relative_time
from app.states.auth_state import AuthState
from app.states.social_state import SocialState

PAGE_SIZE = 25
TYPING_WINDOW_SECONDS = 8


class AvatarBit(TypedDict):
    url: str
    remote: bool


class ConversationRow(TypedDict):
    id: int
    is_group: bool
    other_id: int
    display_name: str
    username: str
    avatar_url: str
    avatar_remote: bool
    is_online: bool
    member_count: int
    avatars: list[AvatarBit]
    summary: str
    preview: str
    time_label: str
    unread: int


class MemberRow(TypedDict):
    id: int
    display_name: str
    username: str
    avatar_url: str
    avatar_remote: bool
    is_online: bool
    role: str
    presence: str
    is_me: bool


class FriendPick(TypedDict):
    id: int
    display_name: str
    username: str
    avatar_url: str
    avatar_remote: bool
    is_online: bool


class ThreadMessage(TypedDict):
    id: int
    body: str
    mine: bool
    time_label: str
    date_label: str
    show_date: bool
    receipt: str
    sender_id: int
    sender_name: str
    sender_avatar: str
    sender_avatar_remote: bool
    show_sender: bool


def _date_label(moment: dt.datetime) -> str:
    if moment.tzinfo is None:
        moment = moment.replace(tzinfo=dt.UTC)
    today = dt.datetime.now(dt.UTC).date()
    day = moment.date()
    if day == today:
        return "Today"
    if (today - day).days == 1:
        return "Yesterday"
    return moment.strftime("%b %d, %Y")


def _clock(moment: dt.datetime) -> str:
    if moment.tzinfo is None:
        moment = moment.replace(tzinfo=dt.UTC)
    return moment.strftime("%H:%M")


def _typing_fresh(flag: object, stamp: dt.datetime | None) -> bool:
    if not bool(flag) or stamp is None:
        return False
    if stamp.tzinfo is None:
        stamp = stamp.replace(tzinfo=dt.UTC)
    age = (dt.datetime.now(dt.UTC) - stamp).total_seconds()
    return age <= TYPING_WINDOW_SECONDS


_FRIENDS_SQL = """
    SELECT a.id, a.username, COALESCE(p.display_name, ''),
           COALESCE(p.avatar_key, ''), a.is_online
    FROM friendship f
    JOIN account a
      ON a.id = CASE WHEN f.account_low_id = :me
                     THEN f.account_high_id ELSE f.account_low_id END
    LEFT JOIN profile p ON p.account_id = a.id
    WHERE (f.account_low_id = :me OR f.account_high_id = :me)
      AND a.status = 'active'
      AND (:term = ''
           OR LOWER(a.username) LIKE :pattern
           OR LOWER(COALESCE(p.display_name, '')) LIKE :pattern)
    ORDER BY LOWER(COALESCE(NULLIF(p.display_name, ''), a.username))
    LIMIT 100
"""

_LIST_SQL = """
    SELECT c.id, c.is_group, COALESCE(c.title, ''),
           COALESCE(c.last_message_preview, ''), c.last_message_at,
           COALESCE(cp.unread_count, 0)
    FROM conversation_participant cp
    JOIN conversation c ON c.id = cp.conversation_id
    WHERE cp.account_id = :me
      AND cp.left_at IS NULL
      AND (:term = ''
           OR LOWER(COALESCE(c.title, '')) LIKE :pattern
           OR LOWER(COALESCE(c.last_message_preview, '')) LIKE :pattern
           OR EXISTS (
              SELECT 1 FROM conversation_participant op
              JOIN account a ON a.id = op.account_id
              LEFT JOIN profile p ON p.account_id = a.id
              WHERE op.conversation_id = c.id
                AND op.account_id <> :me
                AND op.left_at IS NULL
                AND a.status = 'active'
                AND (LOWER(a.username) LIKE :pattern
                     OR LOWER(COALESCE(p.display_name, '')) LIKE :pattern)))
      AND EXISTS (
          SELECT 1 FROM conversation_participant op2
          JOIN account a2 ON a2.id = op2.account_id
          WHERE op2.conversation_id = c.id
            AND op2.account_id <> :me
            AND op2.left_at IS NULL
            AND a2.status = 'active')
    ORDER BY c.last_message_at DESC NULLS LAST, c.id DESC
    LIMIT 80
"""

_LIST_MEMBERS_SQL = """
    SELECT cp.conversation_id, a.id, a.username,
           COALESCE(p.display_name, ''), COALESCE(p.avatar_key, ''),
           a.is_online, cp.is_typing, cp.typing_updated_at
    FROM conversation_participant cp
    JOIN account a ON a.id = cp.account_id
    LEFT JOIN profile p ON p.account_id = a.id
    WHERE cp.conversation_id = ANY(:ids)
      AND cp.account_id <> :me
      AND cp.left_at IS NULL
      AND a.status = 'active'
    ORDER BY cp.conversation_id, cp.joined_at, a.id
"""

_THREAD_SQL = """
    SELECT m.id, m.sender_id, m.body, m.created_at,
           a.username, COALESCE(p.display_name, ''),
           COALESCE(p.avatar_key, ''),
           (SELECT COUNT(*) FROM conversation_participant op
            WHERE op.conversation_id = m.conversation_id
              AND op.left_at IS NULL
              AND op.account_id <> m.sender_id) AS others,
           (SELECT COUNT(*) FROM message_receipt r
            JOIN conversation_participant op
              ON op.conversation_id = m.conversation_id
             AND op.account_id = r.account_id
             AND op.left_at IS NULL
            WHERE r.message_id = m.id
              AND r.account_id <> m.sender_id
              AND r.read_at IS NOT NULL) AS read_count,
           (SELECT COUNT(*) FROM message_receipt r
            JOIN conversation_participant op
              ON op.conversation_id = m.conversation_id
             AND op.account_id = r.account_id
             AND op.left_at IS NULL
            WHERE r.message_id = m.id
              AND r.account_id <> m.sender_id
              AND r.delivered_at IS NOT NULL) AS delivered_count
    FROM message m
    JOIN account a ON a.id = m.sender_id
    LEFT JOIN profile p ON p.account_id = a.id
    WHERE m.conversation_id = :cid AND m.is_deleted = false
    ORDER BY m.created_at DESC, m.id DESC
    LIMIT :limit
"""


class MessagesState(rx.State):
    conversations: list[ConversationRow] = []
    messages: list[ThreadMessage] = []

    query: str = ""
    loading: bool = True
    thread_loading: bool = False

    active_id: int = 0
    active_is_group: bool = False
    group_title_active: str = ""
    group_member_count: int = 0
    group_members: list[MemberRow] = []
    group_avatars: list[AvatarBit] = []
    group_summary: str = ""
    group_typing: str = ""
    members_open: bool = False

    group_open: bool = False
    group_title: str = ""
    group_query: str = ""
    friend_options: list[FriendPick] = []
    selected_ids: list[int] = []
    selected_people: list[FriendPick] = []
    friends_loading: bool = False
    group_saving: bool = False
    group_error: str = ""

    other_id: int = 0
    other_name: str = ""
    other_username: str = ""
    other_avatar: str = ""
    other_avatar_remote: bool = True
    other_online: bool = False
    other_status: str = ""
    other_typing: bool = False

    limit: int = PAGE_SIZE
    total_messages: int = 0
    total_unread: int = 0

    draft: str = ""
    composer_key: int = 0
    error: str = ""

    @rx.var
    def has_active(self) -> bool:
        return self.active_id > 0

    @rx.var
    def has_more(self) -> bool:
        return self.total_messages > len(self.messages)

    @rx.var
    def selected_count(self) -> int:
        return len(self.selected_ids)

    @rx.var
    def can_create_group(self) -> bool:
        title = self.group_title.strip()
        return 2 <= len(title) <= 120 and len(self.selected_ids) >= 2

    async def _me(self) -> int:
        auth = await self.get_state(AuthState)
        return auth.account_id

    # ------------------------------------------------------------------
    # Loading
    # ------------------------------------------------------------------

    @rx.event
    async def load_page(self):
        target = str(self.router.url.query_parameters.get("to", "")).strip()
        yield MessagesState.load_conversations
        if target.isdigit() and int(target) > 0:
            yield MessagesState.open_with_account(int(target))

    @rx.event
    async def load_conversations(self):
        me = await self._me()
        if not me:
            self.loading = False
            return
        term = self.query.strip().lower()
        async with rx.asession() as asession:
            rows = (
                await asession.execute(
                    text(_LIST_SQL),
                    {"me": me, "term": term, "pattern": f"%{term}%"},
                )
            ).all()
            ids = [int(row[0]) for row in rows]
            member_rows = []
            if ids:
                member_rows = (
                    await asession.execute(
                        text(_LIST_MEMBERS_SQL), {"ids": ids, "me": me}
                    )
                ).all()
            total = await asession.scalar(
                text(
                    """
                    SELECT COALESCE(SUM(unread_count), 0)
                    FROM conversation_participant
                    WHERE account_id = :me AND left_at IS NULL
                    """
                ),
                {"me": me},
            )
        grouped: dict[int, list[tuple]] = {}
        for member in member_rows:
            grouped.setdefault(int(member[0]), []).append(member)
        conversations: list[ConversationRow] = []
        for row in rows:
            cid = int(row[0])
            is_group = bool(row[1])
            others = grouped.get(cid, [])
            typing_names = [
                (str(m[3]) or str(m[2]))
                for m in others
                if _typing_fresh(m[6], m[7])
            ]
            avatars: list[AvatarBit] = []
            for member in others[:3]:
                url, remote = avatar_source(member[4], member[2])
                avatars.append({"url": url, "remote": remote})
            online = sum(1 for m in others if bool(m[5]))
            if is_group:
                display = str(row[2]) or "Group conversation"
                other_id = 0
                username = ""
                avatar_url = avatars[0]["url"] if avatars else ""
                avatar_remote = avatars[0]["remote"] if avatars else True
                is_online = online > 0
                member_count = len(others) + 1
                summary = f"{member_count} members · {online} online"
                if typing_names:
                    summary = f"{typing_names[0]} is typing…"
            else:
                first = others[0] if others else None
                display = (
                    (str(first[3]) or str(first[2])) if first else "Unknown"
                )
                other_id = int(first[1]) if first else 0
                username = str(first[2]) if first else ""
                avatar_url = avatars[0]["url"] if avatars else ""
                avatar_remote = avatars[0]["remote"] if avatars else True
                is_online = bool(first[5]) if first else False
                member_count = 2
                summary = "Active now" if is_online else "Offline"
                if typing_names:
                    summary = "typing…"
            conversations.append(
                {
                    "id": cid,
                    "is_group": is_group,
                    "other_id": other_id,
                    "display_name": display,
                    "username": username,
                    "avatar_url": avatar_url,
                    "avatar_remote": avatar_remote,
                    "is_online": is_online,
                    "member_count": member_count,
                    "avatars": avatars,
                    "summary": summary,
                    "preview": str(row[3]) or "No messages yet",
                    "time_label": relative_time(row[4]),
                    "unread": int(row[5] or 0),
                }
            )
        self.conversations = conversations
        self.total_unread = int(total or 0)
        self.loading = False
        social = await self.get_state(SocialState)
        social.unread_messages = self.total_unread

    @rx.event
    async def search_conversations(self, value: str):
        self.query = value
        yield MessagesState.load_conversations

    @rx.event
    async def open_with_account(self, other_id: int):
        """Create or open the deterministic 1:1 conversation with a person."""
        me = await self._me()
        if not me or other_id == me or other_id <= 0:
            self.error = "You cannot message yourself."
            return
        low, high = min(me, other_id), max(me, other_id)
        direct_key = f"{low}:{high}"
        async with rx.asession() as asession:
            row = (
                await asession.execute(
                    text("SELECT id FROM conversation WHERE direct_key = :key"),
                    {"key": direct_key},
                )
            ).first()
            if row is None:
                created = (
                    await asession.execute(
                        text(
                            """
                            INSERT INTO conversation
                                (is_group, title, created_by_id, direct_key,
                                 last_message_preview, created_at, updated_at)
                            VALUES (false, '', :me, :key, '', NOW(), NOW())
                            ON CONFLICT (direct_key) DO NOTHING
                            RETURNING id
                            """
                        ),
                        {"me": me, "key": direct_key},
                    )
                ).first()
                if created is None:
                    created = (
                        await asession.execute(
                            text(
                                "SELECT id FROM conversation WHERE direct_key = :key"
                            ),
                            {"key": direct_key},
                        )
                    ).first()
                conversation_id = int(created[0])
                await asession.execute(
                    text(
                        """
                        INSERT INTO conversation_participant
                            (conversation_id, account_id, role, joined_at)
                        VALUES (:cid, :me, 'member', NOW()),
                               (:cid, :other, 'member', NOW())
                        ON CONFLICT (conversation_id, account_id) DO NOTHING
                        """
                    ),
                    {"cid": conversation_id, "me": me, "other": other_id},
                )
            else:
                conversation_id = int(row[0])
            await asession.commit()
        self.error = ""
        yield MessagesState.open_conversation(conversation_id)

    # ------------------------------------------------------------------
    # Group creation
    # ------------------------------------------------------------------

    @rx.event
    async def open_group_modal(self):
        self.group_open = True
        self.group_title = ""
        self.group_query = ""
        self.group_error = ""
        self.selected_ids = []
        self.selected_people = []
        self.group_saving = False
        yield MessagesState.load_friend_options

    @rx.event
    def close_group_modal(self):
        self.group_open = False
        self.group_error = ""

    @rx.event
    def change_group_title(self, value: str):
        self.group_title = value
        self.group_error = ""

    @rx.event
    async def search_group_friends(self, value: str):
        self.group_query = value
        yield MessagesState.load_friend_options

    @rx.event
    async def load_friend_options(self):
        me = await self._me()
        if not me:
            self.friend_options = []
            self.friends_loading = False
            return
        self.friends_loading = True
        yield
        term = self.group_query.strip().lower()
        async with rx.asession() as asession:
            rows = (
                await asession.execute(
                    text(_FRIENDS_SQL),
                    {"me": me, "term": term, "pattern": f"%{term}%"},
                )
            ).all()
        options: list[FriendPick] = []
        for row in rows:
            url, remote = avatar_source(row[3], row[1])
            options.append(
                {
                    "id": int(row[0]),
                    "display_name": str(row[2]) or str(row[1]),
                    "username": str(row[1]),
                    "avatar_url": url,
                    "avatar_remote": remote,
                    "is_online": bool(row[4]),
                }
            )
        self.friend_options = options
        self.friends_loading = False

    @rx.event
    def toggle_member(self, account_id: int):
        self.group_error = ""
        if account_id in self.selected_ids:
            self.selected_ids = [
                pid for pid in self.selected_ids if pid != account_id
            ]
            self.selected_people = [
                person
                for person in self.selected_people
                if person["id"] != account_id
            ]
            return
        picked = next(
            (p for p in self.friend_options if p["id"] == account_id), None
        )
        if picked is None:
            return
        self.selected_ids = [*self.selected_ids, account_id]
        self.selected_people = [*self.selected_people, picked]

    @rx.event
    async def create_group(self):
        me = await self._me()
        if not me:
            return
        title = self.group_title.strip()
        if len(title) < 2 or len(title) > 120:
            self.group_error = "Group name must be 2–120 characters."
            return
        members = list(dict.fromkeys(int(pid) for pid in self.selected_ids))
        members = [pid for pid in members if pid != me]
        if len(members) < 2:
            self.group_error = "Pick at least 2 friends for a group."
            return
        self.group_error = ""
        self.group_saving = True
        yield
        async with rx.asession() as asession:
            valid = await asession.scalar(
                text(
                    """
                    SELECT COUNT(DISTINCT a.id)
                    FROM friendship f
                    JOIN account a
                      ON a.id = CASE WHEN f.account_low_id = :me
                                     THEN f.account_high_id
                                     ELSE f.account_low_id END
                    WHERE (f.account_low_id = :me OR f.account_high_id = :me)
                      AND a.status = 'active'
                      AND a.id = ANY(:ids)
                    """
                ),
                {"me": me, "ids": members},
            )
            if int(valid or 0) != len(members):
                self.group_saving = False
                self.group_error = (
                    "Every member must be an active friend of yours."
                )
                return
            created = (
                await asession.execute(
                    text(
                        """
                        INSERT INTO conversation
                            (is_group, title, created_by_id, direct_key,
                             last_message_preview, created_at, updated_at)
                        VALUES (true, :title, :me, NULL, '', NOW(), NOW())
                        RETURNING id
                        """
                    ),
                    {"title": title[:120], "me": me},
                )
            ).first()
            conversation_id = int(created[0])
            await asession.execute(
                text(
                    """
                    INSERT INTO conversation_participant
                        (conversation_id, account_id, role, joined_at)
                    VALUES (:cid, :me, 'admin', NOW())
                    ON CONFLICT (conversation_id, account_id) DO NOTHING
                    """
                ),
                {"cid": conversation_id, "me": me},
            )
            await asession.execute(
                text(
                    """
                    INSERT INTO conversation_participant
                        (conversation_id, account_id, role, joined_at)
                    SELECT :cid, a.id, 'member', NOW()
                    FROM account a
                    WHERE a.id = ANY(:ids)
                    ON CONFLICT (conversation_id, account_id) DO NOTHING
                    """
                ),
                {"cid": conversation_id, "ids": members},
            )
            await asession.commit()
        self.group_saving = False
        self.group_open = False
        self.group_title = ""
        self.group_query = ""
        self.selected_ids = []
        self.selected_people = []
        yield MessagesState.open_conversation(conversation_id)

    @rx.event
    def toggle_members_panel(self):
        self.members_open = not self.members_open

    @rx.event
    async def open_conversation(self, conversation_id: int):
        me = await self._me()
        if not me:
            return
        self.active_id = conversation_id
        self.members_open = False
        self.limit = PAGE_SIZE
        self.thread_loading = True
        self.draft = ""
        self.composer_key += 1
        yield
        async with rx.asession() as asession:
            mine = (
                await asession.execute(
                    text(
                        """
                        SELECT c.is_group, COALESCE(c.title, '')
                        FROM conversation_participant cp
                        JOIN conversation c ON c.id = cp.conversation_id
                        WHERE cp.conversation_id = :cid
                          AND cp.account_id = :me
                          AND cp.left_at IS NULL
                        """
                    ),
                    {"cid": conversation_id, "me": me},
                )
            ).first()
            if mine is None:
                self.thread_loading = False
                self.active_id = 0
                self.error = "You are not a member of that conversation."
                return
            people = (
                await asession.execute(
                    text(
                        """
                        SELECT o.id, o.username, COALESCE(p.display_name, ''),
                               COALESCE(p.avatar_key, ''), o.is_online,
                               o.last_seen_at, op.role, op.is_typing,
                               op.typing_updated_at
                        FROM conversation_participant op
                        JOIN account o ON o.id = op.account_id
                        LEFT JOIN profile p ON p.account_id = o.id
                        WHERE op.conversation_id = :cid
                          AND op.left_at IS NULL
                          AND o.status = 'active'
                        ORDER BY op.joined_at, o.id
                        """
                    ),
                    {"cid": conversation_id},
                )
            ).all()
            # Transactionally mark delivery + read receipts and clear unread.
            await asession.execute(
                text(
                    """
                    INSERT INTO message_receipt
                        (message_id, account_id, delivered_at, read_at)
                    SELECT m.id, :me, NOW(), NOW()
                    FROM message m
                    WHERE m.conversation_id = :cid AND m.sender_id <> :me
                      AND NOT EXISTS (
                        SELECT 1 FROM message_receipt r
                        WHERE r.message_id = m.id AND r.account_id = :me)
                    """
                ),
                {"cid": conversation_id, "me": me},
            )
            await asession.execute(
                text(
                    """
                    UPDATE message_receipt r
                    SET read_at = NOW(),
                        delivered_at = COALESCE(r.delivered_at, NOW())
                    WHERE r.account_id = :me AND r.read_at IS NULL
                      AND r.message_id IN (
                        SELECT id FROM message WHERE conversation_id = :cid)
                    """
                ),
                {"cid": conversation_id, "me": me},
            )
            await asession.execute(
                text(
                    """
                    UPDATE conversation_participant
                    SET unread_count = 0,
                        last_read_at = NOW(),
                        last_read_message_id = (
                          SELECT MAX(id) FROM message
                          WHERE conversation_id = :cid)
                    WHERE conversation_id = :cid AND account_id = :me
                      AND left_at IS NULL
                    """
                ),
                {"cid": conversation_id, "me": me},
            )
            await asession.commit()
        self.active_is_group = bool(mine[0])
        others = [row for row in people if int(row[0]) != me]
        members: list[MemberRow] = []
        avatars: list[AvatarBit] = []
        for row in people:
            url, remote = avatar_source(row[3], row[1])
            seen_label = relative_time(row[5])
            members.append(
                {
                    "id": int(row[0]),
                    "display_name": str(row[2]) or str(row[1]),
                    "username": str(row[1]),
                    "avatar_url": url,
                    "avatar_remote": remote,
                    "is_online": bool(row[4]),
                    "role": str(row[6] or "member"),
                    "presence": (
                        "Active now"
                        if bool(row[4])
                        else (
                            f"Active {seen_label}" if seen_label else "Offline"
                        )
                    ),
                    "is_me": int(row[0]) == me,
                }
            )
        for row in others[:4]:
            url, remote = avatar_source(row[3], row[1])
            avatars.append({"url": url, "remote": remote})
        self.group_members = members
        self.group_avatars = avatars
        self.group_member_count = len(members)
        self.group_title_active = str(mine[1]) or "Group conversation"
        online = sum(1 for row in others if bool(row[4]))
        self.group_summary = f"{len(members)} members · {online} online"
        typing_names = [
            (str(row[2]) or str(row[1]))
            for row in others
            if _typing_fresh(row[7], row[8])
        ]
        if len(typing_names) == 1:
            self.group_typing = f"{typing_names[0]} is typing…"
        elif len(typing_names) > 1:
            self.group_typing = f"{len(typing_names)} people are typing…"
        else:
            self.group_typing = ""
        if others and not self.active_is_group:
            member = others[0]
            avatar_url, avatar_remote = avatar_source(member[3], member[1])
            self.other_id = int(member[0])
            self.other_username = str(member[1])
            self.other_name = str(member[2]) or str(member[1])
            self.other_avatar = avatar_url
            self.other_avatar_remote = avatar_remote
            self.other_online = bool(member[4])
            seen = relative_time(member[5])
            self.other_status = (
                "Active now"
                if bool(member[4])
                else (f"Active {seen}" if seen else "Offline")
            )
        yield MessagesState.load_thread
        yield MessagesState.load_conversations

    @rx.event
    async def load_thread(self):
        me = await self._me()
        if not me or not self.active_id:
            self.thread_loading = False
            return
        async with rx.asession() as asession:
            rows = (
                await asession.execute(
                    text(_THREAD_SQL),
                    {"cid": self.active_id, "limit": self.limit},
                )
            ).all()
            total = await asession.scalar(
                text(
                    """
                    SELECT COUNT(*) FROM message
                    WHERE conversation_id = :cid AND is_deleted = false
                    """
                ),
                {"cid": self.active_id},
            )
            typing_rows = (
                await asession.execute(
                    text(
                        """
                        SELECT a.username, COALESCE(p.display_name, ''),
                               cp.is_typing, cp.typing_updated_at
                        FROM conversation_participant cp
                        JOIN account a ON a.id = cp.account_id
                        LEFT JOIN profile p ON p.account_id = a.id
                        WHERE cp.conversation_id = :cid
                          AND cp.account_id <> :me
                          AND cp.left_at IS NULL
                          AND a.status = 'active'
                        """
                    ),
                    {"cid": self.active_id, "me": me},
                )
            ).all()
        ordered = list(reversed(rows))
        thread: list[ThreadMessage] = []
        previous_day = ""
        previous_sender = 0
        for row in ordered:
            created = row[3]
            day = _date_label(created)
            sender_id = int(row[1])
            mine = sender_id == me
            others = int(row[7] or 0)
            read_count = int(row[8] or 0)
            delivered_count = int(row[9] or 0)
            if others > 0 and read_count >= others:
                receipt = "read"
            elif others > 0 and delivered_count >= others:
                receipt = "delivered"
            else:
                receipt = "sent"
            url, remote = avatar_source(row[6], row[4])
            show_date = day != previous_day
            thread.append(
                {
                    "id": int(row[0]),
                    "body": str(row[2]),
                    "mine": mine,
                    "time_label": _clock(created),
                    "date_label": day,
                    "show_date": show_date,
                    "receipt": receipt if mine else "",
                    "sender_id": sender_id,
                    "sender_name": str(row[5]) or str(row[4]),
                    "sender_avatar": url,
                    "sender_avatar_remote": remote,
                    "show_sender": (
                        self.active_is_group
                        and not mine
                        and (sender_id != previous_sender or show_date)
                    ),
                }
            )
            previous_day = day
            previous_sender = sender_id
        self.messages = thread
        self.total_messages = int(total or 0)
        self.thread_loading = False
        typing_names = [
            (str(row[1]) or str(row[0]))
            for row in typing_rows
            if _typing_fresh(row[2], row[3])
        ]
        self.other_typing = bool(typing_names) and not self.active_is_group
        if not self.active_is_group:
            self.group_typing = ""
        elif len(typing_names) == 1:
            self.group_typing = f"{typing_names[0]} is typing…"
        elif len(typing_names) > 1:
            self.group_typing = f"{len(typing_names)} people are typing…"
        else:
            self.group_typing = ""

    @rx.event
    async def load_older(self):
        self.limit += PAGE_SIZE
        yield MessagesState.load_thread

    @rx.event
    async def poll(self):
        """Modest-interval refresh that simulates realtime presence."""
        me = await self._me()
        if not me:
            return
        if self.active_id:
            async with rx.asession() as asession:
                incoming = await asession.scalar(
                    text(
                        """
                        SELECT COALESCE(unread_count, 0)
                        FROM conversation_participant
                        WHERE conversation_id = :cid AND account_id = :me
                          AND left_at IS NULL
                        """
                    ),
                    {"cid": self.active_id, "me": me},
                )
                if int(incoming or 0) > 0:
                    await asession.execute(
                        text(
                            """
                            INSERT INTO message_receipt
                                (message_id, account_id, delivered_at, read_at)
                            SELECT m.id, :me, NOW(), NOW()
                            FROM message m
                            WHERE m.conversation_id = :cid AND m.sender_id <> :me
                              AND NOT EXISTS (
                                SELECT 1 FROM message_receipt r
                                WHERE r.message_id = m.id AND r.account_id = :me)
                            """
                        ),
                        {"cid": self.active_id, "me": me},
                    )
                    await asession.execute(
                        text(
                            """
                            UPDATE conversation_participant
                            SET unread_count = 0, last_read_at = NOW()
                            WHERE conversation_id = :cid AND account_id = :me
                              AND left_at IS NULL
                            """
                        ),
                        {"cid": self.active_id, "me": me},
                    )
                await asession.commit()
            yield MessagesState.load_thread
        yield MessagesState.load_conversations

    # ------------------------------------------------------------------
    # Composer + typing presence
    # ------------------------------------------------------------------

    @rx.event
    async def change_draft(self, value: str):
        self.draft = value
        me = await self._me()
        if not me or not self.active_id:
            return
        async with rx.asession() as asession:
            await asession.execute(
                text(
                    """
                    UPDATE conversation_participant
                    SET is_typing = :typing, typing_updated_at = NOW()
                    WHERE conversation_id = :cid AND account_id = :me
                      AND left_at IS NULL
                    """
                ),
                {
                    "cid": self.active_id,
                    "me": me,
                    "typing": bool(value.strip()),
                },
            )
            await asession.commit()

    @rx.event
    async def send_message(self):
        body = self.draft.strip()
        me = await self._me()
        if not me or not self.active_id:
            return
        if not body:
            self.error = "Write a message first."
            return
        self.error = ""
        async with rx.asession() as asession:
            allowed = (
                await asession.execute(
                    text(
                        """
                        SELECT 1 FROM conversation_participant
                        WHERE conversation_id = :cid AND account_id = :me
                          AND left_at IS NULL
                        """
                    ),
                    {"cid": self.active_id, "me": me},
                )
            ).first()
            if allowed is None:
                self.error = "You are not a member of this conversation."
                return
            created = (
                await asession.execute(
                    text(
                        """
                        INSERT INTO message
                            (conversation_id, sender_id, kind, body,
                             created_at, updated_at)
                        VALUES (:cid, :me, 'text', :body, NOW(), NOW())
                        RETURNING id
                        """
                    ),
                    {"cid": self.active_id, "me": me, "body": body},
                )
            ).first()
            message_id = int(created[0])
            await asession.execute(
                text(
                    """
                    INSERT INTO message_receipt
                        (message_id, account_id, delivered_at, read_at)
                    VALUES (:mid, :me, NOW(), NOW())
                    ON CONFLICT (message_id, account_id) DO NOTHING
                    """
                ),
                {"mid": message_id, "me": me},
            )
            await asession.execute(
                text(
                    """
                    UPDATE conversation
                    SET last_message_at = NOW(),
                        last_message_preview = :preview,
                        updated_at = NOW()
                    WHERE id = :cid
                    """
                ),
                {"cid": self.active_id, "preview": body[:255]},
            )
            await asession.execute(
                text(
                    """
                    UPDATE conversation_participant
                    SET unread_count = unread_count + 1
                    WHERE conversation_id = :cid AND account_id <> :me
                      AND left_at IS NULL
                    """
                ),
                {"cid": self.active_id, "me": me},
            )
            await asession.execute(
                text(
                    """
                    UPDATE conversation_participant
                    SET is_typing = false, typing_updated_at = NOW(),
                        last_read_message_id = :mid, last_read_at = NOW(),
                        unread_count = 0
                    WHERE conversation_id = :cid AND account_id = :me
                      AND left_at IS NULL
                    """
                ),
                {"cid": self.active_id, "me": me, "mid": message_id},
            )
            await asession.commit()
        self.draft = ""
        self.composer_key += 1
        yield MessagesState.load_thread
        yield MessagesState.load_conversations

    @rx.event
    def back_to_list(self):
        self.active_id = 0
        self.messages = []
        self.other_typing = False
        self.group_typing = ""
        self.members_open = False
        self.active_is_group = False
