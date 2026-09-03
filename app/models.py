"""Persistent data model layer for the TATA social & gaming platform.

Pure SQLAlchemy declarative models (managed Reflex database). No UI, no queries.
Passwords are ONLY ever stored as salted hashes. TATA Coins are virtual-only:
there are deliberately no real-money / cash-out / fiat conversion fields.
"""

from __future__ import annotations

import datetime as dt

from sqlalchemy import (
    BigInteger,
    Boolean,
    CheckConstraint,
    DateTime,
    ForeignKey,
    Index,
    Integer,
    String,
    Text,
    UniqueConstraint,
    func,
)
from sqlalchemy.orm import (
    DeclarativeBase,
    Mapped,
    MappedAsDataclass,
    mapped_column,
    relationship,
)


class Base(MappedAsDataclass, DeclarativeBase, kw_only=True):
    pass


class TimestampMixin:
    """created_at / updated_at maintained by the database."""

    created_at: Mapped[dt.datetime] = mapped_column(
        DateTime(timezone=True),
        default=None,
        server_default=func.now(),
        nullable=False,
        index=True,
    )
    updated_at: Mapped[dt.datetime] = mapped_column(
        DateTime(timezone=True),
        default=None,
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )


# ---------------------------------------------------------------------------
# Vocabularies (kept as plain strings + CheckConstraints for migration safety)
# ---------------------------------------------------------------------------

PRIVACY_VALUES = ("public", "friends", "private")
ACCOUNT_STATUS_VALUES = ("active", "suspended", "deactivated", "deleted")
MEDIA_KIND_VALUES = ("image", "video", "audio", "file")
REACTION_VALUES = ("like", "love", "haha", "wow", "sad", "angry", "fire")
REQUEST_STATUS_VALUES = (
    "pending",
    "accepted",
    "declined",
    "cancelled",
    "blocked",
)
MESSAGE_KIND_VALUES = ("text", "image", "video", "audio", "file", "system")
# Existing values preserved; "waiting"/"active" added for authoritative play.
ROOM_STATUS_VALUES = (
    "open",
    "waiting",
    "active",
    "in_progress",
    "finished",
    "closed",
)
GAME_ACTION_KIND_VALUES = (
    "join",
    "leave",
    "ready",
    "start",
    "buy_card",
    "draw",
    "mark",
    "claim_quine",
    "claim_double_quine",
    "claim_full_house",
    "place_tile",
    "draw_tile",
    "pass_turn",
    "roll_dice",
    "move_piece",
    "capture",
    "draw_line",
    "close_box",
    "discard",
    "meld",
    "shoot",
    "pot_ball",
    "foul",
    "timeout",
    "resign",
    "round_end",
    "settle",
    "reaction",
    "system",
)
LEDGER_REASON_VALUES = (
    "signup_bonus",
    "daily_reward",
    "game_win",
    "game_entry",
    "gift_sent",
    "gift_received",
    "achievement",
    "admin_adjustment",
)
THEME_VALUES = ("light", "dark", "system")
# English, French, Arabic, Hindi, Spanish, Portuguese (German retained for
# backwards compatibility) plus Malagasy and Chinese.
LANGUAGE_VALUES = ("en", "es", "fr", "de", "pt", "ar", "hi", "mg", "zh")


# ---------------------------------------------------------------------------
# Accounts, profiles, preferences, sessions
# ---------------------------------------------------------------------------


class Account(Base, TimestampMixin):
    __tablename__ = "account"
    __table_args__ = (
        UniqueConstraint(
            "email_normalized", name="uq_account_email_normalized"
        ),
        UniqueConstraint(
            "username_normalized", name="uq_account_username_normalized"
        ),
        CheckConstraint(
            "status IN " + str(ACCOUNT_STATUS_VALUES), name="ck_account_status"
        ),
        Index("ix_account_status_created", "status", "created_at"),
    )

    id: Mapped[int] = mapped_column(primary_key=True, init=False)
    email: Mapped[str] = mapped_column(String(320), nullable=False)
    email_normalized: Mapped[str] = mapped_column(String(320), nullable=False)
    username: Mapped[str] = mapped_column(String(48), nullable=False)
    username_normalized: Mapped[str] = mapped_column(String(48), nullable=False)

    # Security: only a derived hash is persisted, never a plaintext password.
    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    password_algo: Mapped[str] = mapped_column(
        String(32), default="pbkdf2_sha256", nullable=False
    )
    password_updated_at: Mapped[dt.datetime | None] = mapped_column(
        DateTime(timezone=True), default=None, nullable=True
    )

    status: Mapped[str] = mapped_column(
        String(16), default="active", nullable=False
    )
    email_verified: Mapped[bool] = mapped_column(
        Boolean, default=False, server_default="false", nullable=False
    )
    is_online: Mapped[bool] = mapped_column(
        Boolean, default=False, server_default="false", nullable=False
    )
    last_seen_at: Mapped[dt.datetime | None] = mapped_column(
        DateTime(timezone=True), default=None, nullable=True
    )
    last_login_at: Mapped[dt.datetime | None] = mapped_column(
        DateTime(timezone=True), default=None, nullable=True
    )
    failed_login_count: Mapped[int] = mapped_column(
        Integer, default=0, server_default="0", nullable=False
    )
    deleted_at: Mapped[dt.datetime | None] = mapped_column(
        DateTime(timezone=True), default=None, nullable=True
    )

    profile: Mapped["Profile | None"] = relationship(
        back_populates="account",
        cascade="all, delete-orphan",
        uselist=False,
        init=False,
    )
    preference: Mapped["Preference | None"] = relationship(
        back_populates="account",
        cascade="all, delete-orphan",
        uselist=False,
        init=False,
    )
    wallet: Mapped["Wallet | None"] = relationship(
        back_populates="account",
        cascade="all, delete-orphan",
        uselist=False,
        init=False,
    )
    sessions: Mapped[list["Session"]] = relationship(
        back_populates="account", cascade="all, delete-orphan", init=False
    )
    posts: Mapped[list["Post"]] = relationship(
        back_populates="author", cascade="all, delete-orphan", init=False
    )
    stories: Mapped[list["Story"]] = relationship(
        back_populates="author", cascade="all, delete-orphan", init=False
    )
    game_stats: Mapped[list["PlayerGameStat"]] = relationship(
        back_populates="account", cascade="all, delete-orphan", init=False
    )


class Profile(Base, TimestampMixin):
    __tablename__ = "profile"
    __table_args__ = (
        UniqueConstraint("account_id", name="uq_profile_account"),
        CheckConstraint(
            "default_post_privacy IN " + str(PRIVACY_VALUES),
            name="ck_profile_default_privacy",
        ),
    )

    id: Mapped[int] = mapped_column(primary_key=True, init=False)
    account_id: Mapped[int] = mapped_column(
        ForeignKey("account.id", ondelete="CASCADE"), nullable=False, index=True
    )
    display_name: Mapped[str] = mapped_column(
        String(80), default="", nullable=False
    )
    bio: Mapped[str] = mapped_column(Text, default="", nullable=False)
    location: Mapped[str] = mapped_column(
        String(120), default="", nullable=False
    )
    website: Mapped[str] = mapped_column(
        String(255), default="", nullable=False
    )
    # Upload metadata friendly: store the uploaded filename / key, not a blob.
    avatar_key: Mapped[str] = mapped_column(
        String(255), default="", nullable=False
    )
    cover_key: Mapped[str] = mapped_column(
        String(255), default="", nullable=False
    )
    birthdate: Mapped[dt.date | None] = mapped_column(
        default=None, nullable=True
    )
    default_post_privacy: Mapped[str] = mapped_column(
        String(16), default="public", nullable=False
    )

    account: Mapped[Account] = relationship(
        back_populates="profile", init=False
    )


class Preference(Base, TimestampMixin):
    __tablename__ = "preference"
    __table_args__ = (
        UniqueConstraint("account_id", name="uq_preference_account"),
        CheckConstraint(
            "theme IN " + str(THEME_VALUES), name="ck_preference_theme"
        ),
        CheckConstraint(
            "language IN " + str(LANGUAGE_VALUES), name="ck_preference_language"
        ),
        CheckConstraint(
            "profile_visibility IN " + str(PRIVACY_VALUES),
            name="ck_preference_visibility",
        ),
    )

    id: Mapped[int] = mapped_column(primary_key=True, init=False)
    account_id: Mapped[int] = mapped_column(
        ForeignKey("account.id", ondelete="CASCADE"), nullable=False, index=True
    )
    language: Mapped[str] = mapped_column(
        String(8), default="en", nullable=False
    )
    theme: Mapped[str] = mapped_column(
        String(8), default="system", nullable=False
    )
    profile_visibility: Mapped[str] = mapped_column(
        String(16), default="public", nullable=False
    )
    show_online_status: Mapped[bool] = mapped_column(
        Boolean, default=True, server_default="true", nullable=False
    )
    allow_friend_requests: Mapped[bool] = mapped_column(
        Boolean, default=True, server_default="true", nullable=False
    )
    allow_messages_from_strangers: Mapped[bool] = mapped_column(
        Boolean, default=False, server_default="false", nullable=False
    )
    notify_reactions: Mapped[bool] = mapped_column(
        Boolean, default=True, server_default="true", nullable=False
    )
    notify_comments: Mapped[bool] = mapped_column(
        Boolean, default=True, server_default="true", nullable=False
    )
    notify_messages: Mapped[bool] = mapped_column(
        Boolean, default=True, server_default="true", nullable=False
    )
    notify_friend_requests: Mapped[bool] = mapped_column(
        Boolean, default=True, server_default="true", nullable=False
    )
    notify_game_invites: Mapped[bool] = mapped_column(
        Boolean, default=True, server_default="true", nullable=False
    )

    account: Mapped[Account] = relationship(
        back_populates="preference", init=False
    )


class Session(Base):
    __tablename__ = "auth_session"
    __table_args__ = (
        UniqueConstraint("token_hash", name="uq_session_token_hash"),
        Index("ix_session_account_expires", "account_id", "expires_at"),
    )

    id: Mapped[int] = mapped_column(primary_key=True, init=False)
    account_id: Mapped[int] = mapped_column(
        ForeignKey("account.id", ondelete="CASCADE"), nullable=False, index=True
    )
    # Only a hash of the session token is persisted.
    token_hash: Mapped[str] = mapped_column(String(128), nullable=False)
    user_agent: Mapped[str] = mapped_column(
        String(255), default="", nullable=False
    )
    ip_address: Mapped[str] = mapped_column(
        String(64), default="", nullable=False
    )
    created_at: Mapped[dt.datetime] = mapped_column(
        DateTime(timezone=True),
        default=None,
        server_default=func.now(),
        nullable=False,
    )
    last_active_at: Mapped[dt.datetime] = mapped_column(
        DateTime(timezone=True),
        default=None,
        server_default=func.now(),
        nullable=False,
    )
    expires_at: Mapped[dt.datetime | None] = mapped_column(
        DateTime(timezone=True), default=None, nullable=True
    )
    revoked_at: Mapped[dt.datetime | None] = mapped_column(
        DateTime(timezone=True), default=None, nullable=True
    )

    account: Mapped[Account] = relationship(
        back_populates="sessions", init=False
    )


# ---------------------------------------------------------------------------
# Posts, media, reactions, threaded comments, shares
# ---------------------------------------------------------------------------


class Post(Base, TimestampMixin):
    __tablename__ = "post"
    __table_args__ = (
        CheckConstraint(
            "privacy IN " + str(PRIVACY_VALUES), name="ck_post_privacy"
        ),
        Index("ix_post_author_created", "author_id", "created_at"),
        Index("ix_post_privacy_created", "privacy", "created_at"),
    )

    id: Mapped[int] = mapped_column(primary_key=True, init=False)
    author_id: Mapped[int] = mapped_column(
        ForeignKey("account.id", ondelete="CASCADE"), nullable=False, index=True
    )
    body: Mapped[str] = mapped_column(Text, default="", nullable=False)
    privacy: Mapped[str] = mapped_column(
        String(16), default="public", nullable=False
    )
    location: Mapped[str] = mapped_column(
        String(120), default="", nullable=False
    )
    feeling: Mapped[str] = mapped_column(String(48), default="", nullable=False)
    is_edited: Mapped[bool] = mapped_column(
        Boolean, default=False, server_default="false", nullable=False
    )
    is_deleted: Mapped[bool] = mapped_column(
        Boolean, default=False, server_default="false", nullable=False
    )
    # Denormalized counters for cheap feed rendering.
    reaction_count: Mapped[int] = mapped_column(
        Integer, default=0, server_default="0", nullable=False
    )
    comment_count: Mapped[int] = mapped_column(
        Integer, default=0, server_default="0", nullable=False
    )
    share_count: Mapped[int] = mapped_column(
        Integer, default=0, server_default="0", nullable=False
    )
    # A shared post points at the original ("repost" semantics).
    shared_post_id: Mapped[int | None] = mapped_column(
        ForeignKey("post.id", ondelete="SET NULL"),
        default=None,
        nullable=True,
        index=True,
    )

    author: Mapped[Account] = relationship(back_populates="posts", init=False)
    media: Mapped[list["PostMedia"]] = relationship(
        back_populates="post", cascade="all, delete-orphan", init=False
    )
    reactions: Mapped[list["PostReaction"]] = relationship(
        back_populates="post", cascade="all, delete-orphan", init=False
    )
    comments: Mapped[list["Comment"]] = relationship(
        back_populates="post", cascade="all, delete-orphan", init=False
    )
    shares: Mapped[list["PostShare"]] = relationship(
        back_populates="post", cascade="all, delete-orphan", init=False
    )


class PostMedia(Base):
    __tablename__ = "post_media"
    __table_args__ = (
        CheckConstraint(
            "kind IN " + str(MEDIA_KIND_VALUES), name="ck_post_media_kind"
        ),
        Index("ix_post_media_post_position", "post_id", "position"),
    )

    id: Mapped[int] = mapped_column(primary_key=True, init=False)
    post_id: Mapped[int] = mapped_column(
        ForeignKey("post.id", ondelete="CASCADE"), nullable=False, index=True
    )
    kind: Mapped[str] = mapped_column(
        String(16), default="image", nullable=False
    )
    # Upload metadata (rx.get_upload_dir based storage).
    storage_key: Mapped[str] = mapped_column(String(255), nullable=False)
    original_name: Mapped[str] = mapped_column(
        String(255), default="", nullable=False
    )
    mime_type: Mapped[str] = mapped_column(
        String(128), default="", nullable=False
    )
    size_bytes: Mapped[int] = mapped_column(
        BigInteger, default=0, server_default="0", nullable=False
    )
    width: Mapped[int] = mapped_column(
        Integer, default=0, server_default="0", nullable=False
    )
    height: Mapped[int] = mapped_column(
        Integer, default=0, server_default="0", nullable=False
    )
    duration_seconds: Mapped[int] = mapped_column(
        Integer, default=0, server_default="0", nullable=False
    )
    alt_text: Mapped[str] = mapped_column(
        String(255), default="", nullable=False
    )
    position: Mapped[int] = mapped_column(
        Integer, default=0, server_default="0", nullable=False
    )
    created_at: Mapped[dt.datetime] = mapped_column(
        DateTime(timezone=True),
        default=None,
        server_default=func.now(),
        nullable=False,
    )

    post: Mapped[Post] = relationship(back_populates="media", init=False)


class PostReaction(Base):
    __tablename__ = "post_reaction"
    __table_args__ = (
        UniqueConstraint("post_id", "account_id", name="uq_post_reaction_once"),
        CheckConstraint(
            "kind IN " + str(REACTION_VALUES), name="ck_post_reaction_kind"
        ),
        Index("ix_post_reaction_account", "account_id", "created_at"),
    )

    id: Mapped[int] = mapped_column(primary_key=True, init=False)
    post_id: Mapped[int] = mapped_column(
        ForeignKey("post.id", ondelete="CASCADE"), nullable=False, index=True
    )
    account_id: Mapped[int] = mapped_column(
        ForeignKey("account.id", ondelete="CASCADE"), nullable=False
    )
    kind: Mapped[str] = mapped_column(
        String(16), default="like", nullable=False
    )
    created_at: Mapped[dt.datetime] = mapped_column(
        DateTime(timezone=True),
        default=None,
        server_default=func.now(),
        nullable=False,
    )
    updated_at: Mapped[dt.datetime] = mapped_column(
        DateTime(timezone=True),
        default=None,
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )

    post: Mapped[Post] = relationship(back_populates="reactions", init=False)


class Comment(Base, TimestampMixin):
    __tablename__ = "comment"
    __table_args__ = (
        Index("ix_comment_post_created", "post_id", "created_at"),
        Index("ix_comment_parent_created", "parent_id", "created_at"),
    )

    id: Mapped[int] = mapped_column(primary_key=True, init=False)
    post_id: Mapped[int] = mapped_column(
        ForeignKey("post.id", ondelete="CASCADE"), nullable=False, index=True
    )
    author_id: Mapped[int] = mapped_column(
        ForeignKey("account.id", ondelete="CASCADE"), nullable=False, index=True
    )
    parent_id: Mapped[int | None] = mapped_column(
        ForeignKey("comment.id", ondelete="CASCADE"),
        default=None,
        nullable=True,
    )
    body: Mapped[str] = mapped_column(Text, nullable=False)
    depth: Mapped[int] = mapped_column(
        Integer, default=0, server_default="0", nullable=False
    )
    reaction_count: Mapped[int] = mapped_column(
        Integer, default=0, server_default="0", nullable=False
    )
    reply_count: Mapped[int] = mapped_column(
        Integer, default=0, server_default="0", nullable=False
    )
    is_edited: Mapped[bool] = mapped_column(
        Boolean, default=False, server_default="false", nullable=False
    )
    is_deleted: Mapped[bool] = mapped_column(
        Boolean, default=False, server_default="false", nullable=False
    )

    post: Mapped[Post] = relationship(back_populates="comments", init=False)
    replies: Mapped[list["Comment"]] = relationship(
        back_populates="parent", cascade="all, delete-orphan", init=False
    )
    parent: Mapped["Comment | None"] = relationship(
        back_populates="replies", remote_side="Comment.id", init=False
    )
    reactions: Mapped[list["CommentReaction"]] = relationship(
        back_populates="comment", cascade="all, delete-orphan", init=False
    )


class CommentReaction(Base):
    __tablename__ = "comment_reaction"
    __table_args__ = (
        UniqueConstraint(
            "comment_id", "account_id", name="uq_comment_reaction_once"
        ),
        CheckConstraint(
            "kind IN " + str(REACTION_VALUES), name="ck_comment_reaction_kind"
        ),
    )

    id: Mapped[int] = mapped_column(primary_key=True, init=False)
    comment_id: Mapped[int] = mapped_column(
        ForeignKey("comment.id", ondelete="CASCADE"), nullable=False, index=True
    )
    account_id: Mapped[int] = mapped_column(
        ForeignKey("account.id", ondelete="CASCADE"), nullable=False, index=True
    )
    kind: Mapped[str] = mapped_column(
        String(16), default="like", nullable=False
    )
    created_at: Mapped[dt.datetime] = mapped_column(
        DateTime(timezone=True),
        default=None,
        server_default=func.now(),
        nullable=False,
    )

    comment: Mapped[Comment] = relationship(
        back_populates="reactions", init=False
    )


class PostShare(Base):
    __tablename__ = "post_share"
    __table_args__ = (
        CheckConstraint(
            "privacy IN " + str(PRIVACY_VALUES), name="ck_post_share_privacy"
        ),
        Index("ix_post_share_account_created", "account_id", "created_at"),
    )

    id: Mapped[int] = mapped_column(primary_key=True, init=False)
    post_id: Mapped[int] = mapped_column(
        ForeignKey("post.id", ondelete="CASCADE"), nullable=False, index=True
    )
    account_id: Mapped[int] = mapped_column(
        ForeignKey("account.id", ondelete="CASCADE"), nullable=False
    )
    channel: Mapped[str] = mapped_column(
        String(32), default="feed", nullable=False
    )
    message: Mapped[str] = mapped_column(Text, default="", nullable=False)
    privacy: Mapped[str] = mapped_column(
        String(16), default="public", nullable=False
    )
    created_at: Mapped[dt.datetime] = mapped_column(
        DateTime(timezone=True),
        default=None,
        server_default=func.now(),
        nullable=False,
    )

    post: Mapped[Post] = relationship(back_populates="shares", init=False)


# ---------------------------------------------------------------------------
# Stories (expiring), media, reactions, replies, views
# ---------------------------------------------------------------------------


class Story(Base, TimestampMixin):
    __tablename__ = "story"
    __table_args__ = (
        CheckConstraint(
            "privacy IN " + str(PRIVACY_VALUES), name="ck_story_privacy"
        ),
        Index("ix_story_author_expires", "author_id", "expires_at"),
        Index("ix_story_expires_at", "expires_at"),
    )

    id: Mapped[int] = mapped_column(primary_key=True, init=False)
    author_id: Mapped[int] = mapped_column(
        ForeignKey("account.id", ondelete="CASCADE"), nullable=False, index=True
    )
    caption: Mapped[str] = mapped_column(Text, default="", nullable=False)
    background_color: Mapped[str] = mapped_column(
        String(16), default="", nullable=False
    )
    privacy: Mapped[str] = mapped_column(
        String(16), default="friends", nullable=False
    )
    expires_at: Mapped[dt.datetime] = mapped_column(
        DateTime(timezone=True), nullable=False
    )
    view_count: Mapped[int] = mapped_column(
        Integer, default=0, server_default="0", nullable=False
    )
    reaction_count: Mapped[int] = mapped_column(
        Integer, default=0, server_default="0", nullable=False
    )
    reply_count: Mapped[int] = mapped_column(
        Integer, default=0, server_default="0", nullable=False
    )
    is_deleted: Mapped[bool] = mapped_column(
        Boolean, default=False, server_default="false", nullable=False
    )

    author: Mapped[Account] = relationship(back_populates="stories", init=False)
    media: Mapped[list["StoryMedia"]] = relationship(
        back_populates="story", cascade="all, delete-orphan", init=False
    )
    reactions: Mapped[list["StoryReaction"]] = relationship(
        back_populates="story", cascade="all, delete-orphan", init=False
    )
    replies: Mapped[list["StoryReply"]] = relationship(
        back_populates="story", cascade="all, delete-orphan", init=False
    )
    views: Mapped[list["StoryView"]] = relationship(
        back_populates="story", cascade="all, delete-orphan", init=False
    )


class StoryMedia(Base):
    __tablename__ = "story_media"
    __table_args__ = (
        CheckConstraint(
            "kind IN " + str(MEDIA_KIND_VALUES), name="ck_story_media_kind"
        ),
        Index("ix_story_media_story_position", "story_id", "position"),
    )

    id: Mapped[int] = mapped_column(primary_key=True, init=False)
    story_id: Mapped[int] = mapped_column(
        ForeignKey("story.id", ondelete="CASCADE"), nullable=False, index=True
    )
    kind: Mapped[str] = mapped_column(
        String(16), default="image", nullable=False
    )
    storage_key: Mapped[str] = mapped_column(String(255), nullable=False)
    original_name: Mapped[str] = mapped_column(
        String(255), default="", nullable=False
    )
    mime_type: Mapped[str] = mapped_column(
        String(128), default="", nullable=False
    )
    size_bytes: Mapped[int] = mapped_column(
        BigInteger, default=0, server_default="0", nullable=False
    )
    width: Mapped[int] = mapped_column(
        Integer, default=0, server_default="0", nullable=False
    )
    height: Mapped[int] = mapped_column(
        Integer, default=0, server_default="0", nullable=False
    )
    duration_seconds: Mapped[int] = mapped_column(
        Integer, default=0, server_default="0", nullable=False
    )
    position: Mapped[int] = mapped_column(
        Integer, default=0, server_default="0", nullable=False
    )
    created_at: Mapped[dt.datetime] = mapped_column(
        DateTime(timezone=True),
        default=None,
        server_default=func.now(),
        nullable=False,
    )

    story: Mapped[Story] = relationship(back_populates="media", init=False)


class StoryView(Base):
    __tablename__ = "story_view"
    __table_args__ = (
        UniqueConstraint("story_id", "account_id", name="uq_story_view_once"),
    )

    id: Mapped[int] = mapped_column(primary_key=True, init=False)
    story_id: Mapped[int] = mapped_column(
        ForeignKey("story.id", ondelete="CASCADE"), nullable=False, index=True
    )
    account_id: Mapped[int] = mapped_column(
        ForeignKey("account.id", ondelete="CASCADE"), nullable=False, index=True
    )
    viewed_at: Mapped[dt.datetime] = mapped_column(
        DateTime(timezone=True),
        default=None,
        server_default=func.now(),
        nullable=False,
    )

    story: Mapped[Story] = relationship(back_populates="views", init=False)


class StoryReaction(Base):
    __tablename__ = "story_reaction"
    __table_args__ = (
        UniqueConstraint(
            "story_id", "account_id", name="uq_story_reaction_once"
        ),
        CheckConstraint(
            "kind IN " + str(REACTION_VALUES), name="ck_story_reaction_kind"
        ),
    )

    id: Mapped[int] = mapped_column(primary_key=True, init=False)
    story_id: Mapped[int] = mapped_column(
        ForeignKey("story.id", ondelete="CASCADE"), nullable=False, index=True
    )
    account_id: Mapped[int] = mapped_column(
        ForeignKey("account.id", ondelete="CASCADE"), nullable=False, index=True
    )
    kind: Mapped[str] = mapped_column(
        String(16), default="love", nullable=False
    )
    created_at: Mapped[dt.datetime] = mapped_column(
        DateTime(timezone=True),
        default=None,
        server_default=func.now(),
        nullable=False,
    )

    story: Mapped[Story] = relationship(back_populates="reactions", init=False)


class StoryReply(Base):
    __tablename__ = "story_reply"
    __table_args__ = (
        Index("ix_story_reply_story_created", "story_id", "created_at"),
    )

    id: Mapped[int] = mapped_column(primary_key=True, init=False)
    story_id: Mapped[int] = mapped_column(
        ForeignKey("story.id", ondelete="CASCADE"), nullable=False, index=True
    )
    author_id: Mapped[int] = mapped_column(
        ForeignKey("account.id", ondelete="CASCADE"), nullable=False, index=True
    )
    body: Mapped[str] = mapped_column(Text, nullable=False)
    is_deleted: Mapped[bool] = mapped_column(
        Boolean, default=False, server_default="false", nullable=False
    )
    created_at: Mapped[dt.datetime] = mapped_column(
        DateTime(timezone=True),
        default=None,
        server_default=func.now(),
        nullable=False,
    )

    story: Mapped[Story] = relationship(back_populates="replies", init=False)


# ---------------------------------------------------------------------------
# Friend requests, friendships, follows, blocks
# ---------------------------------------------------------------------------


class FriendRequest(Base, TimestampMixin):
    __tablename__ = "friend_request"
    __table_args__ = (
        UniqueConstraint(
            "sender_id", "receiver_id", name="uq_friend_request_pair"
        ),
        CheckConstraint(
            "sender_id <> receiver_id", name="ck_friend_request_not_self"
        ),
        CheckConstraint(
            "status IN " + str(REQUEST_STATUS_VALUES),
            name="ck_friend_request_status",
        ),
        Index("ix_friend_request_receiver_status", "receiver_id", "status"),
    )

    id: Mapped[int] = mapped_column(primary_key=True, init=False)
    sender_id: Mapped[int] = mapped_column(
        ForeignKey("account.id", ondelete="CASCADE"), nullable=False, index=True
    )
    receiver_id: Mapped[int] = mapped_column(
        ForeignKey("account.id", ondelete="CASCADE"), nullable=False
    )
    status: Mapped[str] = mapped_column(
        String(16), default="pending", nullable=False
    )
    message: Mapped[str] = mapped_column(
        String(255), default="", nullable=False
    )
    responded_at: Mapped[dt.datetime | None] = mapped_column(
        DateTime(timezone=True), default=None, nullable=True
    )


class Friendship(Base):
    """Symmetric friendship stored once with account_low_id < account_high_id."""

    __tablename__ = "friendship"
    __table_args__ = (
        UniqueConstraint(
            "account_low_id", "account_high_id", name="uq_friendship_pair"
        ),
        CheckConstraint(
            "account_low_id < account_high_id", name="ck_friendship_ordered"
        ),
    )

    id: Mapped[int] = mapped_column(primary_key=True, init=False)
    account_low_id: Mapped[int] = mapped_column(
        ForeignKey("account.id", ondelete="CASCADE"), nullable=False, index=True
    )
    account_high_id: Mapped[int] = mapped_column(
        ForeignKey("account.id", ondelete="CASCADE"), nullable=False, index=True
    )
    is_favorite: Mapped[bool] = mapped_column(
        Boolean, default=False, server_default="false", nullable=False
    )
    created_at: Mapped[dt.datetime] = mapped_column(
        DateTime(timezone=True),
        default=None,
        server_default=func.now(),
        nullable=False,
    )


class Follow(Base):
    __tablename__ = "follow"
    __table_args__ = (
        UniqueConstraint("follower_id", "followee_id", name="uq_follow_pair"),
        CheckConstraint(
            "follower_id <> followee_id", name="ck_follow_not_self"
        ),
        Index("ix_follow_followee_created", "followee_id", "created_at"),
    )

    id: Mapped[int] = mapped_column(primary_key=True, init=False)
    follower_id: Mapped[int] = mapped_column(
        ForeignKey("account.id", ondelete="CASCADE"), nullable=False, index=True
    )
    followee_id: Mapped[int] = mapped_column(
        ForeignKey("account.id", ondelete="CASCADE"), nullable=False
    )
    notifications_enabled: Mapped[bool] = mapped_column(
        Boolean, default=True, server_default="true", nullable=False
    )
    created_at: Mapped[dt.datetime] = mapped_column(
        DateTime(timezone=True),
        default=None,
        server_default=func.now(),
        nullable=False,
    )


class Block(Base):
    __tablename__ = "account_block"
    __table_args__ = (
        UniqueConstraint("blocker_id", "blocked_id", name="uq_block_pair"),
        CheckConstraint("blocker_id <> blocked_id", name="ck_block_not_self"),
    )

    id: Mapped[int] = mapped_column(primary_key=True, init=False)
    blocker_id: Mapped[int] = mapped_column(
        ForeignKey("account.id", ondelete="CASCADE"), nullable=False, index=True
    )
    blocked_id: Mapped[int] = mapped_column(
        ForeignKey("account.id", ondelete="CASCADE"), nullable=False, index=True
    )
    reason: Mapped[str] = mapped_column(String(255), default="", nullable=False)
    created_at: Mapped[dt.datetime] = mapped_column(
        DateTime(timezone=True),
        default=None,
        server_default=func.now(),
        nullable=False,
    )


# ---------------------------------------------------------------------------
# Conversations, participants, messages, read state
# ---------------------------------------------------------------------------


class Conversation(Base, TimestampMixin):
    __tablename__ = "conversation"
    __table_args__ = (
        UniqueConstraint("direct_key", name="uq_conversation_direct_key"),
        Index("ix_conversation_last_message", "last_message_at"),
    )

    id: Mapped[int] = mapped_column(primary_key=True, init=False)
    is_group: Mapped[bool] = mapped_column(
        Boolean, default=False, server_default="false", nullable=False
    )
    title: Mapped[str] = mapped_column(String(120), default="", nullable=False)
    created_by_id: Mapped[int | None] = mapped_column(
        ForeignKey("account.id", ondelete="SET NULL"),
        default=None,
        nullable=True,
        index=True,
    )
    # Deterministic "low:high" key for 1:1 chats, NULL for groups.
    direct_key: Mapped[str | None] = mapped_column(
        String(64), default=None, nullable=True
    )
    last_message_at: Mapped[dt.datetime | None] = mapped_column(
        DateTime(timezone=True), default=None, nullable=True
    )
    last_message_preview: Mapped[str] = mapped_column(
        String(255), default="", nullable=False
    )

    participants: Mapped[list["ConversationParticipant"]] = relationship(
        back_populates="conversation", cascade="all, delete-orphan", init=False
    )
    messages: Mapped[list["Message"]] = relationship(
        back_populates="conversation", cascade="all, delete-orphan", init=False
    )


class ConversationParticipant(Base):
    __tablename__ = "conversation_participant"
    __table_args__ = (
        UniqueConstraint(
            "conversation_id", "account_id", name="uq_participant_once"
        ),
        Index("ix_participant_account_conv", "account_id", "conversation_id"),
    )

    id: Mapped[int] = mapped_column(primary_key=True, init=False)
    conversation_id: Mapped[int] = mapped_column(
        ForeignKey("conversation.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    account_id: Mapped[int] = mapped_column(
        ForeignKey("account.id", ondelete="CASCADE"), nullable=False
    )
    role: Mapped[str] = mapped_column(
        String(16), default="member", nullable=False
    )
    unread_count: Mapped[int] = mapped_column(
        Integer, default=0, server_default="0", nullable=False
    )
    last_read_message_id: Mapped[int | None] = mapped_column(
        ForeignKey("message.id", ondelete="SET NULL"),
        default=None,
        nullable=True,
    )
    last_read_at: Mapped[dt.datetime | None] = mapped_column(
        DateTime(timezone=True), default=None, nullable=True
    )
    is_typing: Mapped[bool] = mapped_column(
        Boolean, default=False, server_default="false", nullable=False
    )
    typing_updated_at: Mapped[dt.datetime | None] = mapped_column(
        DateTime(timezone=True), default=None, nullable=True
    )
    is_muted: Mapped[bool] = mapped_column(
        Boolean, default=False, server_default="false", nullable=False
    )
    joined_at: Mapped[dt.datetime] = mapped_column(
        DateTime(timezone=True),
        default=None,
        server_default=func.now(),
        nullable=False,
    )
    left_at: Mapped[dt.datetime | None] = mapped_column(
        DateTime(timezone=True), default=None, nullable=True
    )

    conversation: Mapped[Conversation] = relationship(
        back_populates="participants", init=False
    )


class Message(Base, TimestampMixin):
    __tablename__ = "message"
    __table_args__ = (
        CheckConstraint(
            "kind IN " + str(MESSAGE_KIND_VALUES), name="ck_message_kind"
        ),
        Index(
            "ix_message_conversation_created", "conversation_id", "created_at"
        ),
    )

    id: Mapped[int] = mapped_column(primary_key=True, init=False)
    conversation_id: Mapped[int] = mapped_column(
        ForeignKey("conversation.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    sender_id: Mapped[int] = mapped_column(
        ForeignKey("account.id", ondelete="CASCADE"), nullable=False, index=True
    )
    kind: Mapped[str] = mapped_column(
        String(16), default="text", nullable=False
    )
    body: Mapped[str] = mapped_column(Text, default="", nullable=False)
    # Optional single attachment metadata (upload key based).
    storage_key: Mapped[str] = mapped_column(
        String(255), default="", nullable=False
    )
    mime_type: Mapped[str] = mapped_column(
        String(128), default="", nullable=False
    )
    size_bytes: Mapped[int] = mapped_column(
        BigInteger, default=0, server_default="0", nullable=False
    )
    reply_to_id: Mapped[int | None] = mapped_column(
        ForeignKey("message.id", ondelete="SET NULL"),
        default=None,
        nullable=True,
    )
    is_edited: Mapped[bool] = mapped_column(
        Boolean, default=False, server_default="false", nullable=False
    )
    is_deleted: Mapped[bool] = mapped_column(
        Boolean, default=False, server_default="false", nullable=False
    )

    conversation: Mapped[Conversation] = relationship(
        back_populates="messages", init=False
    )
    receipts: Mapped[list["MessageReceipt"]] = relationship(
        back_populates="message", cascade="all, delete-orphan", init=False
    )


class MessageReceipt(Base):
    __tablename__ = "message_receipt"
    __table_args__ = (
        UniqueConstraint(
            "message_id", "account_id", name="uq_message_receipt_once"
        ),
        Index("ix_message_receipt_account", "account_id", "read_at"),
    )

    id: Mapped[int] = mapped_column(primary_key=True, init=False)
    message_id: Mapped[int] = mapped_column(
        ForeignKey("message.id", ondelete="CASCADE"), nullable=False, index=True
    )
    account_id: Mapped[int] = mapped_column(
        ForeignKey("account.id", ondelete="CASCADE"), nullable=False
    )
    delivered_at: Mapped[dt.datetime | None] = mapped_column(
        DateTime(timezone=True), default=None, nullable=True
    )
    read_at: Mapped[dt.datetime | None] = mapped_column(
        DateTime(timezone=True), default=None, nullable=True
    )

    message: Mapped[Message] = relationship(
        back_populates="receipts", init=False
    )


# ---------------------------------------------------------------------------
# Games: catalog, lobby rooms, memberships, activity, player statistics
# ---------------------------------------------------------------------------


class Game(Base, TimestampMixin):
    __tablename__ = "game"
    __table_args__ = (UniqueConstraint("slug", name="uq_game_slug"),)

    id: Mapped[int] = mapped_column(primary_key=True, init=False)
    slug: Mapped[str] = mapped_column(String(64), nullable=False)
    name: Mapped[str] = mapped_column(String(80), nullable=False)
    description: Mapped[str] = mapped_column(Text, default="", nullable=False)
    category: Mapped[str] = mapped_column(
        String(48), default="casual", nullable=False
    )
    cover_key: Mapped[str] = mapped_column(
        String(255), default="", nullable=False
    )
    min_players: Mapped[int] = mapped_column(
        Integer, default=2, server_default="2", nullable=False
    )
    max_players: Mapped[int] = mapped_column(
        Integer, default=4, server_default="4", nullable=False
    )
    # Virtual-coin entry fee / reward only. No real currency anywhere.
    default_entry_coins: Mapped[int] = mapped_column(
        Integer, default=0, server_default="0", nullable=False
    )
    is_active: Mapped[bool] = mapped_column(
        Boolean, default=True, server_default="true", nullable=False
    )

    rooms: Mapped[list["GameRoom"]] = relationship(
        back_populates="game", cascade="all, delete-orphan", init=False
    )
    stats: Mapped[list["PlayerGameStat"]] = relationship(
        back_populates="game", cascade="all, delete-orphan", init=False
    )


class GameRoom(Base, TimestampMixin):
    __tablename__ = "game_room"
    __table_args__ = (
        UniqueConstraint("code", name="uq_game_room_code"),
        CheckConstraint(
            "status IN " + str(ROOM_STATUS_VALUES), name="ck_game_room_status"
        ),
        CheckConstraint("max_players >= 2", name="ck_game_room_max_players"),
        CheckConstraint("pot_coins >= 0", name="ck_game_room_pot_non_negative"),
        CheckConstraint(
            "state_version >= 0", name="ck_game_room_state_version"
        ),
        CheckConstraint("round_number >= 0", name="ck_game_room_round_number"),
        Index("ix_game_room_game_status", "game_id", "status"),
        Index(
            "ix_game_room_status_turn_deadline", "status", "turn_deadline_at"
        ),
        Index("ix_game_room_current_turn", "current_turn_account_id"),
        Index("ix_game_room_winner", "winner_account_id"),
    )

    id: Mapped[int] = mapped_column(primary_key=True, init=False)
    game_id: Mapped[int] = mapped_column(
        ForeignKey("game.id", ondelete="CASCADE"), nullable=False, index=True
    )
    host_id: Mapped[int] = mapped_column(
        ForeignKey("account.id", ondelete="CASCADE"), nullable=False, index=True
    )
    code: Mapped[str] = mapped_column(String(12), nullable=False)
    name: Mapped[str] = mapped_column(String(80), default="", nullable=False)
    status: Mapped[str] = mapped_column(
        String(16), default="open", nullable=False
    )
    is_private: Mapped[bool] = mapped_column(
        Boolean, default=False, server_default="false", nullable=False
    )
    password_hash: Mapped[str] = mapped_column(
        String(255), default="", nullable=False
    )
    max_players: Mapped[int] = mapped_column(
        Integer, default=4, server_default="4", nullable=False
    )
    player_count: Mapped[int] = mapped_column(
        Integer, default=0, server_default="0", nullable=False
    )
    entry_coins: Mapped[int] = mapped_column(
        Integer, default=0, server_default="0", nullable=False
    )
    started_at: Mapped[dt.datetime | None] = mapped_column(
        DateTime(timezone=True), default=None, nullable=True
    )
    finished_at: Mapped[dt.datetime | None] = mapped_column(
        DateTime(timezone=True), default=None, nullable=True
    )

    # ---- Authoritative server-driven play -------------------------------
    # Flexible per-game rules / configuration, JSON encoded as text so the
    # same column serves loto tiers, domino Maty targets and variants, ludo,
    # faritany, dots-and-boxes grid size, rami, tri and billiards.
    rules_json: Mapped[str] = mapped_column(
        Text, default="{}", server_default="{}", nullable=False
    )
    # Full authoritative match state owned by the server (JSON as text).
    state_json: Mapped[str] = mapped_column(
        Text, default="{}", server_default="{}", nullable=False
    )
    current_turn_account_id: Mapped[int | None] = mapped_column(
        ForeignKey("account.id", ondelete="SET NULL"),
        default=None,
        nullable=True,
    )
    turn_deadline_at: Mapped[dt.datetime | None] = mapped_column(
        DateTime(timezone=True), default=None, nullable=True
    )
    round_number: Mapped[int] = mapped_column(
        Integer, default=0, server_default="0", nullable=False
    )
    # Virtual coin pot only (accumulated entry coins); never real money.
    pot_coins: Mapped[int] = mapped_column(
        BigInteger, default=0, server_default="0", nullable=False
    )
    # Optimistic concurrency guard for authoritative state transitions.
    state_version: Mapped[int] = mapped_column(
        Integer, default=0, server_default="0", nullable=False
    )
    winner_account_id: Mapped[int | None] = mapped_column(
        ForeignKey("account.id", ondelete="SET NULL"),
        default=None,
        nullable=True,
    )
    settled_at: Mapped[dt.datetime | None] = mapped_column(
        DateTime(timezone=True), default=None, nullable=True
    )

    game: Mapped[Game] = relationship(back_populates="rooms", init=False)
    members: Mapped[list["GameRoomMember"]] = relationship(
        back_populates="room", cascade="all, delete-orphan", init=False
    )
    events: Mapped[list["GameRoomEvent"]] = relationship(
        back_populates="room", cascade="all, delete-orphan", init=False
    )
    actions: Mapped[list["GameAction"]] = relationship(
        back_populates="room", cascade="all, delete-orphan", init=False
    )
    bingo_cards: Mapped[list["BingoCard"]] = relationship(
        back_populates="room", cascade="all, delete-orphan", init=False
    )
    reactions: Mapped[list["GameReaction"]] = relationship(
        back_populates="room", cascade="all, delete-orphan", init=False
    )


class GameRoomMember(Base):
    __tablename__ = "game_room_member"
    __table_args__ = (
        UniqueConstraint("room_id", "account_id", name="uq_room_member_once"),
        Index("ix_room_member_account", "account_id", "joined_at"),
    )

    id: Mapped[int] = mapped_column(primary_key=True, init=False)
    room_id: Mapped[int] = mapped_column(
        ForeignKey("game_room.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    account_id: Mapped[int] = mapped_column(
        ForeignKey("account.id", ondelete="CASCADE"), nullable=False
    )
    seat: Mapped[int] = mapped_column(
        Integer, default=0, server_default="0", nullable=False
    )
    is_host: Mapped[bool] = mapped_column(
        Boolean, default=False, server_default="false", nullable=False
    )
    is_ready: Mapped[bool] = mapped_column(
        Boolean, default=False, server_default="false", nullable=False
    )
    score: Mapped[int] = mapped_column(
        Integer, default=0, server_default="0", nullable=False
    )
    result: Mapped[str] = mapped_column(String(16), default="", nullable=False)
    joined_at: Mapped[dt.datetime] = mapped_column(
        DateTime(timezone=True),
        default=None,
        server_default=func.now(),
        nullable=False,
    )
    left_at: Mapped[dt.datetime | None] = mapped_column(
        DateTime(timezone=True), default=None, nullable=True
    )

    room: Mapped[GameRoom] = relationship(back_populates="members", init=False)


class GameRoomEvent(Base):
    """Append-only lobby / match activity log."""

    __tablename__ = "game_room_event"
    __table_args__ = (
        Index("ix_room_event_room_created", "room_id", "created_at"),
    )

    id: Mapped[int] = mapped_column(primary_key=True, init=False)
    room_id: Mapped[int] = mapped_column(
        ForeignKey("game_room.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    account_id: Mapped[int | None] = mapped_column(
        ForeignKey("account.id", ondelete="SET NULL"),
        default=None,
        nullable=True,
        index=True,
    )
    event_type: Mapped[str] = mapped_column(String(32), nullable=False)
    detail: Mapped[str] = mapped_column(Text, default="", nullable=False)
    created_at: Mapped[dt.datetime] = mapped_column(
        DateTime(timezone=True),
        default=None,
        server_default=func.now(),
        nullable=False,
    )

    room: Mapped[GameRoom] = relationship(back_populates="events", init=False)


class GameAction(Base):
    """Append-only authoritative action log for a match.

    Every accepted player or server action is recorded with the room state
    version it produced, giving a deterministic, replayable match history.
    Rows are never updated or deleted by application logic.
    """

    __tablename__ = "game_action"
    __table_args__ = (
        UniqueConstraint(
            "room_id", "sequence", name="uq_game_action_room_sequence"
        ),
        CheckConstraint(
            "kind IN " + str(GAME_ACTION_KIND_VALUES),
            name="ck_game_action_kind",
        ),
        CheckConstraint("sequence >= 0", name="ck_game_action_sequence"),
        CheckConstraint(
            "state_version >= 0", name="ck_game_action_state_version"
        ),
        Index("ix_game_action_room_created", "room_id", "created_at"),
        Index("ix_game_action_room_version", "room_id", "state_version"),
        Index("ix_game_action_account_created", "account_id", "created_at"),
    )

    id: Mapped[int] = mapped_column(primary_key=True, init=False)
    room_id: Mapped[int] = mapped_column(
        ForeignKey("game_room.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    # NULL for server-generated actions (timed draws, timeouts, settlement).
    account_id: Mapped[int | None] = mapped_column(
        ForeignKey("account.id", ondelete="SET NULL"),
        default=None,
        nullable=True,
    )
    kind: Mapped[str] = mapped_column(
        String(32), default="system", nullable=False
    )
    # JSON encoded as text: dice values, tile placement, drawn number, etc.
    payload_json: Mapped[str] = mapped_column(
        Text, default="{}", server_default="{}", nullable=False
    )
    # Room state_version AFTER this action was applied.
    state_version: Mapped[int] = mapped_column(
        Integer, default=0, server_default="0", nullable=False
    )
    # Monotonic per-room ordering, independent of clock skew.
    sequence: Mapped[int] = mapped_column(
        Integer, default=0, server_default="0", nullable=False
    )
    round_number: Mapped[int] = mapped_column(
        Integer, default=0, server_default="0", nullable=False
    )
    created_at: Mapped[dt.datetime] = mapped_column(
        DateTime(timezone=True),
        default=None,
        server_default=func.now(),
        nullable=False,
    )

    room: Mapped[GameRoom] = relationship(back_populates="actions", init=False)


class BingoCard(Base):
    """A single purchased LOTO 9x3 card (1-10 cards per player per room).

    Cards are bought with virtual coins only. The canonical grid, the drawn /
    marked progress and the per-tier claim flags all live here so the server
    remains the sole authority for Quine / Double Quine / Full House payouts.
    """

    __tablename__ = "bingo_card"
    __table_args__ = (
        UniqueConstraint(
            "room_id",
            "account_id",
            "card_index",
            name="uq_bingo_card_room_account_index",
        ),
        CheckConstraint(
            "card_index >= 1 AND card_index <= 10",
            name="ck_bingo_card_index_range",
        ),
        CheckConstraint(
            "marked_count >= 0", name="ck_bingo_card_marked_non_negative"
        ),
        CheckConstraint(
            "price_coins >= 0", name="ck_bingo_card_price_non_negative"
        ),
        Index("ix_bingo_card_room_account", "room_id", "account_id"),
        Index("ix_bingo_card_account_created", "account_id", "created_at"),
    )

    id: Mapped[int] = mapped_column(primary_key=True, init=False)
    room_id: Mapped[int] = mapped_column(
        ForeignKey("game_room.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    account_id: Mapped[int] = mapped_column(
        ForeignKey("account.id", ondelete="CASCADE"), nullable=False, index=True
    )
    # 1..10 within the room for this player.
    card_index: Mapped[int] = mapped_column(Integer, nullable=False)
    # Canonical immutable 9x3 grid as JSON text: 3 rows x 9 columns, 0 = blank.
    grid_json: Mapped[str] = mapped_column(
        Text, default="[]", server_default="[]", nullable=False
    )
    # Numbers of this card already drawn/marked, JSON list of ints.
    marked_json: Mapped[str] = mapped_column(
        Text, default="[]", server_default="[]", nullable=False
    )
    marked_count: Mapped[int] = mapped_column(
        Integer, default=0, server_default="0", nullable=False
    )
    # Count of marked cells per row, JSON list of 3 ints (tier detection).
    row_progress_json: Mapped[str] = mapped_column(
        Text, default="[0, 0, 0]", server_default="[0, 0, 0]", nullable=False
    )
    # Virtual coin price paid for this card (points only, no cash value).
    price_coins: Mapped[int] = mapped_column(
        Integer, default=0, server_default="0", nullable=False
    )
    tier: Mapped[str] = mapped_column(String(16), default="", nullable=False)
    claimed_quine: Mapped[bool] = mapped_column(
        Boolean, default=False, server_default="false", nullable=False
    )
    claimed_quine_at: Mapped[dt.datetime | None] = mapped_column(
        DateTime(timezone=True), default=None, nullable=True
    )
    claimed_double_quine: Mapped[bool] = mapped_column(
        Boolean, default=False, server_default="false", nullable=False
    )
    claimed_double_quine_at: Mapped[dt.datetime | None] = mapped_column(
        DateTime(timezone=True), default=None, nullable=True
    )
    claimed_full_house: Mapped[bool] = mapped_column(
        Boolean, default=False, server_default="false", nullable=False
    )
    claimed_full_house_at: Mapped[dt.datetime | None] = mapped_column(
        DateTime(timezone=True), default=None, nullable=True
    )
    is_void: Mapped[bool] = mapped_column(
        Boolean, default=False, server_default="false", nullable=False
    )
    created_at: Mapped[dt.datetime] = mapped_column(
        DateTime(timezone=True),
        default=None,
        server_default=func.now(),
        nullable=False,
    )
    updated_at: Mapped[dt.datetime] = mapped_column(
        DateTime(timezone=True),
        default=None,
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )

    room: Mapped[GameRoom] = relationship(
        back_populates="bingo_cards", init=False
    )


class GameReaction(Base):
    """Persisted, ephemeral-style emoji reaction fired inside a game room."""

    __tablename__ = "game_reaction"
    __table_args__ = (
        Index("ix_game_reaction_room_created", "room_id", "created_at"),
        Index("ix_game_reaction_room_expires", "room_id", "expires_at"),
        Index("ix_game_reaction_account_created", "account_id", "created_at"),
    )

    id: Mapped[int] = mapped_column(primary_key=True, init=False)
    room_id: Mapped[int] = mapped_column(
        ForeignKey("game_room.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    account_id: Mapped[int] = mapped_column(
        ForeignKey("account.id", ondelete="CASCADE"), nullable=False, index=True
    )
    # Optional target: a seat, a tile, another player, etc.
    target_account_id: Mapped[int | None] = mapped_column(
        ForeignKey("account.id", ondelete="SET NULL"),
        default=None,
        nullable=True,
    )
    emoji: Mapped[str] = mapped_column(String(16), default="", nullable=False)
    label: Mapped[str] = mapped_column(String(32), default="", nullable=False)
    round_number: Mapped[int] = mapped_column(
        Integer, default=0, server_default="0", nullable=False
    )
    # When the floating reaction should stop being rendered.
    expires_at: Mapped[dt.datetime | None] = mapped_column(
        DateTime(timezone=True), default=None, nullable=True
    )
    created_at: Mapped[dt.datetime] = mapped_column(
        DateTime(timezone=True),
        default=None,
        server_default=func.now(),
        nullable=False,
    )

    room: Mapped[GameRoom] = relationship(
        back_populates="reactions", init=False
    )


class PlayerGameStat(Base, TimestampMixin):
    __tablename__ = "player_game_stat"
    __table_args__ = (
        UniqueConstraint("account_id", "game_id", name="uq_player_game_stat"),
        Index("ix_player_game_stat_game_wins", "game_id", "wins"),
    )

    id: Mapped[int] = mapped_column(primary_key=True, init=False)
    account_id: Mapped[int] = mapped_column(
        ForeignKey("account.id", ondelete="CASCADE"), nullable=False, index=True
    )
    game_id: Mapped[int] = mapped_column(
        ForeignKey("game.id", ondelete="CASCADE"), nullable=False, index=True
    )
    matches_played: Mapped[int] = mapped_column(
        Integer, default=0, server_default="0", nullable=False
    )
    wins: Mapped[int] = mapped_column(
        Integer, default=0, server_default="0", nullable=False
    )
    losses: Mapped[int] = mapped_column(
        Integer, default=0, server_default="0", nullable=False
    )
    draws: Mapped[int] = mapped_column(
        Integer, default=0, server_default="0", nullable=False
    )
    best_score: Mapped[int] = mapped_column(
        Integer, default=0, server_default="0", nullable=False
    )
    total_score: Mapped[int] = mapped_column(
        BigInteger, default=0, server_default="0", nullable=False
    )
    current_streak: Mapped[int] = mapped_column(
        Integer, default=0, server_default="0", nullable=False
    )
    best_streak: Mapped[int] = mapped_column(
        Integer, default=0, server_default="0", nullable=False
    )
    coins_earned: Mapped[int] = mapped_column(
        BigInteger, default=0, server_default="0", nullable=False
    )
    last_played_at: Mapped[dt.datetime | None] = mapped_column(
        DateTime(timezone=True), default=None, nullable=True
    )

    account: Mapped[Account] = relationship(
        back_populates="game_stats", init=False
    )
    game: Mapped[Game] = relationship(back_populates="stats", init=False)


# ---------------------------------------------------------------------------
# Wallets and immutable virtual coin ledger
# ---------------------------------------------------------------------------


class Wallet(Base, TimestampMixin):
    """Virtual TATA Coins wallet. Coins have no cash value and cannot be
    converted to or from real money, so no fiat/payment fields exist."""

    __tablename__ = "wallet"
    __table_args__ = (
        UniqueConstraint("account_id", name="uq_wallet_account"),
        CheckConstraint(
            "balance_coins >= 0", name="ck_wallet_balance_non_negative"
        ),
    )

    id: Mapped[int] = mapped_column(primary_key=True, init=False)
    account_id: Mapped[int] = mapped_column(
        ForeignKey("account.id", ondelete="CASCADE"), nullable=False, index=True
    )
    balance_coins: Mapped[int] = mapped_column(
        BigInteger, default=0, server_default="0", nullable=False
    )
    lifetime_earned_coins: Mapped[int] = mapped_column(
        BigInteger, default=0, server_default="0", nullable=False
    )
    lifetime_spent_coins: Mapped[int] = mapped_column(
        BigInteger, default=0, server_default="0", nullable=False
    )
    last_daily_reward_at: Mapped[dt.datetime | None] = mapped_column(
        DateTime(timezone=True), default=None, nullable=True
    )
    is_locked: Mapped[bool] = mapped_column(
        Boolean, default=False, server_default="false", nullable=False
    )

    account: Mapped[Account] = relationship(back_populates="wallet", init=False)
    entries: Mapped[list["CoinLedgerEntry"]] = relationship(
        back_populates="wallet", cascade="all, delete-orphan", init=False
    )


class CoinLedgerEntry(Base):
    """Append-only, immutable double-entry style ledger row for virtual coins.

    Rows are never updated or deleted by application logic; corrections are
    recorded as new compensating entries.
    """

    __tablename__ = "coin_ledger_entry"
    __table_args__ = (
        UniqueConstraint("idempotency_key", name="uq_coin_ledger_idempotency"),
        CheckConstraint(
            "amount_coins <> 0", name="ck_coin_ledger_amount_nonzero"
        ),
        CheckConstraint(
            "balance_after >= 0", name="ck_coin_ledger_balance_non_negative"
        ),
        CheckConstraint(
            "reason IN " + str(LEDGER_REASON_VALUES),
            name="ck_coin_ledger_reason",
        ),
        Index("ix_coin_ledger_wallet_created", "wallet_id", "created_at"),
    )

    id: Mapped[int] = mapped_column(primary_key=True, init=False)
    wallet_id: Mapped[int] = mapped_column(
        ForeignKey("wallet.id", ondelete="CASCADE"), nullable=False, index=True
    )
    account_id: Mapped[int] = mapped_column(
        ForeignKey("account.id", ondelete="CASCADE"), nullable=False, index=True
    )
    # Positive = credit, negative = debit. Virtual coins only.
    amount_coins: Mapped[int] = mapped_column(BigInteger, nullable=False)
    balance_after: Mapped[int] = mapped_column(BigInteger, nullable=False)
    reason: Mapped[str] = mapped_column(String(32), nullable=False)
    description: Mapped[str] = mapped_column(
        String(255), default="", nullable=False
    )
    related_room_id: Mapped[int | None] = mapped_column(
        ForeignKey("game_room.id", ondelete="SET NULL"),
        default=None,
        nullable=True,
    )
    related_account_id: Mapped[int | None] = mapped_column(
        ForeignKey("account.id", ondelete="SET NULL"),
        default=None,
        nullable=True,
    )
    idempotency_key: Mapped[str | None] = mapped_column(
        String(80), default=None, nullable=True
    )
    created_at: Mapped[dt.datetime] = mapped_column(
        DateTime(timezone=True),
        default=None,
        server_default=func.now(),
        nullable=False,
    )

    wallet: Mapped[Wallet] = relationship(back_populates="entries", init=False)
