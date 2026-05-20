"""Link provider events to created lead and conversation rows."""

from __future__ import annotations

import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

from alembic import op

revision = "0003_provider_event_lead_links"
down_revision = "0002_review_outcome_repositories"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(
        "provider_event",
        sa.Column("lead_id", postgresql.UUID(as_uuid=True), nullable=False),
    )
    op.add_column(
        "provider_event",
        sa.Column("conversation_id", postgresql.UUID(as_uuid=True), nullable=False),
    )
    op.create_foreign_key(
        "fk_provider_event_lead_id_lead",
        "provider_event",
        "lead",
        ["lead_id"],
        ["id"],
        ondelete="CASCADE",
    )
    op.create_foreign_key(
        "fk_provider_event_conversation_id_conversation",
        "provider_event",
        "conversation",
        ["conversation_id"],
        ["id"],
        ondelete="CASCADE",
    )
    op.create_index("ix_provider_event_lead_id", "provider_event", ["lead_id"])
    op.create_index("ix_provider_event_conversation_id", "provider_event", ["conversation_id"])


def downgrade() -> None:
    op.drop_index("ix_provider_event_conversation_id", table_name="provider_event")
    op.drop_index("ix_provider_event_lead_id", table_name="provider_event")
    op.drop_constraint(
        "fk_provider_event_conversation_id_conversation",
        "provider_event",
        type_="foreignkey",
    )
    op.drop_constraint("fk_provider_event_lead_id_lead", "provider_event", type_="foreignkey")
    op.drop_column("provider_event", "conversation_id")
    op.drop_column("provider_event", "lead_id")
