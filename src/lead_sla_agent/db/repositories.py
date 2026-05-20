"""Repository helpers that enforce tenant context for tenant-scoped reads."""

from __future__ import annotations

import time
import uuid
from typing import Any

from sqlalchemy import Select, select
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession

from lead_sla_agent.db.audit import AuditEventRepository
from lead_sla_agent.db.lead_repository import LeadRepository as PersistentLeadRepository
from lead_sla_agent.db.lead_repository import RepositoryPersistenceError
from lead_sla_agent.db.models import Conversation, Lead, ProviderEvent
from lead_sla_agent.db.tenant import apply_tenant_context
from lead_sla_agent.db.transcript_repository import TranscriptRepository
from lead_sla_agent.intake.lead_service import LeadService
from lead_sla_agent.intake.schemas import NormalizedInboundEvent, StoredWebhookResult
from lead_sla_agent.observability.metrics import metrics
from lead_sla_agent.observability.tracing import get_tracer


class TenantScopedRepository:
    """Base repository for tenant-scoped queries."""

    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def _execute_tenant_scoped(self, tenant_id: uuid.UUID, statement: Select[Any]) -> Any:
        if tenant_id is None:
            raise ValueError("tenant_id is required")

        await apply_tenant_context(self.session, tenant_id)
        return await self.session.execute(statement)


class LeadRepository(TenantScopedRepository):
    """Read helpers for lead and conversation state."""

    async def get_lead(self, tenant_id: uuid.UUID, lead_id: uuid.UUID) -> Lead | None:
        statement = select(Lead).where(Lead.tenant_id == tenant_id, Lead.id == lead_id)
        result = await self._execute_tenant_scoped(tenant_id, statement)
        return result.scalar_one_or_none()

    async def list_conversations_for_lead(
        self,
        tenant_id: uuid.UUID,
        lead_id: uuid.UUID,
    ) -> list[Conversation]:
        statement = select(Conversation).where(
            Conversation.tenant_id == tenant_id,
            Conversation.lead_id == lead_id,
        )
        result = await self._execute_tenant_scoped(tenant_id, statement)
        return list(result.scalars().all())


class ProviderEventRepository(TenantScopedRepository):
    """Read helpers for provider event idempotency checks."""

    async def get_by_source_event_id(
        self,
        tenant_id: uuid.UUID,
        source_event_id: str,
    ) -> ProviderEvent | None:
        statement = select(ProviderEvent).where(
            ProviderEvent.tenant_id == tenant_id,
            ProviderEvent.source_event_id == source_event_id,
        )
        result = await self._execute_tenant_scoped(tenant_id, statement)
        return result.scalar_one_or_none()


class PersistentWebhookStore:
    """Transactional PostgreSQL-backed webhook intake store."""

    def __init__(
        self,
        session: AsyncSession,
        lead_repository_type: type[PersistentLeadRepository] = PersistentLeadRepository,
        transcript_repository_type: type[TranscriptRepository] = TranscriptRepository,
        audit_repository_type: type[AuditEventRepository] = AuditEventRepository,
    ) -> None:
        self.session = session
        self.lead_repository_type = lead_repository_type
        self.transcript_repository_type = transcript_repository_type
        self.audit_repository_type = audit_repository_type
        self.tracer = get_tracer(__name__)

    async def accept_event(self, event: NormalizedInboundEvent) -> StoredWebhookResult:
        started_at = time.perf_counter()
        try:
            async with self.session.begin():
                with self.tracer.start_as_current_span("db.webhook.accept_event"):
                    await apply_tenant_context(self.session, event.tenant_id)
                    existing = await self._get_existing_event(event)
                    if existing is not None:
                        return StoredWebhookResult(
                            provider_event_id=existing.id,
                            lead_id=existing.lead_id,
                            conversation_id=existing.conversation_id,
                            replayed=True,
                        )

                    lead_service = LeadService(
                        self.lead_repository_type(self.session),
                        self.transcript_repository_type(self.session),
                    )
                    created = await lead_service.create_from_normalized_event(
                        event,
                        provider_message_id=event.source_event_id,
                    )
                    provider_event = ProviderEvent(
                        tenant_id=event.tenant_id,
                        source_event_id=event.source_event_id,
                        channel=event.channel,
                        payload_hash=event.payload_hash,
                        received_at=event.received_at,
                        lead_id=created.lead.id,
                        conversation_id=created.conversation.id,
                    )
                    self.session.add(provider_event)
                    await _safe_flush(self.session)
                    await self.audit_repository_type(self.session).append(
                        tenant_id=event.tenant_id,
                        event_type="webhook.accepted",
                        actor_type="provider",
                        event_metadata={
                            "provider_event_id": str(provider_event.id),
                            "lead_id": str(created.lead.id),
                            "conversation_id": str(created.conversation.id),
                            "payload_hash": event.payload_hash,
                        },
                    )
                    return StoredWebhookResult(
                        provider_event_id=provider_event.id,
                        lead_id=created.lead.id,
                        conversation_id=created.conversation.id,
                        replayed=False,
                    )
        finally:
            metrics.observe("intake_latency_ms", (time.perf_counter() - started_at) * 1000)

    async def _get_existing_event(self, event: NormalizedInboundEvent) -> ProviderEvent | None:
        statement = select(ProviderEvent).where(
            ProviderEvent.tenant_id == event.tenant_id,
            ProviderEvent.source_event_id == event.source_event_id,
        )
        result = await self.session.execute(statement)
        return result.scalar_one_or_none()


async def _safe_flush(session: AsyncSession) -> None:
    try:
        await session.flush()
    except SQLAlchemyError:
        raise RepositoryPersistenceError("repository persistence failed") from None
