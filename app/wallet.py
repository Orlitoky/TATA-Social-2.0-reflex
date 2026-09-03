"""Atomic virtual-coin wallet helpers with an immutable append-only ledger.

TATA Coins are internal points. There is deliberately NO deposit, withdrawal,
purchase, payment or cash-conversion path anywhere in this module.
"""

from __future__ import annotations

from sqlalchemy import text


async def ensure_wallet(asession, account_id: int) -> int:
    row = (
        await asession.execute(
            text("SELECT id FROM wallet WHERE account_id = :a"),
            {"a": account_id},
        )
    ).first()
    if row is not None:
        return int(row[0])
    inserted = (
        await asession.execute(
            text(
                """
                INSERT INTO wallet (account_id, balance_coins,
                    lifetime_earned_coins, lifetime_spent_coins,
                    is_locked, created_at, updated_at)
                VALUES (:a, 0, 0, 0, false, NOW(), NOW())
                RETURNING id
                """
            ),
            {"a": account_id},
        )
    ).first()
    return int(inserted[0])


async def balance_of(asession, account_id: int) -> int:
    row = (
        await asession.execute(
            text(
                "SELECT COALESCE(balance_coins, 0) FROM wallet "
                "WHERE account_id = :a"
            ),
            {"a": account_id},
        )
    ).first()
    return int(row[0]) if row is not None else 0


async def _already_recorded(asession, key: str) -> bool:
    if not key:
        return False
    row = (
        await asession.execute(
            text("SELECT 1 FROM coin_ledger_entry WHERE idempotency_key = :k"),
            {"k": key},
        )
    ).first()
    return row is not None


async def move_coins(
    asession,
    account_id: int,
    amount: int,
    reason: str,
    description: str,
    room_id: int | None = None,
    idempotency_key: str = "",
) -> tuple[bool, str, int]:
    """Debit (amount < 0) or credit (amount > 0) with row locking.

    Returns (ok, message, new_balance). Idempotency keys make settlement and
    payouts safe to retry: a key that already exists can never pay twice.
    """
    if amount == 0:
        return False, "Montant invalide.", 0
    if await _already_recorded(asession, idempotency_key):
        return False, "Deja enregistre.", await balance_of(asession, account_id)

    wallet_id = await ensure_wallet(asession, account_id)
    row = (
        await asession.execute(
            text(
                """
                SELECT balance_coins, lifetime_earned_coins,
                       lifetime_spent_coins, is_locked
                FROM wallet WHERE id = :w FOR UPDATE
                """
            ),
            {"w": wallet_id},
        )
    ).first()
    balance = int(row[0] or 0)
    earned = int(row[1] or 0)
    spent = int(row[2] or 0)
    if bool(row[3]):
        return False, "Portefeuille verrouille.", balance
    if amount < 0 and balance + amount < 0:
        return False, "Solde de points insuffisant.", balance

    new_balance = balance + amount
    if amount > 0:
        earned += amount
    else:
        spent += -amount
    await asession.execute(
        text(
            """
            UPDATE wallet
            SET balance_coins = :b, lifetime_earned_coins = :e,
                lifetime_spent_coins = :s, updated_at = NOW()
            WHERE id = :w
            """
        ),
        {"b": new_balance, "e": earned, "s": spent, "w": wallet_id},
    )
    await asession.execute(
        text(
            """
            INSERT INTO coin_ledger_entry
                (wallet_id, account_id, amount_coins, balance_after, reason,
                 description, related_room_id, idempotency_key, created_at)
            VALUES (:w, :a, :amount, :balance, :reason, :description,
                    :room, :key, NOW())
            """
        ),
        {
            "w": wallet_id,
            "a": account_id,
            "amount": amount,
            "balance": new_balance,
            "reason": reason,
            "description": description[:255],
            "room": room_id,
            "key": idempotency_key or None,
        },
    )
    return True, "", new_balance
