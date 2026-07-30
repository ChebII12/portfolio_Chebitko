"""Create questionnaire_assessments_wide table

Revision ID: 8f4b7c2a9d11
Revises: 0c6d7f633abc
Create Date: 2026-04-24 14:30:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "8f4b7c2a9d11"
down_revision: Union[str, None] = "0c6d7f633abc"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "questionnaire_assessments_wide",
        sa.Column("assessment_id", sa.String(), nullable=False),
        sa.Column("user_id", sa.String(), nullable=False),
        sa.Column("q1_travel_frequency", sa.String(), nullable=False),
        sa.Column("q2_distance_from_medical", sa.String(), nullable=False),
        sa.Column("q3_certification_status", sa.String(), nullable=False),
        sa.Column("q4_real_life_experience", sa.String(), nullable=False),
        sa.Column("q5_trauma_supplies_comfort", sa.String(), nullable=False),
        sa.Column("q6_group_role", sa.String(), nullable=False),
        sa.Column("level", sa.String(), nullable=False),
        sa.Column("confidence", sa.Float(), nullable=False),
        sa.Column("classification_source", sa.String(), nullable=False),
        sa.Column("created_ts", sa.TIMESTAMP(), nullable=False),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"]),
        sa.PrimaryKeyConstraint("assessment_id"),
    )
    op.create_index(
        "ix_questionnaire_assessments_wide_user_id",
        "questionnaire_assessments_wide",
        ["user_id"],
        unique=False,
    )


def downgrade() -> None:
    op.drop_index("ix_questionnaire_assessments_wide_user_id", table_name="questionnaire_assessments_wide")
    op.drop_table("questionnaire_assessments_wide")
