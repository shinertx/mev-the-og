import os
import shutil
import hashlib
import datetime
import subprocess

SNAP_DIR = "snapshots"
LOG_FILE = os.path.join(SNAP_DIR, "snapshot.log")

def ensure_dirs():
    os.makedirs(SNAP_DIR, exist_ok=True)


def get_commit_hash():
    try:
        return subprocess.check_output(["git", "rev-parse", "HEAD"]).decode().strip()
    except Exception:
        return "unknown"


def health_check():
    # Simple health check placeholder
    try:
        subprocess.check_call(["python", "-m", "py_compile", "main.py"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        return "healthy"
    except Exception:
        return "unhealthy"


def create_snapshot():
    ensure_dirs()
    ts = datetime.datetime.utcnow().strftime("%Y%m%d_%H%M%S")
    folder = os.path.join(SNAP_DIR, ts)
    os.makedirs(folder, exist_ok=True)

    commit = get_commit_hash()
    with open(os.path.join(folder, "commit.txt"), "w") as f:
        f.write(commit + "\n")

    if os.path.exists("config.yaml"):
        shutil.copy("config.yaml", os.path.join(folder, "config.yaml"))

    env_hash = "missing"
    if os.path.exists(".env"):
        with open(".env", "rb") as f:
            env_hash = hashlib.sha256(f.read()).hexdigest()
    with open(os.path.join(folder, "env_hash.txt"), "w") as f:
        f.write(env_hash + "\n")

    if os.path.isdir("logs"):
        shutil.make_archive(os.path.join(folder, "logs"), "zip", "logs")

    health = health_check()
    with open(os.path.join(folder, "health.txt"), "w") as f:
        f.write(health + "\n")

    with open(LOG_FILE, "a") as log:
        log.write(f"{ts} SNAPSHOT {folder}\n")
    print(f"Snapshot created at {folder}")


if __name__ == "__main__":
    create_snapshot()
