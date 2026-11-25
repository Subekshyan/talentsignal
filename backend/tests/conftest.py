import os

# Must be set before app.db is imported.
os.environ["DATABASE_URL"] = "sqlite+pysqlite:///:memory:"
