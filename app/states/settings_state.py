"""Persisted preferences: language, appearance, privacy and notifications."""

from __future__ import annotations

import reflex as rx
from sqlalchemy import text

from app.games_catalog import LANGUAGES
from app.states.auth_state import AuthState


class SettingsState(rx.State):
    loading: bool = True
    error: str = ""
    saved: bool = False
    language: str = "fr"
    theme: str = "dark"
    profile_visibility: str = "public"
    show_online_status: bool = True
    allow_friend_requests: bool = True
    allow_messages_from_strangers: bool = False
    notify_reactions: bool = True
    notify_comments: bool = True
    notify_messages: bool = True
    notify_friend_requests: bool = True
    notify_game_invites: bool = True
    languages: list[dict[str, str]] = LANGUAGES

    @rx.event
    async def load_settings(self):
        auth = await self.get_state(AuthState)
        if not auth.account_id:
            return
        self.loading = True
        self.error = ""
        async with rx.asession() as asession:
            row = (
                await asession.execute(
                    text(
                        """
                        SELECT language, theme, profile_visibility,
                               show_online_status, allow_friend_requests,
                               allow_messages_from_strangers,
                               notify_reactions, notify_comments,
                               notify_messages, notify_friend_requests,
                               notify_game_invites
                        FROM preference WHERE account_id = :me
                        """
                    ),
                    {"me": auth.account_id},
                )
            ).first()
            if row is None:
                await asession.execute(
                    text(
                        """
                        INSERT INTO preference (account_id, language, theme,
                            profile_visibility, created_at, updated_at)
                        VALUES (:me, 'fr', 'dark', 'public', NOW(), NOW())
                        """
                    ),
                    {"me": auth.account_id},
                )
                await asession.commit()
                self.loading = False
                return
        self.language = str(row[0])
        self.theme = str(row[1])
        self.profile_visibility = str(row[2])
        self.show_online_status = bool(row[3])
        self.allow_friend_requests = bool(row[4])
        self.allow_messages_from_strangers = bool(row[5])
        self.notify_reactions = bool(row[6])
        self.notify_comments = bool(row[7])
        self.notify_messages = bool(row[8])
        self.notify_friend_requests = bool(row[9])
        self.notify_game_invites = bool(row[10])
        self.loading = False

    async def _persist(self):
        auth = await self.get_state(AuthState)
        if not auth.account_id:
            return
        async with rx.asession() as asession:
            await asession.execute(
                text(
                    """
                    UPDATE preference SET language = :language, theme = :theme,
                        profile_visibility = :visibility,
                        show_online_status = :online,
                        allow_friend_requests = :friends,
                        allow_messages_from_strangers = :strangers,
                        notify_reactions = :reactions,
                        notify_comments = :comments,
                        notify_messages = :messages,
                        notify_friend_requests = :requests,
                        notify_game_invites = :invites,
                        updated_at = NOW()
                    WHERE account_id = :me
                    """
                ),
                {
                    "language": self.language,
                    "theme": self.theme,
                    "visibility": self.profile_visibility,
                    "online": self.show_online_status,
                    "friends": self.allow_friend_requests,
                    "strangers": self.allow_messages_from_strangers,
                    "reactions": self.notify_reactions,
                    "comments": self.notify_comments,
                    "messages": self.notify_messages,
                    "requests": self.notify_friend_requests,
                    "invites": self.notify_game_invites,
                    "me": auth.account_id,
                },
            )
            await asession.commit()
        self.saved = True

    @rx.event
    async def set_language(self, value: str):
        self.language = value
        await self._persist()
        return rx.toast("Langue enregistree.")

    @rx.event
    async def set_theme(self, value: str):
        self.theme = value
        await self._persist()
        return rx.toast("Apparence enregistree.")

    @rx.event
    async def set_visibility(self, value: str):
        self.profile_visibility = value
        await self._persist()

    @rx.event
    async def toggle_flag(self, field: str):
        current = bool(getattr(self, field, False))
        setattr(self, field, not current)
        await self._persist()
