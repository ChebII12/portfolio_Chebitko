"""Legacy database compatibility shim.

The application now uses BigQuery as its primary persistence layer.
This module remains only so older imports do not fail during the transition.
It intentionally does not import SQLAlchemy, because Module 1 should not
require a legacy database package to start or run BigQuery checks.
"""

Base = object


def get_db():
    """Yield a placeholder None value for compatibility."""
    yield None
