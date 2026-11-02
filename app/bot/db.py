"""Persistence layer: users, job history (short-lived), and a tamper-evident
admin audit log (hash-chained, per THREAT_MODEL.md #13)."""

from __future__ import annotations

import hashlib
from datetime import UTC, datetime, timedelta

from sqlalchemy import DateTime, ForeignKey, Integer, String, select
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column

from app.bot.config import settings

JOB_RETENTION_DAYS = 3


class Base(DeclarativeBase):
    pass


class User(Base):
    __tablename__ = "users"

    telegram_id: Mapped[int] = mapped_column(Integer, primary_key=True)
    language: Mapped[str] = mapped_column(String(8), default="uz")
    created_at: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(UTC))


class JobRecord(Base):
    __tablename__ = "jobs"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.telegram_id"))
    job_type: Mapped[str] = mapped_column(String(32))
    status: Mapped[str] = mapped_column(String(16))  # ok | error | timeout
    created_at: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(UTC))


class AdminAuditLog(Base):
    __tablename__ = "admin_audit_log"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    admin_id: Mapped[int] = mapped_column(Integer)
    action: Mapped[str] = mapped_column(String(64))
    target: Mapped[str] = mapped_column(String(256), default="")
    created_at: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(UTC))
    timestamp_str: Mapped[str] = mapped_column(String(64))  # exact string used in the hash
    prev_hash: Mapped[str] = mapped_column(String(64), default="")
    this_hash: Mapped[str] = mapped_column(String(64))


_engine = create_async_engine(settings.database_url, future=True)
_session_factory = async_sessionmaker(_engine, expire_on_commit=False)


async def init_db() -> None:
    async with _engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


def get_session() -> AsyncSession:
    return _session_factory()


async def get_or_create_user(telegram_id: int) -> None:
    async with get_session() as session:
        existing = await session.get(User, telegram_id)
        if existing is None:
            session.add(User(telegram_id=telegram_id))
            await session.commit()


async def record_job(user_id: int, job_type: str, status: str) -> None:
    async with get_session() as session:
        session.add(JobRecord(user_id=user_id, job_type=job_type, status=status))
        await session.commit()


async def prune_expired_jobs() -> int:
    """Data minimization: delete job records older than JOB_RETENTION_DAYS."""
    cutoff = datetime.now(UTC) - timedelta(days=JOB_RETENTION_DAYS)
    async with get_session() as session:
        result = await session.execute(select(JobRecord).where(JobRecord.created_at < cutoff))
        rows = result.scalars().all()
        for row in rows:
            await session.delete(row)
        await session.commit()
        return len(rows)


async def add_audit_log_entry(admin_id: int, action: str, target: str = "") -> None:
    async with get_session() as session:
        result = await session.execute(
            select(AdminAuditLog).order_by(AdminAuditLog.id.desc()).limit(1)
        )
        last = result.scalar_one_or_none()
        prev_hash = last.this_hash if last else ""
        timestamp = datetime.now(UTC).isoformat()
        digest = hashlib.sha256(
            f"{prev_hash}|{admin_id}|{action}|{target}|{timestamp}".encode()
        ).hexdigest()
        session.add(
            AdminAuditLog(
                admin_id=admin_id,
                action=action,
                target=target,
                timestamp_str=timestamp,
                prev_hash=prev_hash,
                this_hash=digest,
            )
        )
        await session.commit()


async def verify_audit_log_integrity() -> bool:
    """Recompute the hash chain and confirm nothing was altered or deleted."""
    async with get_session() as session:
        result = await session.execute(select(AdminAuditLog).order_by(AdminAuditLog.id.asc()))
        entries = result.scalars().all()
        prev_hash = ""
        for entry in entries:
            expected = hashlib.sha256(
                f"{prev_hash}|{entry.admin_id}|{entry.action}|{entry.target}|{entry.timestamp_str}".encode()
            ).hexdigest()
            if entry.prev_hash != prev_hash or entry.this_hash != expected:
                return False
            prev_hash = entry.this_hash
    return True
