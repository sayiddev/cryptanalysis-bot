import os
import tempfile
from pathlib import Path

_TEST_DB_PATH = Path(tempfile.gettempdir()) / "cryptanalysis_bot_test.db"
_TEST_DB_PATH.unlink(missing_ok=True)

os.environ.setdefault("BOT_TOKEN", "000000:TEST-TOKEN-NOT-REAL")
os.environ.setdefault("WEBHOOK_SECRET_TOKEN", "test-secret-token")
os.environ.setdefault("WEBHOOK_BASE_URL", "https://example.test")
os.environ.setdefault("ADMIN_USER_IDS", "111,222")
os.environ.setdefault("DATABASE_URL", f"sqlite+aiosqlite:///{_TEST_DB_PATH.as_posix()}")
