"""Idempotent demo network seeding.

Runs once (when only the very first real account exists) so a brand new
signup immediately lands in a dense, realistic feed. Everything written here
is real database state that the UI then queries and mutates.
"""

from __future__ import annotations

import datetime as dt
import random

from faker import Faker
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import (
    Account,
    Comment,
    Follow,
    Friendship,
    Post,
    PostMedia,
    PostReaction,
    Preference,
    Profile,
    Story,
    StoryMedia,
    Wallet,
)
from app.security import hash_password

fake = Faker()

CAPTIONS = [
    "Golden hour on the rooftop. This city never stops surprising me.",
    "Six months of training and the half marathon is finally done. 1:52:11 🏃",
    "New studio setup is live. Analog warmth, digital speed.",
    "Sunday market haul: figs, sourdough and way too much coffee.",
    "Shipped the redesign today. Small team, big week.",
    "Sunrise swim before the office. Cold water, clear head.",
    "Found this tiny bookshop behind the station. Stayed two hours.",
    "Homemade ramen attempt #7. We are getting closer.",
    "Late night sketching session. Ink everywhere, zero regrets.",
    "Trail was muddy, views were worth it. 14km round trip.",
    "First tomatoes from the balcony garden 🍅",
    "Studio playlist of the week is up. Mostly ambient, mostly loops.",
]
COMMENTS = [
    "This is unreal, where was it taken?",
    "Congratulations! Huge milestone.",
    "Okay this is inspiring me to finally start.",
    "The colours here are perfect.",
    "Saving this for later, thanks for sharing!",
    "Need the recipe immediately.",
    "Been waiting for this update all week.",
    "Adding this to my weekend list.",
]
REACTIONS = ["like", "love", "haha", "wow", "sad", "angry"]


def _photo(seed: str, width: int = 900, height: int = 700) -> str:
    return f"https://picsum.photos/seed/{seed}/{width}/{height}"


async def needs_seed(asession: AsyncSession) -> bool:
    total = await asession.scalar(select(func.count()).select_from(Account))
    return (total or 0) <= 1


async def seed_demo_network(asession: AsyncSession, me_id: int) -> None:
    """Create demo people, friendships, posts, comments, reactions, stories."""
    now = dt.datetime.now(dt.UTC)
    demo_password = hash_password("TataDemo2024")
    demo_ids: list[int] = []

    for index in range(8):
        first = fake.first_name()
        last = fake.last_name()
        username = f"{first.lower()}.{last.lower()}{index}"[:24]
        account = Account(
            email=f"{username}@tata.demo",
            email_normalized=f"{username}@tata.demo",
            username=username,
            username_normalized=username,
            password_hash=demo_password,
            status="active",
            email_verified=True,
            is_online=index % 3 != 0,
            last_seen_at=now - dt.timedelta(minutes=random.randint(1, 900)),
            created_at=now - dt.timedelta(days=random.randint(40, 400)),
            updated_at=now,
        )
        asession.add(account)
        await asession.flush()
        demo_ids.append(account.id)

        asession.add(
            Profile(
                account_id=account.id,
                display_name=f"{first} {last}",
                bio=fake.sentence(nb_words=12),
                location=f"{fake.city()}, {fake.country()}",
                website="",
                avatar_key=(
                    "https://api.dicebear.com/9.x/notionists/svg?seed="
                    f"{username}"
                ),
                cover_key=_photo(f"cover{username}", 1200, 400),
                created_at=now,
                updated_at=now,
            )
        )
        asession.add(
            Preference(account_id=account.id, created_at=now, updated_at=now)
        )
        wallet = Wallet(
            account_id=account.id,
            balance_coins=random.randint(120, 4200),
            lifetime_earned_coins=random.randint(500, 8000),
            created_at=now,
            updated_at=now,
        )
        asession.add(wallet)

    await asession.flush()

    # Social graph with the new account.
    for demo_id in demo_ids[:5]:
        low, high = min(me_id, demo_id), max(me_id, demo_id)
        asession.add(
            Friendship(
                account_low_id=low,
                account_high_id=high,
                created_at=now - dt.timedelta(days=random.randint(1, 90)),
            )
        )
    for demo_id in demo_ids:
        asession.add(
            Follow(
                follower_id=demo_id,
                followee_id=me_id,
                created_at=now - dt.timedelta(hours=random.randint(1, 200)),
            )
        )
        asession.add(
            Follow(
                follower_id=me_id,
                followee_id=demo_id,
                created_at=now - dt.timedelta(hours=random.randint(1, 200)),
            )
        )
    await asession.flush()

    # Posts + media + comments + reactions.
    for index, caption in enumerate(CAPTIONS):
        author_id = demo_ids[index % len(demo_ids)]
        created = now - dt.timedelta(hours=index * 5 + random.randint(1, 4))
        post = Post(
            author_id=author_id,
            body=caption,
            privacy="friends" if index % 5 == 4 else "public",
            location=fake.city() if index % 3 == 0 else "",
            created_at=created,
            updated_at=created,
        )
        asession.add(post)
        await asession.flush()

        media_count = (0, 1, 2, 3)[index % 4]
        for position in range(media_count):
            asession.add(
                PostMedia(
                    post_id=post.id,
                    kind="image",
                    storage_key=_photo(f"post{post.id}-{position}"),
                    original_name=f"photo_{position}.jpg",
                    mime_type="image/jpeg",
                    size_bytes=random.randint(180_000, 2_400_000),
                    position=position,
                    created_at=created,
                )
            )

        reactors = random.sample(demo_ids, k=random.randint(2, 6))
        for reactor in reactors:
            asession.add(
                PostReaction(
                    post_id=post.id,
                    account_id=reactor,
                    kind=random.choice(REACTIONS),
                    created_at=created + dt.timedelta(minutes=5),
                    updated_at=created + dt.timedelta(minutes=5),
                )
            )
        post.reaction_count = len(reactors)

        comment_total = 0
        for c_index in range(random.randint(1, 3)):
            c_created = created + dt.timedelta(minutes=15 * (c_index + 1))
            comment = Comment(
                post_id=post.id,
                author_id=random.choice(demo_ids),
                body=random.choice(COMMENTS),
                created_at=c_created,
                updated_at=c_created,
            )
            asession.add(comment)
            await asession.flush()
            comment_total += 1
            if c_index == 0:
                reply = Comment(
                    post_id=post.id,
                    author_id=author_id,
                    parent_id=comment.id,
                    depth=1,
                    body="Thank you! More coming soon.",
                    created_at=c_created + dt.timedelta(minutes=6),
                    updated_at=c_created + dt.timedelta(minutes=6),
                )
                asession.add(reply)
                comment.reply_count = 1
                comment_total += 1
        post.comment_count = comment_total

    # Live stories (all inside the 24h window).
    for index, demo_id in enumerate(demo_ids[:6]):
        created = now - dt.timedelta(hours=index * 3 + 1)
        story = Story(
            author_id=demo_id,
            caption=fake.sentence(nb_words=7),
            background_color="" if index % 2 == 0 else "#1E9EF5",
            privacy="public",
            expires_at=created + dt.timedelta(hours=24),
            view_count=random.randint(4, 90),
            created_at=created,
            updated_at=created,
        )
        asession.add(story)
        await asession.flush()
        if index % 2 == 0:
            asession.add(
                StoryMedia(
                    story_id=story.id,
                    kind="image",
                    storage_key=_photo(f"story{story.id}", 720, 1280),
                    original_name="story.jpg",
                    mime_type="image/jpeg",
                    size_bytes=random.randint(200_000, 1_800_000),
                    created_at=created,
                )
            )
    await asession.flush()
