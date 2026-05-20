"""Add review task, approval, and outcome label tables."""

from __future__ import annotations

import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

from alembic import op

revision = "0002_review_outcome_repositories"
down_revision = "0001_initial_schema"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "human_review_task",
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
        sa.Column("conversation_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("handoff_reason", sa.String(length=120), nullable=False),
        sa.Column("status", sa.String(length=32), nullable=False),
        sa.Column("payload", postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.ForeignKeyConstraint(
            ["conversation_id"],
            ["conversation.id"],
            name="fk_human_review_task_conversation_id_conversation",
            ondelete="CASCADE",
        ),
        sa.ForeignKeyConstraint(
            ["tenant_id"],
            ["tenant.id"],
            name="fk_human_review_task_tenant_id_tenant",
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("id", name="pk_human_review_task"),
    )
    op.create_index(
        "ix_human_review_task_conversation_id",
        "human_review_task",
        ["conversation_id"],
    )
    op.create_index("ix_human_review_task_tenant_id", "human_review_task", ["tenant_id"])
    op.create_index(
        "ix_human_review_task_tenant_created",
        "human_review_task",
        ["tenant_id", "created_at"],
    )
    op.create_index(
        "ix_human_review_task_tenant_status",
        "human_review_task",
        ["tenant_id", "status"],
    )

    op.create_table(
        "human_review_approval",
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
        sa.Column("review_task_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("actor_id", sa.String(length=120), nullable=False),
        sa.Column("approved_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("original_draft_hash", sa.String(length=64), nullable=False),
        sa.Column("final_message_hash", sa.String(length=64), nullable=False),
        sa.Column("reason_code", sa.String(length=120), nullable=False),
        sa.Column("send_status", sa.String(length=32), nullable=False),
        sa.ForeignKeyConstraint(
            ["review_task_id"],
            ["human_review_task.id"],
            name="fk_human_review_approval_review_task_id_human_review_task",
            ondelete="CASCADE",
        ),
        sa.ForeignKeyConstraint(
            ["tenant_id"],
            ["tenant.id"],
            name="fk_human_review_approval_tenant_id_tenant",
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("id", name="pk_human_review_approval"),
    )
    op.create_index(
        "ix_human_review_approval_review_task_id",
        "human_review_approval",
        ["review_task_id"],
    )
    op.create_index(
        "ix_human_review_approval_tenant_id",
        "human_review_approval",
        ["tenant_id"],
    )

    op.create_table(
        "outcome_label",
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
        sa.Column("lead_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("label", sa.String(length=64), nullable=False),
        sa.Column("labeled_on", sa.Date(), nullable=False),
        sa.ForeignKeyConstraint(
            ["lead_id"], ["lead.id"], name="fk_outcome_label_lead_id_lead", ondelete="CASCADE"
        ),
        sa.ForeignKeyConstraint(
            ["tenant_id"],
            ["tenant.id"],
            name="fk_outcome_label_tenant_id_tenant",
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("id", name="pk_outcome_label"),
    )
    op.create_index("ix_outcome_label_lead_id", "outcome_label", ["lead_id"])
    op.create_index("ix_outcome_label_tenant_id", "outcome_label", ["tenant_id"])
    op.create_index(
        "ix_outcome_label_tenant_labeled_on",
        "outcome_label",
        ["tenant_id", "labeled_on"],
    )


def downgrade() -> None:
    op.drop_index("ix_outcome_label_tenant_labeled_on", table_name="outcome_label")
    op.drop_index("ix_outcome_label_tenant_id", table_name="outcome_label")
    op.drop_index("ix_outcome_label_lead_id", table_name="outcome_label")
    op.drop_table("outcome_label")
    op.drop_index("ix_human_review_approval_tenant_id", table_name="human_review_approval")
    op.drop_index(
        "ix_human_review_approval_review_task_id",
        table_name="human_review_approval",
    )
    op.drop_table("human_review_approval")
    op.drop_index("ix_human_review_task_tenant_status", table_name="human_review_task")
    op.drop_index("ix_human_review_task_tenant_created", table_name="human_review_task")
    op.drop_index("ix_human_review_task_tenant_id", table_name="human_review_task")
    op.drop_index("ix_human_review_task_conversation_id", table_name="human_review_task")
    op.drop_table("human_review_task")
