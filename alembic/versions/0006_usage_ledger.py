"""Add persistent usage ledger."""

from __future__ import annotations

import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

from alembic import op

revision = "0006_usage_ledger"
down_revision = "0005_tenant_config"
branch_labels = None
depends_on = None

USAGE_LEDGER_TABLES = ("usage_ledger_event",)

UPGRADE_RLS_STATEMENTS = (
    sa.text("ALTER TABLE usage_ledger_event ENABLE ROW LEVEL SECURITY"),
    sa.text("ALTER TABLE usage_ledger_event FORCE ROW LEVEL SECURITY"),
    sa.text(
        "CREATE POLICY tenant_isolation ON usage_ledger_event "
        "USING (tenant_id = NULLIF(current_setting('app.tenant_id', true), '')::uuid) "
        "WITH CHECK (tenant_id = NULLIF(current_setting('app.tenant_id', true), '')::uuid)"
    ),
)

DOWNGRADE_RLS_STATEMENTS = (
    sa.text("DROP POLICY IF EXISTS tenant_isolation ON usage_ledger_event"),
    sa.text("ALTER TABLE usage_ledger_event NO FORCE ROW LEVEL SECURITY"),
    sa.text("ALTER TABLE usage_ledger_event DISABLE ROW LEVEL SECURITY"),
)


def upgrade() -> None:
    op.create_table(
        "usage_ledger_event",
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
        sa.Column("event_id", sa.String(length=120), nullable=False),
        sa.Column("event_type", sa.String(length=64), nullable=False),
        sa.Column("occurred_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("quantity", sa.Integer(), nullable=False),
        sa.Column("metadata", postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column("pricing_mapping_version", sa.String(length=64), nullable=False),
        sa.ForeignKeyConstraint(
            ["tenant_id"],
            ["tenant.id"],
            name="fk_usage_ledger_event_tenant_id_tenant",
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("id", name="pk_usage_ledger_event"),
        sa.UniqueConstraint(
            "tenant_id",
            "event_id",
            name="uq_usage_ledger_event_tenant_event_id",
        ),
    )
    op.create_index("ix_usage_ledger_event_tenant_id", "usage_ledger_event", ["tenant_id"])
    op.create_index(
        "ix_usage_ledger_event_tenant_occurred",
        "usage_ledger_event",
        ["tenant_id", "occurred_at"],
    )
    for statement in UPGRADE_RLS_STATEMENTS:
        op.execute(statement)


def downgrade() -> None:
    for statement in DOWNGRADE_RLS_STATEMENTS:
        op.execute(statement)
    op.drop_index("ix_usage_ledger_event_tenant_occurred", table_name="usage_ledger_event")
    op.drop_index("ix_usage_ledger_event_tenant_id", table_name="usage_ledger_event")
    op.drop_table("usage_ledger_event")
