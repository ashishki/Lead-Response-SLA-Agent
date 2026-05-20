"""Initial database model declarations."""

from __future__ import annotations

import uuid
from datetime import date, datetime
from typing import Any

from sqlalchemy import Date, DateTime, ForeignKey, Index, String, UniqueConstraint, func
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
    lead_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("lead.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    conversation_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("conversation.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    received_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
    )


class HumanReviewTask(TenantScopedMixin, UUIDPrimaryKeyMixin, CreatedAtMixin, Base):
    __tablename__ = "human_review_task"
    __table_args__ = (
        Index("ix_human_review_task_tenant_status", "tenant_id", "status"),
        Index("ix_human_review_task_tenant_created", "tenant_id", "created_at"),
    )

    conversation_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("conversation.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    handoff_reason: Mapped[str] = mapped_column(String(120), nullable=False)
    status: Mapped[str] = mapped_column(String(32), nullable=False, default="open")
    payload: Mapped[dict[str, Any]] = mapped_column(JSONB, nullable=False, default=dict)


class HumanReviewApproval(TenantScopedMixin, UUIDPrimaryKeyMixin, CreatedAtMixin, Base):
    __tablename__ = "human_review_approval"

    review_task_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("human_review_task.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    actor_id: Mapped[str] = mapped_column(String(120), nullable=False)
    approved_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    original_draft_hash: Mapped[str] = mapped_column(String(64), nullable=False)
    final_message_hash: Mapped[str] = mapped_column(String(64), nullable=False)
    reason_code: Mapped[str] = mapped_column(String(120), nullable=False)
    send_status: Mapped[str] = mapped_column(String(32), nullable=False)


class OutcomeLabel(TenantScopedMixin, UUIDPrimaryKeyMixin, CreatedAtMixin, Base):
    __tablename__ = "outcome_label"
    __table_args__ = (Index("ix_outcome_label_tenant_labeled_on", "tenant_id", "labeled_on"),)

    lead_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("lead.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    label: Mapped[str] = mapped_column(String(64), nullable=False)
    labeled_on: Mapped[date] = mapped_column(Date, nullable=False)
