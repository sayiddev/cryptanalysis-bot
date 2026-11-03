import pytest

from app.bot import db


@pytest.fixture(autouse=True)
async def _init_db():
    await db.init_db()


async def test_get_or_create_user_is_idempotent():
    await db.get_or_create_user(555)
    await db.get_or_create_user(555)  # should not raise / duplicate
    async with db.get_session() as session:
        user = await session.get(db.User, 555)
        assert user is not None


async def test_get_recent_jobs_returns_newest_first():
    await db.get_or_create_user(777)
    await db.record_job(777, "chain", "ok")
    await db.record_job(777, "xor", "error")

    jobs = await db.get_recent_jobs(777, limit=10)
    assert len(jobs) == 2
    assert jobs[0][0] == "xor"  # most recent first
    assert jobs[1][0] == "chain"


async def test_record_job_and_prune_expired(monkeypatch):
    await db.get_or_create_user(555)
    await db.record_job(555, "chain", "ok")

    # Nothing should be pruned yet (job is brand new).
    pruned = await db.prune_expired_jobs()
    assert pruned == 0


async def test_audit_log_hash_chain_detects_tampering():
    await db.add_audit_log_entry(111, "ban_user", "target-123")
    await db.add_audit_log_entry(111, "unban_user", "target-123")

    assert await db.verify_audit_log_integrity() is True

    # Tamper with an entry directly and confirm verification now fails.
    async with db.get_session() as session:
        from sqlalchemy import select

        result = await session.execute(select(db.AdminAuditLog).order_by(db.AdminAuditLog.id.asc()))
        first_entry = result.scalars().first()
        first_entry.action = "tampered_action"
        await session.commit()

    assert await db.verify_audit_log_integrity() is False
