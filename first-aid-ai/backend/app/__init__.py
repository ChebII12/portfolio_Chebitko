"""Application package exports.

The FastAPI app is loaded lazily so utility scripts that import
``app.db.models`` do not pull in web dependencies at import time.
"""


def __getattr__(name):
	if name == "app":
		from .main import app as fastapi_app

		return fastapi_app
	raise AttributeError(f"module 'app' has no attribute {name!r}")


__all__ = ["app"]

__all__ = ["app"]
