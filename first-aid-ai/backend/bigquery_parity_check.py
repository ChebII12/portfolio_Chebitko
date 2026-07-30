#!/usr/bin/env python
"""
Phase 4: BigQuery Parity Check Script
Validate data consistency between legacy DB and BigQuery.

Usage:
  python bigquery_parity_check.py --project-id YOUR_PROJECT_ID --dataset-id first_aid_ai_module1 --credentials credentials.json
"""

import argparse
import logging
from datetime import datetime
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from google.cloud import bigquery
import sys

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class ParityChecker:
    """Check data parity between legacy DB and BigQuery."""
    
    def __init__(self, db_session, bq_client, project_id: str, dataset_id: str):
        self.db_session = db_session
        self.bq_client = bq_client
        self.project_id = project_id
        self.dataset_id = dataset_id
        self.results = {}
    
    def check_row_count_parity(self) -> bool:
        """Check total row counts match."""
        from app.db.models import User, QuestionnaireAssessmentWide
        
        logger.info("Checking row count parity...")
        
        # Legacy DB counts
        legacy_users_count = self.db_session.query(User).count()
        legacy_assessments_count = self.db_session.query(QuestionnaireAssessmentWide).count()
        
        # BigQuery counts
        bq_users_query = f"SELECT COUNT(*) as count FROM `{self.project_id}.{self.dataset_id}.user_profiles`"
        bq_assessments_query = f"SELECT COUNT(*) as count FROM `{self.project_id}.{self.dataset_id}.questionnaire_assessments_wide`"
        
        bq_users_result = list(self.bq_client.query(bq_users_query).result())
        bq_assessments_result = list(self.bq_client.query(bq_assessments_query).result())
        
        bq_users_count = bq_users_result[0]['count'] if bq_users_result else 0
        bq_assessments_count = bq_assessments_result[0]['count'] if bq_assessments_result else 0
        
        # Compare
        users_match = legacy_users_count == bq_users_count
        assessments_match = legacy_assessments_count == bq_assessments_count
        
        self.results['row_count'] = {
            'users': {
                'legacy': legacy_users_count,
                'bigquery': bq_users_count,
                'match': users_match
            },
            'assessments': {
                'legacy': legacy_assessments_count,
                'bigquery': bq_assessments_count,
                'match': assessments_match
            }
        }
        
        logger.info(f"  Users: {legacy_users_count} (legacy) vs {bq_users_count} (BQ) - {'✓' if users_match else '✗'}")
        logger.info(f"  Assessments: {legacy_assessments_count} (legacy) vs {bq_assessments_count} (BQ) - {'✓' if assessments_match else '✗'}")
        
        return users_match and assessments_match
    
    def check_level_distribution(self) -> bool:
        """Check level distribution matches."""
        logger.info("Checking level distribution...")
        
        # Legacy DB distribution
        from app.db.models import QuestionnaireAssessmentWide
        legacy_levels = self.db_session.query(
            QuestionnaireAssessmentWide.level,
            func.count(QuestionnaireAssessmentWide.id).label('count')
        ).group_by(QuestionnaireAssessmentWide.level).all()
        
        legacy_dist = {level: count for level, count in legacy_levels}
        
        # BigQuery distribution
        bq_query = f"""
        SELECT level, COUNT(*) as count 
        FROM `{self.project_id}.{self.dataset_id}.questionnaire_assessments_wide`
        GROUP BY level
        """
        
        bq_result = list(self.bq_client.query(bq_query).result())
        bq_dist = {row['level']: row['count'] for row in bq_result}
        
        # Compare distributions
        all_levels = set(legacy_dist.keys()) | set(bq_dist.keys())
        match = True
        
        for level in sorted(all_levels):
            legacy_count = legacy_dist.get(level, 0)
            bq_count = bq_dist.get(level, 0)
            level_match = legacy_count == bq_count
            match = match and level_match
            logger.info(f"  {level}: {legacy_count} (legacy) vs {bq_count} (BQ) - {'✓' if level_match else '✗'}")
        
        self.results['level_distribution'] = {
            'legacy': legacy_dist,
            'bigquery': bq_dist,
            'match': match
        }
        
        return match
    
    def check_classification_source_distribution(self) -> bool:
        """Check classification source distribution matches."""
        logger.info("Checking classification source distribution...")
        
        # Legacy DB distribution
        from app.db.models import QuestionnaireAssessmentWide
        from sqlalchemy import func
        
        legacy_sources = self.db_session.query(
            QuestionnaireAssessmentWide.classification_source,
            func.count(QuestionnaireAssessmentWide.id).label('count')
        ).group_by(QuestionnaireAssessmentWide.classification_source).all()
        
        legacy_dist = {source: count for source, count in legacy_sources}
        
        # BigQuery distribution
        bq_query = f"""
        SELECT classification_source, COUNT(*) as count 
        FROM `{self.project_id}.{self.dataset_id}.questionnaire_assessments_wide`
        GROUP BY classification_source
        """
        
        bq_result = list(self.bq_client.query(bq_query).result())
        bq_dist = {row['classification_source']: row['count'] for row in bq_result}
        
        # Compare
        all_sources = set(legacy_dist.keys()) | set(bq_dist.keys())
        match = True
        
        for source in sorted(all_sources):
            legacy_count = legacy_dist.get(source, 0)
            bq_count = bq_dist.get(source, 0)
            source_match = legacy_count == bq_count
            match = match and source_match
            logger.info(f"  {source}: {legacy_count} (legacy) vs {bq_count} (BQ) - {'✓' if source_match else '✗'}")
        
        self.results['classification_source_distribution'] = {
            'legacy': legacy_dist,
            'bigquery': bq_dist,
            'match': match
        }
        
        return match
    
    def check_null_constraints(self) -> bool:
        """Check for null values in required fields."""
        logger.info("Checking null constraints...")
        
        required_fields = {
            'user_profiles': ['user_id', 'name', 'email', 'password_hash'],
            'questionnaire_assessments_wide': ['assessment_id', 'user_id', 'level', 'confidence', 'classification_source']
        }
        
        match = True
        
        for table, fields in required_fields.items():
            for field in fields:
                query = f"SELECT COUNT(*) as count FROM `{self.project_id}.{self.dataset_id}.{table}` WHERE {field} IS NULL"
                result = list(self.bq_client.query(query).result())
                null_count = result[0]['count'] if result else 0
                field_match = null_count == 0
                match = match and field_match
                logger.info(f"  {table}.{field}: {null_count} nulls - {'✓' if field_match else '✗'}")
        
        self.results['null_constraints'] = {'match': match}
        
        return match
    
    def run_all_checks(self) -> bool:
        """Run all parity checks."""
        logger.info("\n" + "="*60)
        logger.info("BIGQUERY PARITY CHECK")
        logger.info("="*60 + "\n")
        
        results = [
            ("Row Count Parity", self.check_row_count_parity()),
            ("Level Distribution", self.check_level_distribution()),
            ("Classification Source Distribution", self.check_classification_source_distribution()),
            ("Null Constraints", self.check_null_constraints()),
        ]
        
        logger.info("\n" + "="*60)
        logger.info("PARITY CHECK RESULTS")
        logger.info("="*60)
        
        all_passed = True
        for check_name, passed in results:
            status = "✓ PASS" if passed else "✗ FAIL"
            logger.info(f"{check_name}: {status}")
            all_passed = all_passed and passed
        
        logger.info("="*60)
        
        if all_passed:
            logger.info("\n✓ ALL PARITY CHECKS PASSED - Ready for cutover")
        else:
            logger.warning("\n✗ PARITY CHECKS FAILED - Do not proceed with cutover")
        
        return all_passed


def run_parity_check(database_url: str, project_id: str, dataset_id: str, 
                     credentials_path: str = None):
    """Run parity check."""
    from app.db.models import Base
    
    # Initialize database connection
    engine = create_engine(database_url)
    Session = sessionmaker(bind=engine)
    db_session = Session()
    
    # Initialize BigQuery client
    from google.oauth2 import service_account
    if credentials_path:
        credentials = service_account.Credentials.from_service_account_file(credentials_path)
        bq_client = bigquery.Client(project=project_id, credentials=credentials)
    else:
        bq_client = bigquery.Client(project=project_id)
    
    try:
        checker = ParityChecker(db_session, bq_client, project_id, dataset_id)
        return checker.run_all_checks()
    finally:
        db_session.close()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="BigQuery Parity Check Script")
    parser.add_argument("--database-url", default="sqlite:///./firstaidai.db",
                       help="Source database URL (default: local SQLite)")
    parser.add_argument("--project-id", required=True, help="GCP Project ID")
    parser.add_argument("--dataset-id", default="first_aid_ai_module1", help="BigQuery Dataset ID")
    parser.add_argument("--credentials", help="Path to Google Cloud credentials JSON file")
    
    args = parser.parse_args()
    
    try:
        success = run_parity_check(
            database_url=args.database_url,
            project_id=args.project_id,
            dataset_id=args.dataset_id,
            credentials_path=args.credentials
        )
        sys.exit(0 if success else 1)
    except Exception as e:
        logger.error(f"Parity check failed: {e}", exc_info=True)
        sys.exit(1)
