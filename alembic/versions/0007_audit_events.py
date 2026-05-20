"""Add canonical audit event store."""

from __future__ import annotations

import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

from alembic import op

revision = "0007_audit_events"
down_revision = "0006_usage_ledger"
branch_labels = None
depends_on = None

AUDIT_EVENT_TABLES = ("audit_log_event",)

UPGRADE_RLS_STATEMENTS = (
    sa.text("ALTER TABLE audit_log_event ENABLE ROW LEVEL SECURITY"),
    sa.text("ALTER TABLE audit_log_event FORCE ROW LEVEL SECURITY"),
    sa.text(
        "CREATE POLICY tenant_isolation ON audit_log_event "
        "USING (tenant_id = NULLIF(current_setting('app.tenant_id', true), '')::uuid) "
        "WITH CHECK (tenant_id = NULLIF(current_setting('app.tenant_id', true), '')::uuid)"
    ),
)

DOWNGRADE_RLS_STATEMENTS = (
    sa.text("DROP POLICY IF EXISTS tenant_isolation ON audit_log_event"),
    sa.text("ALTER TABLE audit_log_event NO FORCE ROW LEVEL SECURITY"),
    sa.text("ALTER TABLE audit_log_event DISABLE ROW LEVEL SECURITY"),
)


def upgrade() -> None:
    op.create_table(
        "audit_log_event",
        sa.Column("tenant_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column(
            "id",
            postgresql.UUID(as_uuid=True),
            server_default=sa.text("gen_random_uuid()"),
            nullable=False,
        ),
        sa.Column(
            "created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False
        ),
        sa.Column("actor_ref", sa.String(length=160), nullable=False),
        sa.Column("action", sa.String(length=120), nullable=False),
        sa.Column("resource_type", sa.String(length=120), nullable=False),
        sa.Column("resource_id", sa.String(length=160), nullable=False),
        sa.Column("result", sa.String(length=64), nullable=False),
        sa.Column("policy_version", sa.String(length=64), nullable=False),
        sa.Column("payload", postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.ForeignKeyConstraint(
            ["tenant_id"],
            ["tenant.id"],
            name="fk_audit_log_event_tenant_id_tenant",
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("id", name="pk_audit_log_event"),
    )
    op.create_index("ix_audit_log_event_tenant_id", "audit_log_event", ["tenant_id"])
    op.create_index(
        "ix_audit_log_event_tenant_created",
        "audit_log_event",
        ["tenant_id", "created_at"],
    )
    op.create_index(
        "ix_audit_log_event_tenant_action",
        "audit_log_event",
        ["tenant_id", "action"],
    )
    for statement in UPGRADE_RLS_STATEMENTS:
        op.execute(statement)


def downgrade() -> None:
    for statement in DOWNGRADE_RLS_STATEMENTS:
        op.execute(statement)
    op.drop_index("ix_audit_log_event_tenant_action", table_name="audit_log_event")
    op.drop_index("ix_audit_log_event_tenant_created", table_name="audit_log_event")
    op.drop_index("ix_audit_log_event_tenant_id", table_name="audit_log_event")
    op.drop_table("audit_log_event")
