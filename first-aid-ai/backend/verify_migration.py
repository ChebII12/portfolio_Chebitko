#!/usr/bin/env python3
"""
BigQuery-Only Migration Verification Script
Validates that the migration from SQLite+BigQuery to BigQuery-only is complete.
"""

import subprocess
import sys
import os

def print_header(text):
    print(f"\n{'='*60}")
    print(f"  {text}")
    print(f"{'='*60}")

def print_success(text):
    print(f"✓ {text}")

def print_warning(text):
    print(f"⚠ {text}")

def print_error(text):
    print(f"✗ {text}")

def run_command(cmd, description, allow_fail=False):
    """Run a shell command and report results."""
    try:
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=10)
        if result.returncode == 0:
            print_success(description)
            return True
        else:
            if allow_fail:
                print_warning(description)
                return False
            print_error(description)
            if result.stderr:
                print(f"  Error: {result.stderr[:200]}")
            return False
    except subprocess.TimeoutExpired:
        print_error(f"{description} (timeout)")
        return False
    except Exception as e:
        print_error(f"{description}: {str(e)}")
        return False

def verify_dependencies():
    """Verify that SQLAlchemy and Alembic are removed."""
    print_header("CHECKING DEPENDENCIES")
    
    # Check requirements.txt
    with open("requirements.txt", "r") as f:
        reqs = f.read()
    
    issues = []
    
    if "sqlalchemy" in reqs.lower():
        issues.append("SQLAlchemy still in requirements.txt")
    else:
        print_success("SQLAlchemy removed from requirements.txt")
    
    if "alembic" in reqs.lower():
        issues.append("Alembic still in requirements.txt")
    else:
        print_success("Alembic removed from requirements.txt")
    
    if "google-cloud-bigquery" in reqs:
        print_success("BigQuery is in requirements.txt")
    else:
        issues.append("BigQuery not found in requirements.txt")
    
    return len(issues) == 0, issues

def verify_configuration():
    """Verify configuration changes."""
    print_header("CHECKING CONFIGURATION")
    
    # Read config file
    try:
        with open("app/core/config.py", "r") as f:
            config = f.read()
    except Exception as e:
        print_error(f"Could not read config.py: {e}")
        return False, ["Cannot read config.py"]
    
    issues = []
    
    # Check for removed fields
    if "database_url" in config:
        issues.append("database_url still in config.py")
    else:
        print_success("database_url removed from config.py")
    
    if "bigquery_write_enabled" in config:
        issues.append("bigquery_write_enabled still in config.py")
    else:
        print_success("bigquery_write_enabled removed from config.py")
    
    if "bigquery_read_source" in config:
        issues.append("bigquery_read_source still in config.py")
    else:
        print_success("bigquery_read_source removed from config.py")
    
    # Check for required BigQuery fields
    if "bigquery_project_id" in config:
        print_success("bigquery_project_id is configured")
    else:
        issues.append("bigquery_project_id not found in config.py")
    
    if "bigquery_dataset_id" in config:
        print_success("bigquery_dataset_id is configured")
    else:
        issues.append("bigquery_dataset_id not found in config.py")
    
    return len(issues) == 0, issues

def verify_bigquery_service():
    """Verify BigQueryService updates."""
    print_header("CHECKING BIGQUERY SERVICE")
    
    try:
        with open("app/core/bigquery_service.py", "r") as f:
            service = f.read()
    except Exception as e:
        print_error(f"Could not read bigquery_service.py: {e}")
        return False, ["Cannot read bigquery_service.py"]
    
    issues = []
    
    # Check removed memory fallbacks
    if "_MEMORY_USERS" in service:
        issues.append("_MEMORY_USERS still present in bigquery_service.py")
    else:
        print_success("_MEMORY_USERS removed from bigquery_service.py")
    
    if "_MEMORY_ASSESSMENTS" in service:
        issues.append("_MEMORY_ASSESSMENTS still present in bigquery_service.py")
    else:
        print_success("_MEMORY_ASSESSMENTS removed from bigquery_service.py")
    
    # Check for required initialization
    if "BIGQUERY_PROJECT_ID is required" in service:
        print_success("BigQuery project ID validation added")
    else:
        issues.append("BigQuery project ID validation not found")
    
    # Check that legacy methods are removed
    if "def read_user_profile" in service:
        issues.append("Legacy read_user_profile method still present")
    else:
        print_success("Legacy read_user_profile method removed")
    
    if "def read_latest_assessment" in service:
        issues.append("Legacy read_latest_assessment method still present")
    else:
        print_success("Legacy read_latest_assessment method removed")
    
    return len(issues) == 0, issues

def verify_imports():
    """Verify no SQLAlchemy imports remain."""
    print_header("CHECKING IMPORTS")
    
    issues = []
    
    # Check for SQLAlchemy imports in Python files
    result = subprocess.run(
        "grep -r \"from sqlalchemy\\|import sqlalchemy\\|from alembic\\|import alembic\" app/ --include=\"*.py\"",
        shell=True,
        capture_output=True,
        text=True
    )
    
    if result.returncode == 0 and result.stdout:
        issues.append(f"SQLAlchemy/Alembic imports found:\n{result.stdout}")
        print_error("SQLAlchemy/Alembic imports still present")
    else:
        print_success("No SQLAlchemy/Alembic imports found")
    
    # Check that BigQuery is imported correctly
    result = subprocess.run(
        "grep -r \"from google.cloud import bigquery\\|from google.oauth2 import service_account\" app/ --include=\"*.py\"",
        shell=True,
        capture_output=True,
        text=True
    )
    
    if result.returncode == 0:
        print_success("BigQuery imports present")
    else:
        issues.append("BigQuery imports not found")
        print_error("BigQuery imports not found")
    
    return len(issues) == 0, issues

def verify_environment():
    """Verify .env.example changes."""
    print_header("CHECKING ENVIRONMENT CONFIGURATION")
    
    try:
        with open(".env.example", "r") as f:
            env_example = f.read()
    except Exception as e:
        print_error(f"Could not read .env.example: {e}")
        return False, ["Cannot read .env.example"]
    
    issues = []
    
    if "DATABASE_URL" in env_example:
        issues.append("DATABASE_URL still in .env.example")
    else:
        print_success("DATABASE_URL removed from .env.example")
    
    if "BIGQUERY_WRITE_ENABLED" in env_example:
        issues.append("BIGQUERY_WRITE_ENABLED still in .env.example")
    else:
        print_success("BIGQUERY_WRITE_ENABLED removed from .env.example")
    
    if "BIGQUERY_PROJECT_ID" in env_example:
        print_success("BIGQUERY_PROJECT_ID in .env.example")
    else:
        issues.append("BIGQUERY_PROJECT_ID not in .env.example")
    
    return len(issues) == 0, issues

def verify_app_startup():
    """Verify main.py changes."""
    print_header("CHECKING APPLICATION STARTUP")
    
    try:
        with open("app/main.py", "r") as f:
            main = f.read()
    except Exception as e:
        print_error(f"Could not read main.py: {e}")
        return False, ["Cannot read main.py"]
    
    issues = []
    
    if "initialize_bigquery" in main:
        print_success("initialize_bigquery event present")
    else:
        issues.append("initialize_bigquery event not found")
    
    # Check that it properly raises errors instead of silently catching
    if "except Exception:" in main and "pass" in main:
        issues.append("Exception silencing found in startup event")
    else:
        print_success("Startup errors are properly raised")
    
    return len(issues) == 0, issues

def main():
    """Run all verification checks."""
    print("\n" + "="*60)
    print("  BIGQUERY-ONLY MIGRATION VERIFICATION")
    print("="*60)
    
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    
    results = {
        "Dependencies": verify_dependencies(),
        "Configuration": verify_configuration(),
        "BigQuery Service": verify_bigquery_service(),
        "Imports": verify_imports(),
        "Environment": verify_environment(),
        "App Startup": verify_app_startup(),
    }
    
    # Print summary
    print_header("VERIFICATION SUMMARY")
    
    all_passed = True
    for check_name, (passed, issues) in results.items():
        if passed:
            print_success(f"{check_name}")
        else:
            print_error(f"{check_name}")
            all_passed = False
            for issue in issues:
                print(f"    - {issue}")
    
    # Final verdict
    print_header("FINAL VERDICT")
    
    if all_passed:
        print_success("Migration to BigQuery-only is complete!")
        print("\nNext steps:")
        print("  1. Set BIGQUERY_PROJECT_ID in .env")
        print("  2. Set BIGQUERY_CREDENTIALS_PATH in .env (if using service account file)")
        print("  3. Run: python -m uvicorn app.main:app --reload")
        print("  4. Test endpoints")
        return 0
    else:
        print_error("Migration verification failed!")
        print("\nPlease review the issues above and fix them.")
        return 1

if __name__ == "__main__":
    sys.exit(main())

