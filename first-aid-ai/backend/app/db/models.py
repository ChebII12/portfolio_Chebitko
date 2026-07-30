"""Database models - keeping for reference purposes only.

With BigQuery as the primary persistence layer, these SQLAlchemy models
are no longer used for persistence. The BigQueryService handles all data
operations directly.

For reference of the data structures:
- User: Represents user profiles
- QuestionnaireAssessmentWide: Represents questionnaire assessments
"""

# User table structure reference:
# - user_id (STRING, PRIMARY KEY)
# - name (STRING)
# - email (STRING)
# - password_hash (STRING)
# - level (STRING: beginner/intermediate/expert)
# - registration_ts (TIMESTAMP)
# - updated_ts (TIMESTAMP)
# - questionnaire_data (STRING JSON payload of the latest questionnaire)

# QuestionnaireAssessmentWide table structure reference:
# - assessment_id (STRING, PRIMARY KEY)
# - user_id (STRING, FOREIGN KEY)
# - q1_travel_frequency (STRING)
# - q2_distance_from_medical (STRING)
# - q3_certification_status (STRING)
# - q4_real_life_experience (STRING)
# - q5_trauma_supplies_comfort (STRING)
# - q6_group_role (STRING)
# - level (STRING)
# - confidence (FLOAT64)
# - classification_source (STRING)
# - created_ts (TIMESTAMP)
