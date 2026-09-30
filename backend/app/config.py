import os

AUTH_MODE = os.getenv("AUTH_MODE", "LOCAL")  # "LOCAL" | "DBX"

# Comma-separated extra origins allowed to call the API (e.g. https://<user>.github.io)
CORS_ORIGINS = [o.strip() for o in os.getenv("CORS_ORIGINS", "").split(",") if o.strip()]
