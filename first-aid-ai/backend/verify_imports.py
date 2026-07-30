#!/usr/bin/env python3
"""Quick verification that app loads correctly."""

import sys
try:
    from app.main import app
    print("✓ App imports successfully")
    
    from app.core.bigquery_service import BigQueryService
    print("✓ BigQueryService imports successfully")
    
    service = BigQueryService()
    client_status = "BigQuery" if service.client else "In-memory (fallback)"
    print(f"✓ BigQueryService initialized ({client_status})")
    
    print("\n✓ All imports and initializations successful!")
    sys.exit(0)
    
except Exception as e:
    print(f"✗ Import failed: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

