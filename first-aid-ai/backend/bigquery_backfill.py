#!/usr/bin/env python
"""
Phase 3: BigQuery Backfill Script
Export historical users and assessments from source DB to BigQuery.

Usage:
  python bigquery_backfill.py --project-id YOUR_PROJECT_ID --dataset-id first_aid_ai_module1 --credentials credentials.json
"""

import argparse
import logging
from datetime import datetime
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import sys
import os

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def backfill_users(db_session, bq_service, limit: int = None):
    """Backfill users from legacy DB to BigQuery."""
    from app.db.models import User
    
    query = db_session.query(User)
    if limit:
        query = query.limit(limit)
    
    users = query.all()
    success_count = 0
    error_count = 0
    
    logger.info(f"Starting backfill of {len(users)} users to BigQuery")
    
    for user in users:
        try:
            bq_service.write_user_profile(
                user_id=str(user.id),
                name=user.name,
                email=user.email,
                password_hash=user.password_hash,
                level=user.level,
                registration_ts=user.registration_date
            )
            success_count += 1
            if success_count % 100 == 0:
                logger.info(f"Backfilled {success_count} users...")
        except Exception as e:
            error_count += 1
            logger.error(f"Error backfilling user {user.id}: {e}")
    
    logger.info(f"User backfill complete: {success_count} success, {error_count} errors")
    return success_count, error_count


def backfill_assessments(db_session, bq_service, limit: int = None):
    """Backfill assessments from legacy DB to BigQuery."""
    from app.db.models import QuestionnaireAssessmentWide
    
    query = db_session.query(QuestionnaireAssessmentWide)
    if limit:
        query = query.limit(limit)
    
    assessments = query.all()
    success_count = 0
    error_count = 0
    
    logger.info(f"Starting backfill of {len(assessments)} assessments to BigQuery")
    
    for assessment in assessments:
        try:
            bq_service.write_assessment(
                assessment_id=assessment.assessment_id,
                user_id=str(assessment.user_id),
                answers={
                    "q1_travel_frequency": assessment.q1_travel_frequency,
                    "q2_distance_from_medical": assessment.q2_distance_from_medical,
                    "q3_certification_status": assessment.q3_certification_status,
                    "q4_real_life_experience": assessment.q4_real_life_experience,
                    "q5_trauma_supplies_comfort": assessment.q5_trauma_supplies_comfort,
                    "q6_group_role": assessment.q6_group_role,
                },
                level=assessment.level,
                confidence=assessment.confidence,
                classification_source=assessment.classification_source,
                created_ts=assessment.created_ts
            )
            success_count += 1
            if success_count % 100 == 0:
                logger.info(f"Backfilled {success_count} assessments...")
        except Exception as e:
            error_count += 1
            logger.error(f"Error backfilling assessment {assessment.assessment_id}: {e}")
    
    logger.info(f"Assessment backfill complete: {success_count} success, {error_count} errors")
    return success_count, error_count


def run_backfill(database_url: str, project_id: str, dataset_id: str, 
                 credentials_path: str = None, limit: int = None):
    """Run backfill process."""
    from app.core.config import settings as app_settings
    from app.core.bigquery_service import BigQueryService
    from app.db.models import Base
    
    # Initialize database connection
    engine = create_engine(database_url)
    Session = sessionmaker(bind=engine)
    db_session = Session()
    
    # Initialize BigQuery service
    bq_service = BigQueryService()
    bq_service.enabled = True
    bq_service.project_id = project_id
    bq_service.dataset_id = dataset_id
    if credentials_path:
        bq_service.bigquery_credentials_path = credentials_path
    bq_service._initialize_client()
    
    # Create dataset and tables
    logger.info("Creating BigQuery dataset and tables...")
    bq_service.create_dataset_and_tables()
    
    # Run backfill
    try:
        user_success, user_errors = backfill_users(db_session, bq_service, limit)
        assessment_success, assessment_errors = backfill_assessments(db_session, bq_service, limit)
        
        logger.info("\n" + "="*60)
        logger.info("BACKFILL SUMMARY")
        logger.info("="*60)
        logger.info(f"Users:       {user_success} success, {user_errors} errors")
        logger.info(f"Assessments: {assessment_success} success, {assessment_errors} errors")
        logger.info(f"Total:       {user_success + assessment_success} success, {user_errors + assessment_errors} errors")
        logger.info("="*60 + "\n")
        
        return user_errors + assessment_errors == 0
    finally:
        db_session.close()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="BigQuery Backfill Script")
    parser.add_argument("--database-url", default="sqlite:///./firstaidai.db", 
                       help="Source database URL (default: local SQLite)")
    parser.add_argument("--project-id", required=True, help="GCP Project ID")
    parser.add_argument("--dataset-id", default="first_aid_ai_module1", help="BigQuery Dataset ID")
    parser.add_argument("--credentials", help="Path to Google Cloud credentials JSON file")
    parser.add_argument("--limit", type=int, help="Limit number of records to backfill (for testing)")
    
    args = parser.parse_args()
    
    try:
        success = run_backfill(
            database_url=args.database_url,
            project_id=args.project_id,
            dataset_id=args.dataset_id,
            credentials_path=args.credentials,
            limit=args.limit
        )
        sys.exit(0 if success else 1)
    except Exception as e:
        logger.error(f"Backfill failed: {e}", exc_info=True)
        sys.exit(1)
