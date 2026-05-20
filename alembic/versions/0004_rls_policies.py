"""Add row-level security policies for tenant-scoped tables."""

from __future__ import annotations

import sqlalchemy as sa

from alembic import op

revision = "0004_rls_policies"
down_revision = "0003_provider_event_lead_links"
branch_labels = None
depends_on = None

TENANT_TABLES = (
    "lead",
    "conversation",
    "message",
    "audit_event",
    "provider_event",
    "human_review_task",
    "human_review_approval",
    "outcome_label",
)

TENANT_POLICY_EXPR = "tenant_id = NULLIF(current_setting('app.tenant_id', true), '')::uuid"

UPGRADE_STATEMENTS = (
    sa.text("ALTER TABLE lead ENABLE ROW LEVEL SECURITY"),
    sa.text("ALTER TABLE lead FORCE ROW LEVEL SECURITY"),
    sa.text(
        "CREATE POLICY tenant_isolation ON lead "
        "USING (tenant_id = NULLIF(current_setting('app.tenant_id', true), '')::uuid) "
        "WITH CHECK (tenant_id = NULLIF(current_setting('app.tenant_id', true), '')::uuid)"
    ),
    sa.text("ALTER TABLE conversation ENABLE ROW LEVEL SECURITY"),
    sa.text("ALTER TABLE conversation FORCE ROW LEVEL SECURITY"),
    sa.text(
        "CREATE POLICY tenant_isolation ON conversation "
        "USING (tenant_id = NULLIF(current_setting('app.tenant_id', true), '')::uuid) "
        "WITH CHECK (tenant_id = NULLIF(current_setting('app.tenant_id', true), '')::uuid)"
    ),
    sa.text("ALTER TABLE message ENABLE ROW LEVEL SECURITY"),
    sa.text("ALTER TABLE message FORCE ROW LEVEL SECURITY"),
    sa.text(
        "CREATE POLICY tenant_isolation ON message "
        "USING (tenant_id = NULLIF(current_setting('app.tenant_id', true), '')::uuid) "
        "WITH CHECK (tenant_id = NULLIF(current_setting('app.tenant_id', true), '')::uuid)"
    ),
    sa.text("ALTER TABLE audit_event ENABLE ROW LEVEL SECURITY"),
    sa.text("ALTER TABLE audit_event FORCE ROW LEVEL SECURITY"),
    sa.text(
        "CREATE POLICY tenant_isolation ON audit_event "
        "USING (tenant_id = NULLIF(current_setting('app.tenant_id', true), '')::uuid) "
        "WITH CHECK (tenant_id = NULLIF(current_setting('app.tenant_id', true), '')::uuid)"
    ),
    sa.text("ALTER TABLE provider_event ENABLE ROW LEVEL SECURITY"),
    sa.text("ALTER TABLE provider_event FORCE ROW LEVEL SECURITY"),
    sa.text(
        "CREATE POLICY tenant_isolation ON provider_event "
        "USING (tenant_id = NULLIF(current_setting('app.tenant_id', true), '')::uuid) "
        "WITH CHECK (tenant_id = NULLIF(current_setting('app.tenant_id', true), '')::uuid)"
    ),
    sa.text("ALTER TABLE human_review_task ENABLE ROW LEVEL SECURITY"),
    sa.text("ALTER TABLE human_review_task FORCE ROW LEVEL SECURITY"),
    sa.text(
        "CREATE POLICY tenant_isolation ON human_review_task "
        "USING (tenant_id = NULLIF(current_setting('app.tenant_id', true), '')::uuid) "
        "WITH CHECK (tenant_id = NULLIF(current_setting('app.tenant_id', true), '')::uuid)"
    ),
    sa.text("ALTER TABLE human_review_approval ENABLE ROW LEVEL SECURITY"),
    sa.text("ALTER TABLE human_review_approval FORCE ROW LEVEL SECURITY"),
    sa.text(
        "CREATE POLICY tenant_isolation ON human_review_approval "
        "USING (tenant_id = NULLIF(current_setting('app.tenant_id', true), '')::uuid) "
        "WITH CHECK (tenant_id = NULLIF(current_setting('app.tenant_id', true), '')::uuid)"
    ),
    sa.text("ALTER TABLE outcome_label ENABLE ROW LEVEL SECURITY"),
    sa.text("ALTER TABLE outcome_label FORCE ROW LEVEL SECURITY"),
    sa.text(
        "CREATE POLICY tenant_isolation ON outcome_label "
        "USING (tenant_id = NULLIF(current_setting('app.tenant_id', true), '')::uuid) "
        "WITH CHECK (tenant_id = NULLIF(current_setting('app.tenant_id', true), '')::uuid)"
    ),
)

DOWNGRADE_STATEMENTS = (
    sa.text("DROP POLICY IF EXISTS tenant_isolation ON outcome_label"),
    sa.text("ALTER TABLE outcome_label NO FORCE ROW LEVEL SECURITY"),
    sa.text("ALTER TABLE outcome_label DISABLE ROW LEVEL SECURITY"),
    sa.text("DROP POLICY IF EXISTS tenant_isolation ON human_review_approval"),
    sa.text("ALTER TABLE human_review_approval NO FORCE ROW LEVEL SECURITY"),
    sa.text("ALTER TABLE human_review_approval DISABLE ROW LEVEL SECURITY"),
    sa.text("DROP POLICY IF EXISTS tenant_isolation ON human_review_task"),
    sa.text("ALTER TABLE human_review_task NO FORCE ROW LEVEL SECURITY"),
    sa.text("ALTER TABLE human_review_task DISABLE ROW LEVEL SECURITY"),
    sa.text("DROP POLICY IF EXISTS tenant_isolation ON provider_event"),
    sa.text("ALTER TABLE provider_event NO FORCE ROW LEVEL SECURITY"),
    sa.text("ALTER TABLE provider_event DISABLE ROW LEVEL SECURITY"),
    sa.text("DROP POLICY IF EXISTS tenant_isolation ON audit_event"),
    sa.text("ALTER TABLE audit_event NO FORCE ROW LEVEL SECURITY"),
    sa.text("ALTER TABLE audit_event DISABLE ROW LEVEL SECURITY"),
    sa.text("DROP POLICY IF EXISTS tenant_isolation ON message"),
    sa.text("ALTER TABLE message NO FORCE ROW LEVEL SECURITY"),
    sa.text("ALTER TABLE message DISABLE ROW LEVEL SECURITY"),
    sa.text("DROP POLICY IF EXISTS tenant_isolation ON conversation"),
    sa.text("ALTER TABLE conversation NO FORCE ROW LEVEL SECURITY"),
    sa.text("ALTER TABLE conversation DISABLE ROW LEVEL SECURITY"),
    sa.text("DROP POLICY IF EXISTS tenant_isolation ON lead"),
    sa.text("ALTER TABLE lead NO FORCE ROW LEVEL SECURITY"),
    sa.text("ALTER TABLE lead DISABLE ROW LEVEL SECURITY"),
)


def upgrade() -> None:
    for statement in UPGRADE_STATEMENTS:
        op.execute(statement)


def downgrade() -> None:
    for statement in DOWNGRADE_STATEMENTS:
        op.execute(statement)
