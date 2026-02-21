import os
import datetime
import subprocess
from pathlib import Path
from dotenv import load_dotenv

# Load config
load_dotenv()

DB_NAME = os.getenv('DB_NAME')
DB_USER = os.getenv('DB_USER')
DB_PASSWORD = os.getenv('DB_PASSWORD')
DB_HOST = os.getenv('DB_HOST', 'localhost')
DB_PORT = os.getenv('DB_PORT', '5432')

# Setup Backup Directory
BACKUP_DIR = Path('backups')
BACKUP_DIR.mkdir(exist_ok=True)

# Generate Filename
timestamp = datetime.datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
backup_file = BACKUP_DIR / f"{DB_NAME}_backup_{timestamp}.sql"

print(f"Starting backup for {DB_NAME}...")

# Construct pg_dump command
# Note: PGPASSWORD env var is the safest way to pass password to pg_dump
env = os.environ.copy()
env['PGPASSWORD'] = DB_PASSWORD

command = [
    'pg_dump',
    '-h', DB_HOST,
    '-p', DB_PORT,
    '-U', DB_USER,
    '-F', 'c', # Custom format (compressed)
    '-b',      # Include blobs
    '-v',      # Verbose
    '-f', str(backup_file),
    DB_NAME
]

try:
    subprocess.run(command, env=env, check=True)
    print(f"Backup successful: {backup_file}")
    
    # Cleanup old backups (older than 30 days)
    # TODO: Implement if needed.
    
except subprocess.CalledProcessError as e:
    print(f"Backup FAILED: {e}")
except FileNotFoundError:
    print("Error: 'pg_dump' not found. Make sure PostgreSQL bin directory is in your PATH.")

print("Done.")
