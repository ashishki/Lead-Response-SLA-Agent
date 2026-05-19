"""Initial database model declarations."""

from __future__ import annotations

import uuid
from datetime import datetime
from typing import Any

from sqlalchemy import DateTime, ForeignKey, Index, String, UniqueConstraint, func
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column

from lead_sla_agent.db.base import Base, CreatedAtMixin, UUIDPrimaryKeyMixin


class Tenant(UUIDPrimaryKeyMixin, CreatedAtMixin, Base):
    __tablename__ = "tenant"

    name: Mapped[str] = mapped_column(String(255), nullable=False)
    slug: Mapped[str] = mapped_column(String(120), nullable=False, unique=True)
    status: Mapped[str] = mapped_column(String(32), nullable=False, default="active")


class TenantScopedMixin:
    tenant_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("tenant.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )


class Lead(TenantScopedMixin, UUIDPrimaryKeyMixin, CreatedAtMixin, Base):
    __tablename__ = "lead"

    source_channel: Mapped[str] = mapped_column(String(32), nullable=False)
    status: Mapped[str] = mapped_column(String(32), nullable=False, default="new")
    contact_name: Mapped[str | None] = mapped_column(String(255))
    contact_email: Mapped[str | None] = mapped_column(String(320))
    contact_phone: Mapped[str | None] = mapped_column(String(64))


class Conversation(TenantScopedMixin, UUIDPrimaryKeyMixin, CreatedAtMixin, Base):
    __tablename__ = "conversation"

    lead_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("lead.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    status: Mapped[str] = mapped_column(String(32), nullable=False, default="open")


class Message(TenantScopedMixin, UUIDPrimaryKeyMixin, CreatedAtMixin, Base):
    __tablename__ = "message"

    conversation_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("conversation.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    role: Mapped[str] = mapped_column(String(32), nullable=False)
    channel: Mapped[str] = mapped_column(String(32), nullable=False)
    provider_message_id: Mapped[str | None] = mapped_column(String(255))
    content_hash: Mapped[str] = mapped_column(String(64), nullable=False)
    redacted_preview: Mapped[str] = mapped_column(String(280), nullable=False)


class AuditEvent(TenantScopedMixin, UUIDPrimaryKeyMixin, CreatedAtMixin, Base):
    __tablename__ = "audit_event"

    event_type: Mapped[str] = mapped_column(String(120), nullable=False)
    actor_type: Mapped[str] = mapped_column(String(64), nullable=False)
    event_metadata: Mapped[dict[str, Any]] = mapped_column(JSONB, nullable=False, default=dict)


class ProviderEvent(TenantScopedMixin, UUIDPrimaryKeyMixin, CreatedAtMixin, Base):
    __tablename__ = "provider_event"
    __table_args__ = (
        UniqueConstraint("tenant_id", "source_event_id", name="uq_provider_event_tenant_source"),
        Index("ix_provider_event_tenant_received_at", "tenant_id", "received_at"),
    )

    source_event_id: Mapped[str] = mapped_column(String(255), nullable=False)
    channel: Mapped[str] = mapped_column(String(32), nullable=False)
    payload_hash: Mapped[str] = mapped_column(String(64), nullable=False)
    received_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
    )
