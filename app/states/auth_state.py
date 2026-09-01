"""Email/password authentication with persistent hashed-token sessions."""

from __future__ import annotations

import datetime as dt
from typing import Any

import reflex as rx
from sqlalchemy import select, text

from app.media import avatar_source
from app.models import Account, CoinLedgerEntry, Preference, Profile, Wallet
from app.security import (
    hash_password,
    hash_token,
    new_session_token,
    normalize_email,
    normalize_username,
    validate_signup,
    verify_password,
)
from app.seed import needs_seed, seed_demo_network

SESSION_DAYS = 30
SIGNUP_BONUS_COINS = 500


class AuthState(rx.State):
    token: str = rx.LocalStorage("", name="tata_session_token")

    account_id: int = 0
    username: str = ""
    display_name: str = ""
    email: str = ""
    avatar_url: str = ""
    avatar_remote: bool = True
    coin_balance: int = 0

    error: str = ""
    processing: bool = False
    checked: bool = False

    delete_error: str = ""
    delete_open: bool = False

    @rx.var
    def is_authenticated(self) -> bool:
        return self.account_id > 0

    @rx.var
    def initials(self) -> str:
        name = self.display_name.strip() or self.username
        return name[:1].upper()

    def _clear_identity(self) -> None:
        self.account_id = 0
        self.username = ""
        self.display_name = ""
        self.email = ""
        self.avatar_url = ""
        self.coin_balance = 0

    async def _load_identity(self, asession, account_id: int) -> None:
        row = (
            await asession.execute(
                text(
                    """
                    SELECT a.username, a.email,
                           COALESCE(p.display_name, ''),
                           COALESCE(p.avatar_key, ''),
                           COALESCE(w.balance_coins, 0)
                    FROM account a
                    LEFT JOIN profile p ON p.account_id = a.id
                    LEFT JOIN wallet w ON w.account_id = a.id
                    WHERE a.id = :id
                    """
                ),
                {"id": account_id},
            )
        ).first()
        if row is None:
            self._clear_identity()
            return
        self.account_id = account_id
        self.username = str(row[0])
        self.email = str(row[1])
        self.display_name = str(row[2]) or str(row[0])
        url, remote = avatar_source(row[3], row[0])
        self.avatar_url = url
        self.avatar_remote = remote
        self.coin_balance = int(row[4])

    @rx.event
    async def check_session(self):
        """Route protection: resolve the hashed session token or go to login."""
        self.error = ""
        token = self.token
        if not token:
            self.checked = True
            self._clear_identity()
            yield rx.redirect("/login")
            return
        async with rx.asession() as asession:
            row = (
                await asession.execute(
                    text(
                        """
                        SELECT s.id, s.account_id
                        FROM auth_session s
                        JOIN account a ON a.id = s.account_id
                        WHERE s.token_hash = :token_hash
                          AND s.revoked_at IS NULL
                          AND (s.expires_at IS NULL OR s.expires_at > NOW())
                          AND a.status = 'active'
                        """
                    ),
                    {"token_hash": hash_token(token)},
                )
            ).first()
            if row is None:
                self.token = ""
                self._clear_identity()
                self.checked = True
                yield rx.redirect("/login")
                return
            await asession.execute(
                text(
                    """
                    UPDATE auth_session
                    SET last_active_at = NOW()
                    WHERE id = :id
                    """
                ),
                {"id": int(row[0])},
            )
            await asession.execute(
                text(
                    """
                    UPDATE account
                    SET is_online = true, last_seen_at = NOW()
                    WHERE id = :id
                    """
                ),
                {"id": int(row[1])},
            )
            await self._load_identity(asession, int(row[1]))
            await asession.commit()
        self.checked = True
        yield AuthState.fanout_load

    @rx.event
    async def guard_session(self):
        """Route protection for secondary pages (no Home data fanout)."""
        self.error = ""
        token = self.token
        if not token:
            self.checked = True
            self._clear_identity()
            return rx.redirect("/login")
        async with rx.asession() as asession:
            row = (
                await asession.execute(
                    text(
                        """
                        SELECT s.id, s.account_id
                        FROM auth_session s
                        JOIN account a ON a.id = s.account_id
                        WHERE s.token_hash = :token_hash
                          AND s.revoked_at IS NULL
                          AND (s.expires_at IS NULL OR s.expires_at > NOW())
                          AND a.status = 'active'
                        """
                    ),
                    {"token_hash": hash_token(token)},
                )
            ).first()
            if row is None:
                self.token = ""
                self._clear_identity()
                self.checked = True
                return rx.redirect("/login")
            await asession.execute(
                text(
                    """
                    UPDATE auth_session SET last_active_at = NOW()
                    WHERE id = :id
                    """
                ),
                {"id": int(row[0])},
            )
            await asession.execute(
                text(
                    """
                    UPDATE account
                    SET is_online = true, last_seen_at = NOW()
                    WHERE id = :id
                    """
                ),
                {"id": int(row[1])},
            )
            await self._load_identity(asession, int(row[1]))
            await asession.commit()
        self.checked = True

    @rx.event
    async def fanout_load(self):
        """Load the Home data sets once the session is confirmed."""
        from app.states.feed_state import FeedState
        from app.states.social_state import SocialState
        from app.states.story_state import StoryState

        yield StoryState.load_stories
        yield FeedState.load_feed
        yield SocialState.load_side_data

    @rx.event
    async def redirect_if_authenticated(self):
        self.error = ""
        if not self.token:
            return
        async with rx.asession() as asession:
            row = (
                await asession.execute(
                    text(
                        """
                        SELECT account_id FROM auth_session
                        WHERE token_hash = :token_hash
                          AND revoked_at IS NULL
                          AND (expires_at IS NULL OR expires_at > NOW())
                        """
                    ),
                    {"token_hash": hash_token(self.token)},
                )
            ).first()
        if row is not None:
            return rx.redirect("/")

    async def _start_session(self, asession, account_id: int) -> None:
        token = new_session_token()
        expires = dt.datetime.now(dt.UTC) + dt.timedelta(days=SESSION_DAYS)
        await asession.execute(
            text(
                """
                INSERT INTO auth_session
                    (account_id, token_hash, user_agent, ip_address,
                     created_at, last_active_at, expires_at)
                VALUES (:account_id, :token_hash, '', '', NOW(), NOW(), :expires)
                """
            ),
            {
                "account_id": account_id,
                "token_hash": hash_token(token),
                "expires": expires,
            },
        )
        self.token = token

    @rx.event
    async def signup(self, form_data: dict[str, Any]):
        email = str(form_data.get("email", ""))
        username = str(form_data.get("username", ""))
        display_name = str(form_data.get("display_name", ""))
        password = str(form_data.get("password", ""))
        confirm = str(form_data.get("confirm_password", ""))

        self.error = validate_signup(
            email, username, password, confirm, display_name
        )
        if self.error:
            return
        self.processing = True
        yield

        email_n = normalize_email(email)
        username_n = normalize_username(username)
        now = dt.datetime.now(dt.UTC)

        async with rx.asession() as asession:
            existing = (
                await asession.execute(
                    text(
                        """
                        SELECT email_normalized, username_normalized
                        FROM account
                        WHERE email_normalized = :email
                           OR username_normalized = :username
                        """
                    ),
                    {"email": email_n, "username": username_n},
                )
            ).first()
            if existing is not None:
                self.processing = False
                self.error = (
                    "That email is already registered."
                    if str(existing[0]) == email_n
                    else "That username is already taken."
                )
                return

            account = Account(
                email=email.strip(),
                email_normalized=email_n,
                username=username.strip(),
                username_normalized=username_n,
                password_hash=hash_password(password),
                password_updated_at=now,
                status="active",
                is_online=True,
                last_seen_at=now,
                last_login_at=now,
                created_at=now,
                updated_at=now,
            )
            asession.add(account)
            await asession.flush()

            asession.add(
                Profile(
                    account_id=account.id,
                    display_name=display_name.strip()[:80],
                    created_at=now,
                    updated_at=now,
                )
            )
            asession.add(
                Preference(
                    account_id=account.id, created_at=now, updated_at=now
                )
            )
            wallet = Wallet(
                account_id=account.id,
                balance_coins=SIGNUP_BONUS_COINS,
                lifetime_earned_coins=SIGNUP_BONUS_COINS,
                created_at=now,
                updated_at=now,
            )
            asession.add(wallet)
            await asession.flush()
            asession.add(
                CoinLedgerEntry(
                    wallet_id=wallet.id,
                    account_id=account.id,
                    amount_coins=SIGNUP_BONUS_COINS,
                    balance_after=SIGNUP_BONUS_COINS,
                    reason="signup_bonus",
                    description="Welcome to TATA - signup bonus",
                    idempotency_key=f"signup:{account.id}",
                    created_at=now,
                )
            )

            if await needs_seed(asession):
                await seed_demo_network(asession, account.id)

            await self._start_session(asession, account.id)
            await self._load_identity(asession, account.id)
            await asession.commit()

        self.processing = False
        self.checked = True
        yield rx.redirect("/")

    @rx.event
    async def login(self, form_data: dict[str, Any]):
        identifier = str(form_data.get("identifier", "")).strip()
        password = str(form_data.get("password", ""))
        self.error = ""
        if not identifier or not password:
            self.error = "Enter your email or username and password."
            return
        self.processing = True
        yield

        async with rx.asession() as asession:
            row = (
                await asession.execute(
                    text(
                        """
                        SELECT id, password_hash, status
                        FROM account
                        WHERE email_normalized = :ident
                           OR username_normalized = :ident
                        """
                    ),
                    {"ident": identifier.lower()},
                )
            ).first()
            if row is None or not verify_password(password, row[1]):
                if row is not None:
                    await asession.execute(
                        text(
                            """
                            UPDATE account
                            SET failed_login_count = failed_login_count + 1
                            WHERE id = :id
                            """
                        ),
                        {"id": int(row[0])},
                    )
                    await asession.commit()
                self.processing = False
                self.error = "Invalid credentials. Please try again."
                return
            if str(row[2]) != "active":
                self.processing = False
                self.error = "This account is not active."
                return

            account_id = int(row[0])
            await asession.execute(
                text(
                    """
                    UPDATE account
                    SET failed_login_count = 0, last_login_at = NOW(),
                        is_online = true, last_seen_at = NOW()
                    WHERE id = :id
                    """
                ),
                {"id": account_id},
            )
            await self._start_session(asession, account_id)
            await self._load_identity(asession, account_id)
            await asession.commit()

        self.processing = False
        self.checked = True
        yield rx.redirect("/")

    @rx.event
    async def logout(self):
        token = self.token
        if token:
            async with rx.asession() as asession:
                await asession.execute(
                    text(
                        """
                        UPDATE auth_session
                        SET revoked_at = NOW()
                        WHERE token_hash = :token_hash
                        """
                    ),
                    {"token_hash": hash_token(token)},
                )
                if self.account_id:
                    await asession.execute(
                        text(
                            """
                            UPDATE account
                            SET is_online = false, last_seen_at = NOW()
                            WHERE id = :id
                            """
                        ),
                        {"id": self.account_id},
                    )
                await asession.commit()
        self.token = ""
        self._clear_identity()
        return rx.redirect("/login")

    @rx.event
    def toggle_delete_dialog(self):
        self.delete_open = not self.delete_open
        self.delete_error = ""

    @rx.event
    async def delete_account(self, form_data: dict[str, Any]):
        """Guarded deletion: password + exact username confirmation."""
        password = str(form_data.get("password", ""))
        confirm_username = str(form_data.get("confirm_username", "")).strip()
        self.delete_error = ""
        if not self.account_id:
            self.delete_error = "You are not signed in."
            return
        if confirm_username.lower() != self.username.lower():
            self.delete_error = "Type your username exactly to confirm."
            return
        async with rx.asession() as asession:
            account = await asession.scalar(
                select(Account).where(Account.id == self.account_id)
            )
            if account is None or not verify_password(
                password, account.password_hash
            ):
                self.delete_error = "Password is incorrect."
                return
            await asession.execute(
                text("DELETE FROM account WHERE id = :id"),
                {"id": self.account_id},
            )
            await asession.commit()
        self.token = ""
        self.delete_open = False
        self._clear_identity()
        return rx.redirect("/signup")
