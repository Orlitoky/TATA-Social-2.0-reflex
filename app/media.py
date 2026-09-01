"""Upload storage, MIME/size validation and display helpers."""

from __future__ import annotations

import datetime as dt
import secrets
from pathlib import Path

import reflex as rx

IMAGE_TYPES: dict[str, str] = {
    "image/png": ".png",
    "image/jpeg": ".jpg",
    "image/jpg": ".jpg",
    "image/webp": ".webp",
    "image/gif": ".gif",
}
VIDEO_TYPES: dict[str, str] = {
    "video/mp4": ".mp4",
    "video/webm": ".webm",
    "video/quicktime": ".mov",
}
MAX_IMAGE_BYTES = 8 * 1024 * 1024
MAX_VIDEO_BYTES = 64 * 1024 * 1024


class UploadError(ValueError):
    """Raised when an upload fails MIME or size validation."""


def _extension_kind(name: str) -> tuple[str, str, str]:
    suffix = Path(name).suffix.lower()
    for mime, ext in IMAGE_TYPES.items():
        if suffix == ext:
            return "image", mime, ext
    for mime, ext in VIDEO_TYPES.items():
        if suffix == ext:
            return "video", mime, ext
    raise UploadError(
        "Unsupported file type. Use PNG, JPG, WEBP, GIF, MP4 or WEBM."
    )


async def store_upload(file: rx.UploadFile) -> dict[str, str | int]:
    """Validate and persist an upload under a generated storage name."""
    original_name = Path(file.name or "upload").name
    mime = (file.content_type or "").lower()
    if mime in IMAGE_TYPES:
        kind, extension = "image", IMAGE_TYPES[mime]
    elif mime in VIDEO_TYPES:
        kind, extension = "video", VIDEO_TYPES[mime]
    else:
        kind, mime, extension = _extension_kind(original_name)

    data = await file.read()
    limit = MAX_IMAGE_BYTES if kind == "image" else MAX_VIDEO_BYTES
    if len(data) == 0:
        raise UploadError("The selected file is empty.")
    if len(data) > limit:
        raise UploadError(
            f"{original_name} is too large (max {limit // (1024 * 1024)} MB)."
        )

    storage_key = (
        f"{dt.datetime.now(dt.UTC):%Y%m%d}_{secrets.token_hex(12)}{extension}"
    )
    upload_dir = rx.get_upload_dir()
    upload_dir.mkdir(parents=True, exist_ok=True)
    with (upload_dir / storage_key).open("wb") as handle:
        handle.write(data)

    return {
        "kind": kind,
        "storage_key": storage_key,
        "original_name": original_name[:255],
        "mime_type": mime[:128],
        "size_bytes": len(data),
    }


def avatar_source(avatar_key: str, seed: str) -> tuple[str, bool]:
    """Return (url_or_key, is_remote) for an avatar."""
    if avatar_key.startswith("http"):
        return avatar_key, True
    if avatar_key:
        return avatar_key, False
    return (
        f"https://api.dicebear.com/9.x/notionists/svg?seed={seed or 'tata'}",
        True,
    )


def media_source(storage_key: str) -> tuple[str, bool]:
    if storage_key.startswith("http"):
        return storage_key, True
    return storage_key, False


def relative_time(moment: dt.datetime | None) -> str:
    if moment is None:
        return ""
    if moment.tzinfo is None:
        moment = moment.replace(tzinfo=dt.UTC)
    delta = dt.datetime.now(dt.UTC) - moment
    seconds = int(delta.total_seconds())
    if seconds < 60:
        return "just now"
    if seconds < 3600:
        return f"{seconds // 60}m ago"
    if seconds < 86400:
        return f"{seconds // 3600}h ago"
    if seconds < 604800:
        return f"{seconds // 86400}d ago"
    return moment.strftime("%b %d, %Y")
