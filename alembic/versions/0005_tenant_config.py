"""Add persistent tenant configuration tables."""

from __future__ import annotations

import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

from alembic import op

revision = "0005_tenant_config"
down_revision = "0004_rls_policies"
branch_labels = None
depends_on = None

TENANT_CONFIG_TABLES = (
    "tenant_config",
    "tenant_config_audit",
)

UPGRADE_RLS_STATEMENTS = (
    sa.text("ALTER TABLE tenant_config ENABLE ROW LEVEL SECURITY"),
    sa.text("ALTER TABLE tenant_config FORCE ROW LEVEL SECURITY"),
    sa.text(
        "CREATE POLICY tenant_isolation ON tenant_config "
        "USING (tenant_id = NULLIF(current_setting('app.tenant_id', true), '')::uuid) "
        "WITH CHECK (tenant_id = NULLIF(current_setting('app.tenant_id', true), '')::uuid)"
    ),
    sa.text("ALTER TABLE tenant_config_audit ENABLE ROW LEVEL SECURITY"),
    sa.text("ALTER TABLE tenant_config_audit FORCE ROW LEVEL SECURITY"),
    sa.text(
        "CREATE POLICY tenant_isolation ON tenant_config_audit "
        "USING (tenant_id = NULLIF(current_setting('app.tenant_id', true), '')::uuid) "
        "WITH CHECK (tenant_id = NULLIF(current_setting('app.tenant_id', true), '')::uuid)"
    ),
)

DOWNGRADE_RLS_STATEMENTS = (
    sa.text("DROP POLICY IF EXISTS tenant_isolation ON tenant_config_audit"),
    sa.text("ALTER TABLE tenant_config_audit NO FORCE ROW LEVEL SECURITY"),
    sa.text("ALTER TABLE tenant_config_audit DISABLE ROW LEVEL SECURITY"),
    sa.text("DROP POLICY IF EXISTS tenant_isolation ON tenant_config"),
    sa.text("ALTER TABLE tenant_config NO FORCE ROW LEVEL SECURITY"),
    sa.text("ALTER TABLE tenant_config DISABLE ROW LEVEL SECURITY"),
)


def upgrade() -> None:
    op.create_table(
        "tenant_config",
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
        sa.Column("version", sa.Integer(), nullable=False),
        sa.Column("config", postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column(
            "updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False
        ),
        sa.ForeignKeyConstraint(
            ["tenant_id"],
            ["tenant.id"],
            name="fk_tenant_config_tenant_id_tenant",
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("id", name="pk_tenant_config"),
        sa.UniqueConstraint("tenant_id", name="uq_tenant_config_tenant_id"),
    )
    op.create_index("ix_tenant_config_tenant_id", "tenant_config", ["tenant_id"])
    op.create_index(
        "ix_tenant_config_tenant_version",
        "tenant_config",
        ["tenant_id", "version"],
    )
    op.create_table(
        "tenant_config_audit",
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
        sa.Column("config_version", sa.Integer(), nullable=False),
        sa.Column("actor_id", sa.String(length=120), nullable=False),
        sa.Column("actor_role", sa.String(length=64), nullable=False),
        sa.Column("changed_fields", postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column("approval_id", sa.String(length=120), nullable=True),
        sa.Column("event_metadata", postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.ForeignKeyConstraint(
            ["tenant_id"],
            ["tenant.id"],
            name="fk_tenant_config_audit_tenant_id_tenant",
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("id", name="pk_tenant_config_audit"),
        sa.UniqueConstraint(
            "tenant_id",
            "config_version",
            name="uq_tenant_config_audit_tenant_config_version",
        ),
    )
    op.create_index("ix_tenant_config_audit_tenant_id", "tenant_config_audit", ["tenant_id"])
    op.create_index(
        "ix_tenant_config_audit_tenant_created",
        "tenant_config_audit",
        ["tenant_id", "created_at"],
    )
    for statement in UPGRADE_RLS_STATEMENTS:
        op.execute(statement)


def downgrade() -> None:
    for statement in DOWNGRADE_RLS_STATEMENTS:
        op.execute(statement)
    op.drop_index("ix_tenant_config_audit_tenant_created", table_name="tenant_config_audit")
    op.drop_index("ix_tenant_config_audit_tenant_id", table_name="tenant_config_audit")
    op.drop_table("tenant_config_audit")
    op.drop_index("ix_tenant_config_tenant_version", table_name="tenant_config")
    op.drop_index("ix_tenant_config_tenant_id", table_name="tenant_config")
    op.drop_table("tenant_config")
