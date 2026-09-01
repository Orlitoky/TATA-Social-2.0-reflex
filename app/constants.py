"""Shared frontend vocabularies for the TATA social experience."""

REACTION_CHOICES: list[dict[str, str]] = [
    {"kind": "like", "emoji": "👍", "label": "Like"},
    {"kind": "love", "emoji": "❤️", "label": "Love"},
    {"kind": "haha", "emoji": "😂", "label": "Haha"},
    {"kind": "wow", "emoji": "😮", "label": "Wow"},
    {"kind": "sad", "emoji": "😢", "label": "Sad"},
    {"kind": "angry", "emoji": "😡", "label": "Angry"},
]

PRIVACY_CHOICES: list[dict[str, str]] = [
    {"value": "public", "label": "Public", "icon": "globe"},
    {"value": "friends", "label": "Friends", "icon": "users"},
    {"value": "private", "label": "Only me", "icon": "lock"},
]

STORY_COLORS: list[str] = [
    "#1E9EF5",
    "#22D3EE",
    "#0D1420",
    "#0EA5A5",
    "#2563EB",
]

REACTION_EMOJI: dict[str, str] = {
    "like": "👍",
    "love": "❤️",
    "haha": "😂",
    "wow": "😮",
    "sad": "😢",
    "angry": "😡",
    "fire": "🔥",
}
