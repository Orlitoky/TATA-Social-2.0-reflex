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


class ConversationRow(TypedDict):
    id: int
    other_id: int
    display_name: str
    username: str
    avatar_url: str
    avatar_remote: bool
    is_online: bool
    preview: str
    time_label: str
    unread: int


class ThreadMessage(TypedDict):
    id: int
    body: str
    mine: bool
    time_label: str
    date_label: str
    show_date: bool
    receipt: str


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


class MessagesState(rx.State):
    conversations: list[ConversationRow] = []
    messages: list[ThreadMessage] = []

    query: str = ""
    loading: bool = True
    thread_loading: bool = False

    active_id: int = 0
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
                    text(
                        """
                        SELECT c.id, cp.unread_count,
                               COALESCE(c.last_message_preview, ''),
                               c.last_message_at, o.id, o.username,
                               COALESCE(p.display_name, ''),
                               COALESCE(p.avatar_key, ''), o.is_online
                        FROM conversation_participant cp
                        JOIN conversation c ON c.id = cp.conversation_id
                        JOIN conversation_participant op
                          ON op.conversation_id = c.id AND op.account_id <> :me
                        JOIN account o ON o.id = op.account_id
                        LEFT JOIN profile p ON p.account_id = o.id
                        WHERE cp.account_id = :me
                          AND c.is_group = false
                          AND o.status = 'active'
                          AND (:term = ''
                               OR LOWER(o.username) LIKE :pattern
                               OR LOWER(COALESCE(p.display_name, '')) LIKE :pattern
                               OR LOWER(COALESCE(c.last_message_preview, '')) LIKE :pattern)
                        ORDER BY c.last_message_at DESC NULLS LAST, c.id DESC
                        LIMIT 50
                        """
                    ),
                    {"me": me, "term": term, "pattern": f"%{term}%"},
                )
            ).all()
            total = await asession.scalar(
                text(
                    """
                    SELECT COALESCE(SUM(unread_count), 0)
                    FROM conversation_participant
                    WHERE account_id = :me
                    """
                ),
                {"me": me},
            )
        conversations: list[ConversationRow] = []
        for row in rows:
            avatar_url, avatar_remote = avatar_source(row[7], row[5])
            conversations.append(
                {
                    "id": int(row[0]),
                    "other_id": int(row[4]),
                    "display_name": str(row[6]) or str(row[5]),
                    "username": str(row[5]),
                    "avatar_url": avatar_url,
                    "avatar_remote": avatar_remote,
                    "is_online": bool(row[8]),
                    "preview": str(row[2]) or "No messages yet",
                    "time_label": relative_time(row[3]),
                    "unread": int(row[1] or 0),
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

    @rx.event
    async def open_conversation(self, conversation_id: int):
        me = await self._me()
        if not me:
            return
        self.active_id = conversation_id
        self.limit = PAGE_SIZE
        self.thread_loading = True
        self.draft = ""
        self.composer_key += 1
        yield
        async with rx.asession() as asession:
            member = (
                await asession.execute(
                    text(
                        """
                        SELECT o.id, o.username, COALESCE(p.display_name, ''),
                               COALESCE(p.avatar_key, ''), o.is_online,
                               o.last_seen_at
                        FROM conversation_participant op
                        JOIN account o ON o.id = op.account_id
                        LEFT JOIN profile p ON p.account_id = o.id
                        WHERE op.conversation_id = :cid AND op.account_id <> :me
                        LIMIT 1
                        """
                    ),
                    {"cid": conversation_id, "me": me},
                )
            ).first()
            mine = (
                await asession.execute(
                    text(
                        """
                        SELECT 1 FROM conversation_participant
                        WHERE conversation_id = :cid AND account_id = :me
                        """
                    ),
                    {"cid": conversation_id, "me": me},
                )
            ).first()
            if member is None or mine is None:
                self.thread_loading = False
                self.active_id = 0
                return
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
                    """
                ),
                {"cid": conversation_id, "me": me},
            )
            await asession.commit()
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
                    text(
                        """
                        SELECT m.id, m.sender_id, m.body, m.created_at,
                               r.delivered_at, r.read_at
                        FROM message m
                        LEFT JOIN message_receipt r
                               ON r.message_id = m.id AND r.account_id = :other
                        WHERE m.conversation_id = :cid AND m.is_deleted = false
                        ORDER BY m.created_at DESC, m.id DESC
                        LIMIT :limit
                        """
                    ),
                    {
                        "cid": self.active_id,
                        "other": self.other_id,
                        "limit": self.limit,
                    },
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
            typing = (
                await asession.execute(
                    text(
                        """
                        SELECT is_typing, typing_updated_at
                        FROM conversation_participant
                        WHERE conversation_id = :cid AND account_id = :other
                        """
                    ),
                    {"cid": self.active_id, "other": self.other_id},
                )
            ).first()
        ordered = list(reversed(rows))
        thread: list[ThreadMessage] = []
        previous_day = ""
        for row in ordered:
            created = row[3]
            day = _date_label(created)
            mine = int(row[1]) == me
            if row[5] is not None:
                receipt = "read"
            elif row[4] is not None:
                receipt = "delivered"
            else:
                receipt = "sent"
            thread.append(
                {
                    "id": int(row[0]),
                    "body": str(row[2]),
                    "mine": mine,
                    "time_label": _clock(created),
                    "date_label": day,
                    "show_date": day != previous_day,
                    "receipt": receipt if mine else "",
                }
            )
            previous_day = day
        self.messages = thread
        self.total_messages = int(total or 0)
        self.thread_loading = False
        active_typing = False
        if typing is not None and bool(typing[0]) and typing[1] is not None:
            stamp = typing[1]
            if stamp.tzinfo is None:
                stamp = stamp.replace(tzinfo=dt.UTC)
            age = (dt.datetime.now(dt.UTC) - stamp).total_seconds()
            active_typing = age <= TYPING_WINDOW_SECONDS
        self.other_typing = active_typing

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
